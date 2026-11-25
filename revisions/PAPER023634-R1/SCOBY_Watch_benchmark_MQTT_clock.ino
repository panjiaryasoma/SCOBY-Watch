#include <WiFi.h>
#include <PubSubClient.h>
#include "DHTesp.h"
#include <esp_system.h>
#include <math.h>
#include <string.h>

// WiFi & MQTT Configuration
const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "broker.emqx.io";
const int mqtt_port = 1883;
const char* mqtt_topic = "scobywatch/panji/sensor";

// Pin Configuration
const int DHT_PIN = 15;
const int PH_PIN = 34;
const int BRIX_PIN = 35;

// SCOBY Watch Static Metadata
String batch_id = "KB-WOKWI-001";
String recipe_id = "R1";
String tea_type = "black_tea";
int sugar_g_per_l = 80;
int starter_ml = 150;
float water_volume_l = 1.0;
int fermentation_day = 7;

// Objects
WiFiClient espClient;
PubSubClient client(espClient);
DHTesp dhtSensor;

// Added benchmark state (no network initialization here)
const char* probe_topic = "scobywatch/panji/benchclock/probe";
const char* report_topic = "scobywatch/panji/benchclock/report";
const char* finish_topic = "scobywatch/panji/benchclock/finish";
const int MESSAGE_COUNT = 100;
String runId, replyTopic, phase;
long long probeSent = 0, offsetLo = 0, offsetHi = 0;
long long epochOffset = 0;
long long replyT1 = 0, replyT2 = 0, replyT3 = 0;
bool gotProbe = false, started = false, finished = false;
int attempted = 0, published = 0;

// Helper Function (original)
float mapFloat(float x, float in_min, float in_max, float out_min, float out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

// WiFi Setup (original connection, bounded wait)
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.println("Connecting to WiFi...");

  WiFi.begin(ssid, password);

  unsigned long wifiStarted = millis();
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    if (millis() - wifiStarted >= 30000UL) {
      Serial.printf("\nWIFI FAILED status=%d. Check Wokwi project/gateway.\n", (int)WiFi.status());
      finished = true;
      return;
    }
  }

  Serial.println();
  Serial.println("WiFi connected.");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

// MQTT Reconnect (original connection, bounded retries)
void reconnect_mqtt() {
  for (int retry = 0; !client.connected() && retry < 4; ++retry) {
    Serial.print("Connecting to MQTT...");
    String clientId = "SCOBYWatch-";
    clientId += String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      Serial.println("connected.");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 2 seconds...");
      delay(2000);
    }
  }
}

// Setup (original ordering; stop safely if WiFi fails)
void setup() {
  Serial.begin(115200);
  dhtSensor.setup(DHT_PIN, DHTesp::DHT22);
  setup_wifi();
  if (finished) return;
  client.setServer(mqtt_server, mqtt_port);
  Serial.println("SCOBY Watch sensor simulator started.");
}

// Added helpers: called only after WiFi and MQTT have connected.
// No NTP or extra network service: calibrate against the existing collector.
// Host epoch = local millis() + offset estimated by an MQTT clock exchange.
long long epochMs() {
  return epochOffset + (long long)millis();
}

void onMessage(char* topic, byte* bytes, unsigned int length) {
  if (String(topic) != replyTopic || length > 180) return;
  char buf[181];
  memcpy(buf, bytes, length);
  buf[length] = '\0';
  char p[16];
  long long t0, t1, t2;
  if (sscanf(buf, "%15[^,],%lld,%lld,%lld", p, &t0, &t1, &t2) != 4) return;
  if (String(p) != phase || t0 != probeSent || t2 < t1) return;
  long long t3 = epochMs();
  if (t3 < t0 || t2 - t3 > t1 - t0) return;
  replyT1 = t1; replyT2 = t2; replyT3 = t3;
  gotProbe = true;
}

bool clockExchange(const char* name) {
  if (!client.connected()) reconnect_mqtt();
  if (!client.connected()) return false;
  if (!client.subscribe(replyTopic.c_str(), 0)) return false;
  phase = name;
  gotProbe = false;
  for (int tries = 0; tries < 3 && !gotProbe; ++tries) {
    probeSent = epochMs();
    char probe[100];
    snprintf(probe, sizeof(probe), "%s,%s,%lld", runId.c_str(), name, probeSent);
    if (!client.publish(probe_topic, probe, false)) continue;
    unsigned long start = millis();
    while (!gotProbe && millis() - start < 5000UL) {
      client.loop();
      delay(10);
    }
  }
  return gotProbe;
}

bool clockProbe(const char* name) {
  if (!clockExchange(name)) return false;
  offsetLo = replyT2 - replyT3;
  offsetHi = replyT1 - probeSent;
  char report[220];
  snprintf(report, sizeof(report), "%s,%s,%lld,%lld,%lld,%lld", runId.c_str(), name,
           probeSent, replyT1, replyT2, replyT3);
  bool ok = client.publish(report_topic, report, false);
  Serial.printf("CLOCK %s host-minus-ESP bounds: [%lld, %lld] ms; report=%s\n",
                name, offsetLo, offsetHi, ok ? "OK" : "FAILED");
  return ok;
}

