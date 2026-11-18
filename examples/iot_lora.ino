#include <Arduino.h>
#include "../c_core/ouroboros.h"

void setup() {
    Serial.begin(115200);
    while (!Serial) { delay(10); }

    Serial.println("=== OUROBOROS IoT / LoRa Telemetry Demo ===");

    // Simulated sensor payload (Temp: 24, Humidity: 65, Battery: 98, Status: 1)
    uint8_t sensor_payload[4] = { 24, 65, 98, 1 };
    char radio_packet[17]; // 4 bytes * 4 chars + null terminator

    // 1. Zero-allocation hardware-speed encoding
    size_t encoded_len = ouro_encode_buffer(sensor_payload, 4, radio_packet);
    radio_packet[encoded_len] = '\0';

    Serial.print("Transmitting over noisy LoRa RF: ");
    Serial.println(radio_packet);

    // 2. Simulate RF interference (corrupting a filler vowel in block 2)
    radio_packet[4] = (radio_packet[4] == 'a') ? 'o' : 'a';
    Serial.print("Received with RF noise        : ");
    Serial.println(radio_packet);

    // 3. Self-healing 3-vs-1 majority decode
    uint8_t decoded_payload[4];
    size_t repaired = 0;
    size_t decoded_len = ouro_decode_buffer(radio_packet, encoded_len, decoded_payload, &repaired);

    if (decoded_len == 4) {
        Serial.print("Decoded successfully! Blocks auto-repaired: ");
        Serial.println(repaired);
        Serial.print("Restored values: ");
        for (int i = 0; i < 4; i++) {
            Serial.print(decoded_payload[i]);
            Serial.print(" ");
        }
        Serial.println();
    } else {
        Serial.println("Critical packet loss.");
    }
}

void loop() {
    delay(5000);
}
