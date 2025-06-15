#define DOWN 5
#define RIGHT 6
#define LEFT 7
#define UP 8
#define MINUS 9
#define PLUS 14
#define B 15
#define Y 16
#define A 17
#define X 18

void setup() {
  Serial.begin(115200);
  pinMode(DOWN, OUTPUT);
  pinMode(RIGHT, OUTPUT);
  pinMode(LEFT, OUTPUT);
  pinMode(UP, OUTPUT);
  pinMode(MINUS, OUTPUT);
  pinMode(PLUS, OUTPUT);
  pinMode(B, OUTPUT);
  pinMode(Y, OUTPUT);
  pinMode(A, OUTPUT);
  pinMode(X, OUTPUT);
}

uint8_t toPress = 0;

void handle(uint8_t received) {
  if (received == 'z') {
    // Press the next two at the same time
    toPress = 999;
    return;
  }

  if (toPress == 999) {
    toPress = received;
    return;
  }

  if (toPress != 0) {
    digitalWrite(toPress, HIGH);
    digitalWrite(received, HIGH);
    delay(50);
    digitalWrite(toPress, LOW);
    if (received < 9) {
      delay(30);
    }
    digitalWrite(received, LOW);
    toPress = 0;
    return;
  }

  digitalWrite(received, HIGH);
  delay(50);
  if (received < 9) {
      delay(30);
  }
  digitalWrite(received, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    uint8_t received = Serial.read();
    handle(received);
  }
}
