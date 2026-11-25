"""Collect actual Wokwi ESP32-origin benchmark receipts, using existing BENCH nodes.
No sensor messages are published by Python. Clock probes only are answered over MQTT.
MQTT-clock-calibrated one-way latency is an estimate; start/end clock bounds diagnose offsets.
"""
import argparse
import csv
import json
import re
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import paho.mqtt.client as mqtt

BASE = 'scobywatch/panji/benchclock/'
PATTERN = re.compile(r'^SWB-ESP-([0-9a-f]{8})-(\d+)-(\d{13})$')

def now(): return time.time_ns() // 1_000_000

def metrics(values):
    vals = sorted(values)
    if not vals: return {'n': 0}
    def q(p):
        k=(len(vals)-1)*p; i=int(k); j=min(i+1,len(vals)-1)
        return round(vals[i]+(vals[j]-vals[i])*(k-i),3)
    return {'n':len(vals),'negative_count':sum(x<0 for x in vals), **{f'p{p}_ms':q(p/100) for p in (50,95,99)}}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--messages',type=int,default=100)
    ap.add_argument('--timeout',type=int,default=600)
    ap.add_argument('--drain',type=int,default=20)
    ap.add_argument('--output',type=Path,default=Path('revisions/PAPER023634-R1/results/esp32_dashboard_benchmark'))
    a=ap.parse_args()
    if min(a.messages,a.timeout,a.drain)<1: ap.error('positive settings required')
    lock=threading.Lock(); ready=threading.Event(); records={}; clock={}; finish={}; state={'run':None,'done_at':None}
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def do_POST(self):
            try:
                n=int(self.headers.get('Content-Length',0))
                if self.path!='/event' or not 0<n<8192: raise ValueError('bad event')
                d=json.loads(self.rfile.read(n)); m=PATTERN.fullmatch(d['batch_id']); stage=d['stage']; ts=int(d['ts_ms'])
                if stage not in ('ingress','dashboard'): raise ValueError('bad stage')
                if m:
                    rid,seq,sent=m.groups();seq=int(seq);sent=int(sent)
                    with lock:
                        if rid==state['run'] and 1<=seq<=a.messages:
                            r=records.setdefault(seq,{'sequence':seq,'batch_id':d['batch_id'],'esp_sent_ms':sent,'ingress_ms':None,'dashboard_ms':None,'ingress_count':0,'dashboard_count':0})
                            if r['batch_id']==d['batch_id']:
                                r[stage+'_count']+=1
                                if r[stage+'_ms'] is None:r[stage+'_ms']=ts
                self.send_response(204); self.end_headers()
            except (ValueError,KeyError,TypeError,OverflowError):self.send_response(400); self.end_headers()
    server=ThreadingHTTPServer(('127.0.0.1',8765),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    c=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,protocol=mqtt.MQTTv311)
    def on_connect(c,u,f,reason,props):
        if reason==0:c.subscribe([(BASE+'probe',0),(BASE+'report',0),(BASE+'finish',0)])
    def on_subscribe(c,u,mid,reasons,props):
        if all(not x.is_failure for x in reasons):ready.set()
    def on_message(c,u,msg):
        t1=now()
        try:
            v=msg.payload.decode('ascii').split(',');rid=v[0]
            if not re.fullmatch(r'[0-9a-f]{8}',rid):return
            if msg.topic==BASE+'probe' and len(v)==3:
                phase=v[1];t0=int(v[2]);
                if phase not in ('start','end'):return
                with lock:
                    if state['run'] is None and phase=='start':state['run']=rid; print('ESP32 run:',rid,flush=True)
                    if state['run']!=rid:return
                t2=now();c.publish(BASE+'reply/'+rid,f'{phase},{t0},{t1},{t2}',qos=0,retain=False)
            elif msg.topic==BASE+'report' and len(v)==6:
                phase=v[1];t0,t1r,t2,t3=map(int,v[2:]);lo=t2-t3;hi=t1r-t0
                with lock:
                    if rid!=state['run'] or phase not in ('start','end'):return
                    clock[phase]={'esp_send_ms':t0,'host_receive_ms':t1r,'host_send_ms':t2,'esp_receive_ms':t3,'offset_lower_ms':lo,'offset_upper_ms':hi,'offset_interval_width_ms':hi-lo,'zero_within_bounds':lo<=0<=hi}
                print('Clock',phase,'host minus ESP bounds:',lo,hi,'ms',flush=True)
            elif msg.topic==BASE+'finish' and len(v)==4:
                with lock:
                    if rid!=state['run']:return
                    finish.update(attempted=int(v[1]),local_publish_ok=int(v[2]),clock_end_ok=bool(int(v[3])))
                    state['done_at']=time.monotonic()
                print('ESP32 finished:',finish,'collecting late receipts...',flush=True)
        except (ValueError,UnicodeError,IndexError):return
    c.on_connect=on_connect;c.on_subscribe=on_subscribe;c.on_message=on_message
    started=datetime.now(timezone.utc).isoformat()
    try:
        c.connect('broker.emqx.io',1883,60);c.loop_start()
        if not ready.wait(20):raise RuntimeError('MQTT subscriptions not ready')
        print('READY. Start the instrumented Wokwi sketch now. Keep dashboard and Wokwi visible.',flush=True)
        deadline=time.monotonic()+a.timeout;last=-1
        while time.monotonic()<deadline:
            with lock:
                n=sum(r['dashboard_ms'] is not None for r in records.values());done=state['done_at']
            if n!=last and (n%10==0 or n==a.messages):print(f'Dashboard receipts: {n}/{a.messages}',flush=True);last=n
            if done is not None and time.monotonic()-done>=a.drain:break
            time.sleep(.25)
    finally:
        c.disconnect();c.loop_stop();server.shutdown();server.server_close()
    rows=[]
    for seq in range(1,a.messages+1):
        r=records.get(seq,{'sequence':seq,'batch_id':None,'esp_sent_ms':None,'ingress_ms':None,'dashboard_ms':None,'ingress_count':0,'dashboard_count':0})
        sent=r['esp_sent_ms']; ing=r['ingress_ms'];ui=r['dashboard_ms']
        r['esp_to_ingress_estimate_ms']=None if ing is None or sent is None else ing-sent
        r['esp_to_dashboard_estimate_ms']=None if ui is None or sent is None else ui-sent
        r['ingress_to_dashboard_ms']=None if ing is None or ui is None else ui-ing
        rows.append(r)
    ni=sum(r['ingress_ms'] is not None for r in rows);nd=sum(r['dashboard_ms'] is not None for r in rows)
    ok=finish.get('local_publish_ok'); bounds_ok=all(k in clock and clock[k]['zero_within_bounds'] for k in ('start','end'))
    latency={k:metrics([r[k] for r in rows if r[k] is not None]) for k in ('esp_to_ingress_estimate_ms','esp_to_dashboard_estimate_ms','ingress_to_dashboard_ms')}
    summary={'started_utc':started,'run_id':state['run'],'publisher':'Wokwi simulated ESP32, host epoch estimated via MQTT clock exchange','expected_messages':a.messages,'firmware_finish':finish,'node_red_ingress':ni,'dashboard_receipts':nd,'ingress_missing_pct_of_expected':round(100*(a.messages-ni)/a.messages,4),'dashboard_missing_pct_of_expected':round(100*(a.messages-nd)/a.messages,4),'ingress_missing_pct_of_local_publish_ok':round(100*(ok-ni)/ok,4) if ok and ni<=ok else None,'dashboard_missing_pct_of_local_publish_ok':round(100*(ok-nd)/ok,4) if ok and nd<=ok else None,'clock_offset_checks':clock,'zero_offset_plausible_at_start_and_end':bounds_ok,'latency':latency,'drain_seconds_after_finish':a.drain,'measurement':'ESP32 estimated host-epoch timestamp immediately before payload serialization/publish to Node-RED parsed ingress or instrumented browser widget receipt; not whole dashboard rendering. One-way estimates include residual clock offset and simulation-clock drift. Clock probes bound offset only at probe times under nonnegative transit assumptions; not a calibration of every sample. Missing receipts are within observation window.'}
    a.output.mkdir(parents=True,exist_ok=True)
    with (a.output/'esp32_dashboard_raw.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (a.output/'esp32_dashboard_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
    if not bounds_ok or not finish or finish.get('attempted')!=a.messages or any(x.get('negative_count',0) for x in latency.values()):print('WARNING: check clock alignment / incomplete run before reporting one-way latency.')
if __name__=='__main__':main()
