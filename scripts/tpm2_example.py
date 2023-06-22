import random
import time
from ledcontrol.tpm2 import SerialTPM2


NUM_LEDS = 120
NUM_COLOURS = 5


def main():
    wled = SerialTPM2(brightness=0.1)

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

        leds[index] = colours[int(colour_index % len(colours))]

        wled.flush_hsv(leds, block=True)

        if wled.counter.ready():
            frequency = wled.counter.sample()
            print(f"{frequency} Hz")


if __name__ == "__main__":
    main()
