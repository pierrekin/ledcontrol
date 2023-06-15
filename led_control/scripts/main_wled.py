import json
import socket
import colorsys
import serial
import sacn
import time
import collections
from datetime import datetime


SERIAL_DEVICE = "/dev/tty.usbserial-0001"
SERIAL_BAUDRATE = 115200
LED_COUNT = 120
BRIGHTNESS = 1.0
MIDDLE_LEDS_COUNT = 3


def flush_leds(leds, wled_interface, brightness=1):
    rgb_data = [colorsys.hsv_to_rgb(h, s, v) for (h, s, v) in leds]
    rgb_data_int = [
        (int(r * 255 * brightness), int(g * 255 * brightness), int(b * 255 * brightness)) for (r, g, b) in rgb_data
    ]
    data = {"seg": {"i": rgb_data_int}}
    message = (json.dumps(data) + '\n').encode('ascii')
    wled_interface.write(message)


def read_ahrs(imu_interface):
    line = imu_interface.readline().decode("ascii")
    return [float(component) for component in line.split(",")]


def scale(x, input_min, input_max, output_min=0, output_max=1):
    a = output_min
    b = (x - input_min) / (input_max - input_min)
    c = output_max - output_min

    return output_min + b * c


def clamp(x, lower=0, upper=1):
    return min(max(x, lower), upper)


def main():
    wled_interface = serial.Serial(SERIAL_DEVICE, baudrate=SERIAL_BAUDRATE)

    position = 60
    bottom_colour = (0.4, 1.0, 1.0)
    middle_colour = (0.6, 1.0, 1.0)
    top_colour = (0.1, 1.0, 1.0)

    bottom_leds = [bottom_colour for i in range(position)]
    middle_leds = [middle_colour for i in range(MIDDLE_LEDS_COUNT)]
    top_leds = [top_colour for i in range(120 - position - MIDDLE_LEDS_COUNT)]

    flush_leds(
        bottom_leds + middle_leds + top_leds, wled_interface, brightness=BRIGHTNESS
    )

    time.sleep(5)


if __name__ == "__main__":
    main()
