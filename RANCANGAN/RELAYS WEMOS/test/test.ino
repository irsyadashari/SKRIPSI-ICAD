void setup() {
  // put your setup code here, to run once:
  pinMode(D6,OUTPUT);
  pinMode(D7,OUTPUT);
  pinMode(D5,OUTPUT);
  pinMode(D8,OUTPUT);

  digitalWrite(D5,HIGH);
  digitalWrite(D6,HIGH);
  digitalWrite(D7,HIGH);
  digitalWrite(D8,HIGH);

  
}

void loop() {
  // put your main code here, to run repeatedly:
  delay(3000);
  digitalWrite(D5,LOW);
  delay(3000);
  digitalWrite(D6,LOW);
  delay(3000);
  digitalWrite(D7,LOW);
  delay(3000);
  digitalWrite(D8,LOW);
  delay(3000);

  digitalWrite(D5,HIGH);
  digitalWrite(D6,HIGH);
  digitalWrite(D7,HIGH);
  digitalWrite(D8,HIGH);
}
