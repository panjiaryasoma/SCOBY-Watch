#include <WiFi.h>
#include <PubSubClient.h>
#include "DHTesp.h"

// ===============================
// WiFi & MQTT Configuration
// ===============================
const char* ssid = "Wokwi-GUEST";
const char* password = "";

const char* mqtt_server = "broker.emqx.io";
const int mqtt_port = 1883;
const char* mqtt_topic = "scobywatch/panji/sensor";

// ===============================
// Pin Configuration
// ===============================
const int DHT_PIN = 15;
const int PH_PIN = 34;
const int BRIX_PIN = 35;

// ===============================
// SCOBY Watch Static Metadata
// ===============================
String batch_id = "KB-WOKWI-001";
String recipe_id = "R1";
String tea_type = "black_tea";

int sugar_g_per_l = 80;
int starter_ml = 150;
float water_volume_l = 1.0;
int fermentation_day = 7;

// ===============================
// Objects
// ===============================
WiFiClient espClient;
PubSubClient client(espClient);
DHTesp dhtSensor;

// ===============================
// Helper Function
// ===============================
float mapFloat(float x, float in_min, float in_max, float out_min, float out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

// ===============================
// WiFi Setup
// ===============================
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.println("Connecting to WiFi...");

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi connected.");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

// ===============================
// MQTT Reconnect
// ===============================
void reconnect_mqtt() {
  while (!client.connected()) {
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

// ===============================
// Setup
// ===============================
void setup() {
  Serial.begin(115200);

  dhtSensor.setup(DHT_PIN, DHTesp::DHT22);

  setup_wifi();

  client.setServer(mqtt_server, mqtt_port);

  Serial.println("SCOBY Watch sensor simulator started.");
}

// ===============================
// Loop
// ===============================
void loop() {
  if (!client.connected()) {
    reconnect_mqtt();
  }

  client.loop();

  // Read DHT22
  TempAndHumidity data = dhtSensor.getTempAndHumidity();

  float temperature = data.temperature;
  float humidity = data.humidity;

  // Read potentiometers
  int phRaw = analogRead(PH_PIN);
  int brixRaw = analogRead(BRIX_PIN);

  // Convert analog value to simulated pH and Brix
  float ph = mapFloat(phRaw, 0, 4095, 2.4, 5.0);
  float brix = mapFloat(brixRaw, 0, 4095, 1.5, 14.0);

  // Build JSON payload manually
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

  Serial.println("Publishing payload:");
  Serial.println(payload);

  client.publish(mqtt_topic, payload.c_str());

  delay(3000);
}