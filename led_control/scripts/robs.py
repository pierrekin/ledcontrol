import random
import time
from led_control.wled import SerialWLED


SERIAL_DEVICE = "/dev/cu.usbmodem7111101"
NUM_LEDS = 120
NUM_COLOURS = 5


def main():
    wled = SerialWLED(SERIAL_DEVICE, brightness=0.1)

    index = 0
    direction = 1
    colour_index = 0
    colours = [((1 / NUM_COLOURS) * i, 0.8, 0.5) for i in range(NUM_COLOURS)]
    leds = [colours[-1] for i in range(NUM_LEDS)]

    while True:
        if (index >= NUM_LEDS - 1) or index < 0:
            direction = -direction
            colour_index += 1

        if colour_index >= NUM_COLOURS:
            colour_index = 0

        index += direction

        # colour_index += random.choice([1, 2, 3, 4, 5])

        leds[index] = colours[int(colour_index % len(colours))]
        # leds[index] = random.choice(colours)

        wled.flush_hsv(leds, block=True)

        if wled.counter.ready():
            print(wled.counter.sample())


if __name__ == "__main__":
    main()
