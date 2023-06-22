from led_control import ahrs
from led_control import wled
from led_control import timing
from datetime import datetime


WLED_DEVICE = "/dev/cu.usbmodem7111101"
AHRS_DEVICE = "/dev/cu.usbserial-0001"

LED_COUNT = 120
BRIGHTNESS = 0.1
SENSITIVITY = 2


def scale(x, input_min, input_max, output_min=0, output_max=1):
    a = output_min
    b = (x - input_min) / (input_max - input_min)
    c = output_max - output_min

    return output_min + b * c


def clamp(x, lower=0, upper=1):
    return min(max(x, lower), upper)


def main():
    ahrs_interface = ahrs.SerialAHRS(AHRS_DEVICE)
    wled_interface = wled.SerialWLED(WLED_DEVICE)

    while True:
        attitude_sample, imu_sample, timing_sample = ahrs_interface.read()

        scaled_roll = scale(attitude_sample.roll, -90, 90, 0, LED_COUNT * SENSITIVITY)

        # colours = [(i / (float(LED_COUNT)), 1, 1) for i in range(LED_COUNT)]
        # leds = [colours[int(i + scaled_roll) % 120] for i in range(LED_COUNT)]

        leds = [(1, 1, 1) for i in range(LED_COUNT)]
        leds[int(scaled_roll % 120)] = (0.4, 1, 1)
        leds[int((scaled_roll - 1) % 120)] = (0.55, 1, 1)
        leds[int((scaled_roll + 1) % 120)] = (0.55, 1, 1)

        wled_interface.flush_hsv(leds, brightness=BRIGHTNESS)

        if ahrs_interface.counter.ready():
            print(f"AHRS: {ahrs_interface.counter.sample()} Hz")

        if wled_interface.counter.ready():
            print(f"WLED: {wled_interface.counter.sample()} Hz")


if __name__ == "__main__":
    main()
