"""Controlled MQTT replay benchmark against SCOBY Watch's existing Node-RED flow.
Requires paho-mqtt==2.1.0. The publisher, Node-RED and dashboard browser must
run on the same PC. This is not ESP32/Wokwi-origin latency. The UI receipt is
an instrumented dashboard widget callback, not a measurement of every gauge paint.
"""
import argparse, csv, json, platform, secrets, threading, time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import paho.mqtt.client as mqtt

ROOT = Path(__file__).resolve().parents[3]
TOPIC = 'scobywatch/panji/sensor'

def now_ms(): return time.time_ns()/1e6

def percentiles(values):
    vals = sorted(values)
    def q(p):
        k = (len(vals)-1)*p; i=int(k); j=min(i+1,len(vals)-1)
        return round(vals[i]+(vals[j]-vals[i])*(k-i),3)
    return {f'p{p}_ms':q(p/100) for p in (50,95,99)} if vals else {}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--messages',type=int,default=100)
    ap.add_argument('--interval',type=float,default=0.5)
    ap.add_argument('--drain',type=float,default=15)
    ap.add_argument('--broker',default='broker.emqx.io')
    ap.add_argument('--topic',default=TOPIC)
    ap.add_argument('--port',type=int,default=1883)
    ap.add_argument('--output',type=Path,default=ROOT/'revisions/PAPER023634-R1/results/mqtt_dashboard_benchmark')
    a=ap.parse_args()
    if a.messages<1 or a.interval<0.1 or a.drain<1: ap.error('Invalid messages, interval or drain')
    run='SWB-'+secrets.token_hex(6)+'-'; rows={}; lock=threading.Lock(); connected=threading.Event()
    class Collector(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def do_POST(self):
            try:
                length=int(self.headers.get('Content-Length',0))
                if self.path!='/event' or not 0<length<8192: raise ValueError('invalid request')
                event=json.loads(self.rfile.read(length)); bid=event['batch_id']; stage=event['stage']; ts=float(event['ts_ms'])
                if stage not in ('ingress','dashboard') or not isinstance(bid,str): raise ValueError('invalid event')
                with lock:
                    row=rows.get(bid)
                    if row is not None:
                        row[stage+'_count']+=1
                        key=stage+'_ms'
                        if row[key] is None: row[key]=ts
                self.send_response(204);self.end_headers()
            except (ValueError,KeyError,TypeError):
                self.send_response(400);self.end_headers()
    server=ThreadingHTTPServer(('127.0.0.1',8765),Collector)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id=run+'publisher',protocol=mqtt.MQTTv311)
    def on_connect(c,u,f,reason,props):
        if reason==0: connected.set()
    client.on_connect=on_connect
    started=datetime.now(timezone.utc).isoformat()
    try:
        client.connect(a.broker,a.port,60); client.loop_start()
        if not connected.wait(15): raise RuntimeError('MQTT connection not confirmed')
        print('Connected. Keep dashboard visible. Run:',run,flush=True)
        start=time.monotonic()
        for seq in range(1,a.messages+1):
            target=start+(seq-1)*a.interval
            time.sleep(max(0,target-time.monotonic()))
            bid=run+str(seq)
            payload=dict(batch_id=bid,recipe_id='R1',tea_type='black_tea',sugar_g_per_l=80,starter_ml=150,water_volume_l=1.0,day=7,room_temp_c=24.4,humidity_percent=68.0,ph=3.56,brix=7.71)
            wire=json.dumps(payload,separators=(',',':'))
            with lock: rows[bid]={'batch_id':bid,'sequence':seq,'sent_ms':now_ms(),'publish_ok':False,'ingress_ms':None,'dashboard_ms':None,'ingress_count':0,'dashboard_count':0}
            info=client.publish(a.topic,wire,qos=0,retain=False)
            try:
                info.wait_for_publish(timeout=5); ok=info.rc==mqtt.MQTT_ERR_SUCCESS and info.is_published()
            except (RuntimeError,ValueError): ok=False
            with lock: rows[bid]['publish_ok']=ok
            if seq%20==0 or seq==a.messages: print(f'Attempted {seq}/{a.messages}',flush=True)
        print('Collecting late events for',a.drain,'seconds',flush=True);time.sleep(a.drain)
    finally:
        client.disconnect();client.loop_stop();server.shutdown();server.server_close()
    records=list(rows.values())
    for r in records:
        for stage in ('ingress','dashboard'):
            t=r[stage+'_ms']; r[stage+'_latency_ms']=None if t is None else round(t-r['sent_ms'],3)
        r['node_red_to_dashboard_ms']=None if r['ingress_ms'] is None or r['dashboard_ms'] is None else round(r['dashboard_ms']-r['ingress_ms'],3)
    sent=[r for r in records if r['publish_ok']];received=[r for r in sent if r['ingress_ms'] is not None];ui=[r for r in sent if r['dashboard_ms'] is not None];
    def latency(field,subset):
        values=[r[field] for r in subset if r[field] is not None]
        return dict(n=len(values),negative_count=sum(v<0 for v in values),**percentiles([v for v in values if v>=0]))
    def loss(n,d):return round(100*(d-n)/d,4) if d else None
    summary=dict(run_id=run,started_utc=started,broker=a.broker,port=a.port,topic=a.topic,qos=0,attempted=len(records),locally_published=len(sent),local_publish_failures=len(records)-len(sent),unique_node_red_ingress=len(received),unique_dashboard_receipts=len(ui),mqtt_ingress_missing_pct=loss(len(received),len(sent)),dashboard_missing_pct=loss(len(ui),len(sent)),ingress_duplicates=sum(max(0,r['ingress_count']-1) for r in sent),dashboard_duplicates=sum(max(0,r['dashboard_count']-1) for r in sent),interval_s=a.interval,offered_rate_messages_per_s=1/a.interval,drain_s=a.drain,python=platform.python_version(),platform=platform.platform(),publisher='Python replay on same PC, not Wokwi ESP32',measurement='Host wall-clock publisher to parsed MQTT ingress and browser instrumented widget receipt; not all widget rendering',ingress_latency=latency('ingress_latency_ms',received),dashboard_latency=latency('dashboard_latency_ms',ui),node_red_to_dashboard_latency=latency('node_red_to_dashboard_ms',ui))
    if len(ui)>1:
        stamps=sorted(r['dashboard_ms'] for r in ui)
        summary['observed_dashboard_completion_rate_messages_per_s']=round((len(stamps)-1)/((stamps[-1]-stamps[0])/1000),4) if stamps[-1]>stamps[0] else None
    a.output.mkdir(parents=True,exist_ok=True)
    with (a.output/'mqtt_dashboard_raw.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    (a.output/'mqtt_dashboard_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
    if not received or not ui: print('WARNING: missing instrumentation receipts; investigate before interpreting loss/latency.')
if __name__=='__main__':main()
