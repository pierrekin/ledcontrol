#include <WS2812Serial.h>
#define USE_WS2812SERIAL
#include <FastLED.h>

#include "TPM2.h"

#define NUM_LEDS 120

#define DATA_PIN 1

CRGB leds[NUM_LEDS];

char serialBuffer[NUM_LEDS * 3 + 5];
uint8_t tpm2Buffer[NUM_LEDS * 3];
TPM2 tpm2Driver(tpm2Buffer, sizeof(tpm2Buffer));

void CallbackRx(uint8_t *data, uint16_t len)
{
    uint16_t i, led;

    for (i = 0, led = 0; i < len; i += 3, led++)
    {
        leds[led] = CRGB(data[i], data[i + 1], data[i + 2]);
    }
}

void setup()
{
    Serial.begin(0);

    LEDS.addLeds<WS2812SERIAL, DATA_PIN, RGB>(leds, NUM_LEDS);

    tpm2Driver.registerRxData(CallbackRx);

    // Initialize all pixels
    for (int i = 0; i < NUM_LEDS; i++)
    {
        leds[i] = CRGB(0, 15, 0);
    }
    FastLED.show();
}

void loop()
{
    int n = Serial.readBytes(serialBuffer, sizeof(serialBuffer));
    for (int i = 0; i < n; i++)
    {
        tpm2Driver.update(serialBuffer[i]);
    }
    FastLED.show();
}