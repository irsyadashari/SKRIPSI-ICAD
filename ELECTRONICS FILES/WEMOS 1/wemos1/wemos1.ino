#include <OneWire.h>
#include <DallasTemperature.h>
#include <ESP8266WiFi.h> // Enables the ESP8266 to connect to the local network (via WiFi)
#include <PubSubClient.h> // Allows us to connect to, and publish to the MQTT broker

#define trigPin D2
#define echoPin D3
#define tempPin D8

// WiFi
// Make sure to update this for your own WiFi network!
const char* ssid = "TIDAK ADA";
const char* wifi_password = "sopkonropanastidakgratis";

// MQTT
// Make sure to update this for your own MQTT Broker!
const char* mqttServer = "192.168.1.15";
const int mqttPort = 1883;
const char* mqttTopicTemp = "temperatures";
const char* mqttTopicDistance = "distance";
const char* mqttUsername = "icad";
const char* mqttPassword = "ashari";
// The client id identifies the ESP8266 device. Think of it a bit like a hostname (Or just a name, like Greg).
const char* clientID = "WeMosD1R1";

// Initialise the WiFi and MQTT Client objects
WiFiClient espClient;
PubSubClient client(espClient);

// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(tempPin);

// Pass our oneWire reference to Dallas Temperature sensor 
DallasTemperature tempSensors(&oneWire);

// Define variables :
long duration;
int distance;
long temperatures;

void setup() {
  
   // Define inputs and outputs
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  
  // Begin Serial on 115200
  // Remember to choose the correct Baudrate on the Serial monitor!
  // This is just for debugging purposes
  Serial.begin(115200);

  Serial.print("Connecting to ");
  Serial.println(ssid);

  // Connect to the WiFi
  WiFi.begin(ssid, wifi_password);

  // Wait until the connection has been confirmed before continuing
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi...");
  }

  // Debugging - Output the IP Address of the ESP8266
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);

   while (!client.connected()) {
    Serial.println("Connecting to MQTT...");

    if (client.connect("ESP8266Client", mqttUsername, mqttPassword )) {
      Serial.println("connected");
    } else {
      Serial.print("failed with state ");
      Serial.print(client.state());
      delay(2000);
    }
  }
   // Start up the library
  tempSensors.begin();
}

void loop() {
     getTemperaturesAndDistances();
//   client.publish("esp8266", "Hello Raspberry Pi");
//   client.subscribe("esp8266");
     client.publish("temperatures", String(temperatures).c_str());
     client.subscribe("temperatures");
//   client.publish("distance",distance);
//   client.subscribe("esp8266");
     delay(500);
     client.loop();
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived in topic: ");
  Serial.println(topic);
  Serial.print("Temperatures :");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
  Serial.print("Distance = ");
  Serial.println(distance);
  Serial.println("-------------------------");
}

void getTemperaturesAndDistances(){
  // Call sensors.requestTemperatures() to issue a global temperature and Requests to all devices on the bus
  tempSensors.requestTemperatures(); 
  
  // Clear the trigPin by setting it LOW:
  digitalWrite(trigPin, LOW);
  
  delayMicroseconds(5);
 // Trigger the sensor by setting the trigPin high for 100 microseconds:
  digitalWrite(trigPin, HIGH);
  delay(500);
  digitalWrite(trigPin, LOW);
  
  // Read the echoPin. pulseIn() returns the duration (length of the pulse) in microseconds:
  duration = pulseIn(echoPin, HIGH);
  
  // Calculate the distance:
  distance = duration*0.034/2;
  
//  Print the distance on the Serial Monitor (Ctrl+Shift+M):
//  Serial.print("Distance = ");
//  Serial.print(distance);
//  Serial.println(" cm");
//  Serial.print("Celsius temperature: ");
//  Why "byIndex"? You can have more than one IC on the same bus. 0 refers to the first IC on the wire //TODO: LEARN ABOUT THIS
//  Serial.println(tempSensors.getTempCByIndex(0)); 
  temperatures = tempSensors.getTempCByIndex(0);
  delay(100);
}
