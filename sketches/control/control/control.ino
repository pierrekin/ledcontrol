#include <FastLED.h>

#include "TPM2.h"

#define DATA_PIN 14
#define NO_OF_LEDS 120

uint8_t buffer[NO_OF_LEDS * 3];
CRGB leds[NO_OF_LEDS];
TPM2 tpm2Driver(&Serial, buffer, sizeof(buffer));

uint8_t counter = 1;

void CallbackRx(uint8_t *data, uint16_t len)
{
    uint16_t i, led;

    for (i = 0, led = 0; i < len; i += 3, led++)
    {
        leds[led] = CRGB(data[i], data[i + 1], data[i + 2]);
    }
    FastLED.show();
}

void setup()
{
    Serial.begin(115200);
    tpm2Driver.registerRxData(CallbackRx);

    FastLED.addLeds<WS2812, DATA_PIN, GRB>(leds, NO_OF_LEDS);
    // Initialize all pixels to 'off'
    for (int i = 0; i < NO_OF_LEDS; i++)
    {
        leds[i] = CRGB(0, 0, 5);
    }
    FastLED.show();
}

void loop()
{
    tpm2Driver.update();
}
