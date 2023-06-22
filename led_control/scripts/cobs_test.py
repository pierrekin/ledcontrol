import time
from led_control import wled


SERIAL_DEVICE = "/dev/cu.usbserial-0001"
WLED_BAUD = 115200 * 8


counter = 0


def tick(interface):
    global counter
    counter += 1
    leds = [(0, 0, 0) for i in range(120)]
    leds[counter % 120] = (1, 1, 1)
    interface.flush_rgb(leds)


def main():
    interface = wled.SerialWLED(SERIAL_DEVICE, baudrate=WLED_BAUD)

    while True:
        tick(interface)
        time.sleep(0.02)


if __name__ == "__main__":
    main()