bool startBenchmark() {
  if (!client.setBufferSize(1024)) {
    Serial.println("MQTT BUFFER FAILED");
    return false;
  }
  char id[9];
  snprintf(id, sizeof(id), "%08lx", (unsigned long)esp_random());
  runId = id;
  replyTopic = "scobywatch/panji/benchclock/reply/" + runId;
  client.setCallback(onMessage);
  Serial.println("Calibrating clock via MQTT collector (no NTP)...");
  // First exchange registers the run in the unchanged Python collector.
  // Its timestamps are local uptime, not UTC; no report is sent for it.
  if (!clockExchange("start")) {
    Serial.println("CLOCK CALIBRATION FAILED: check collector READY.");
    return false;
  }
  epochOffset += ((replyT2 - replyT3) + (replyT1 - probeSent)) / 2;
  if (epochMs() < 1000000000000LL || epochMs() >= 10000000000000LL) {
    Serial.println("CLOCK CALIBRATION INVALID: expected 13-digit epoch milliseconds.");
    return false;
  }
  // A second exchange measures residual offset after calibration.
  if (!clockProbe("start")) {
    Serial.println("CLOCK START FAILED: check collector READY.");
    return false;
  }
  Serial.printf("BENCH START %s; %d messages\n", runId.c_str(), MESSAGE_COUNT);
  return true;
}

void loop() {
  if (finished) {
    if (client.connected()) client.loop();
    delay(100);
    return;
  }
  // Original MQTT connection sequence.
  if (!client.connected()) {
    reconnect_mqtt();
    if (!client.connected()) { Serial.println("MQTT FAILED"); finished = true; return; }
  }
  client.loop();

  // Added benchmark initialization: only after original MQTT connection.
  if (!started) {
    started = startBenchmark();
    if (!started) { finished = true; return; }
  }
  if (attempted >= MESSAGE_COUNT) {
    bool endOK = clockProbe("end");
    char finish[100];
    snprintf(finish, sizeof(finish), "%s,%d,%d,%d", runId.c_str(), attempted, published, endOK ? 1 : 0);
    if (!client.connected()) reconnect_mqtt();
    bool reported = client.connected() && client.publish(finish_topic, finish, false);
    Serial.printf("BENCH DONE %s attempted=%d local_publish_ok=%d clock_end=%s finish_report=%s\n", runId.c_str(), attempted, published, endOK ? "OK" : "FAILED", reported ? "OK" : "FAILED");
    finished = true;
    return;
  }

  // Read DHT22 (original)
  TempAndHumidity data = dhtSensor.getTempAndHumidity();
  float temperature = data.temperature;
  float humidity = data.humidity;

  // Read potentiometers (original)
  int phRaw = analogRead(PH_PIN);
  int brixRaw = analogRead(BRIX_PIN);
  float ph = mapFloat(phRaw, 0, 4095, 2.4, 5.0);
  float brix = mapFloat(brixRaw, 0, 4095, 1.5, 14.0);

  // Added: unique ID with estimated host epoch timestamp, preserved by Flask.
  ++attempted;
  char bid[90];
  snprintf(bid, sizeof(bid), "SWB-ESP-%s-%d-%lld", runId.c_str(), attempted, epochMs());
  batch_id = bid;
  String payload = "{";
  payload += "\"batch_id\":\"" + batch_id + "\",";
  payload += "\"recipe_id\":\"" + recipe_id + "\",";
  payload += "\"tea_type\":\"" + tea_type + "\",";
  payload += "\"sugar_g_per_l\":" + String(sugar_g_per_l) + ",";
  payload += "\"starter_ml\":" + String(starter_ml) + ",";
  payload += "\"water_volume_l\":" + String(water_volume_l, 1) + ",";
  payload += "\"day\":" + String(fermentation_day) + ",";
  payload += "\"room_temp_c\":" + String(temperature, 2) + ",";
  payload += "\"humidity_percent\":" + String(humidity, 2) + ",";
  payload += "\"ph\":" + String(ph, 2) + ",";
  payload += "\"brix\":" + String(brix, 2);
  payload += "}";
  bool ok = isfinite(temperature) && isfinite(humidity) && client.publish(mqtt_topic, payload.c_str());
  if (ok) ++published;
  Serial.printf("%d/%d %s %s\n", attempted, MESSAGE_COUNT, batch_id.c_str(), ok ? "PUBLISH_OK" : "PUBLISH_FAILED");
  // Maintain original interval while allowing MQTT keepalive.
  unsigned long waitStart = millis();
  while (millis() - waitStart < 3000UL) { client.loop(); delay(10); }
}
