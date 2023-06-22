#include "FastLED.h"

#define LED_TYPE WS2812 // What kind of strip are you using? WS2812, APA102. . .
#define LED_DT 14       // Serial data pin for WS2812 or WS2801.
#define COLOR_ORDER GRB // Are they GRB for WS2812 and GBR for APA102
#define NUM_LEDS 120    // Number of LED's.

struct CRGB leds[NUM_LEDS]; // Initialize our LED array.
int myIndex = 0;

void setup()
{
    Serial.begin(115200);
    LEDS.addLeds<LED_TYPE, LED_DT, COLOR_ORDER>(leds, NUM_LEDS); // WS2801 and APA102
}

void loop()
{
    EVERY_N_SECONDS(1)
    {
        Serial.println("Hello Robyn and Jade.");
    }

    EVERY_N_MILLIS(100)
    {
        leds[myIndex % NUM_LEDS] = CRGB(myIndex % 255, 0, 0);
        myIndex++;
    }

    FastLED.show();
}