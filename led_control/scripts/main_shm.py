import socket
import colorsys
import serial
import sacn
import time
import collections
import ahrs


SERIAL_DEVICE = "/dev/tty.usbserial-0001"
SERIAL_BAUDRATE = 115200
WLED_HOSTNAME = "wled.local"
SACN_MULTICAST = False
LED_COUNT = 120
BRIGHTNESS = 0.01


def flush_leds(leds, sender, brightness=1):
    rgb_data = [colorsys.hsv_to_rgb(h, s, v) for (h, s, v) in leds]
    rgb_data_int = [
        (int(r * 255), int(g * 255), int(b * 255)) for (r, g, b) in rgb_data
    ]
    sender.dmx_data = [
        int(channel * brightness) for led in rgb_data_int for channel in led
    ]


def read_imu(imu_interface):
    line = imu_interface.readline().decode("ascii")
    ax, ay, az, gx, gy, gz, t = line.split(",")
    return (float(ax), float(ay), float(az)), (float(gx), float(gy), float(gz)), t


def scale(x, input_min, input_max, output_min=0, output_max=1):
    a = output_min
    b = (x - input_min) / (input_max - input_min)
    c = output_max - output_min

    return output_min + b * c


def clamp(x, lower=0, upper=1):
    return min(max(x, lower), upper)


class Osc:
    def __init__(self, spring, timedelta, strength, drag=0):
        self.position = 0
        self.spring = spring
        self.timedelta = timedelta
        self.velocity = 0
        self.strength = strength
        self.drag = drag

    def tick(self, influence):
        force = -self.position * self.spring + influence * self.strength
        self.velocity = (
            self.velocity
            + force * self.timedelta
            + (self.drag * (1 if self.velocity < 0 else -1))
        )
        self.position = self.position + self.velocity * self.timedelta

    def interpolate(self, lower=0, upper=1):
        return clamp(scale(self.position, -1, 1, lower, upper), lower, upper)


def main():
    imu_interface = serial.Serial(SERIAL_DEVICE, baudrate=SERIAL_BAUDRATE)
    imu_interface.readline()

    sacn_sender = sacn.sACNsender()

    sacn_sender.start()
    sacn_sender.activate_output(1)

    sacn_sender[1].multicast = SACN_MULTICAST

    wled_host = socket.gethostbyname(WLED_HOSTNAME)
    sacn_sender[1].destination = wled_host

    position_osc = Osc(spring=10, timedelta=0.035, strength=10, drag=0.02)
    hue_osc = Osc(spring=10, timedelta=0.05, strength=5)
    saturation_osc = Osc(spring=10, timedelta=0.05, strength=5)
    value_osc = Osc(spring=10, timedelta=0.05, strength=5)

    while True:
        accel, gyro, t = read_imu(imu_interface)
        # attitude = ahrs.filters.FAMC([0, 0, 0], [0, 0, 0])
        # print(attitude.Q)

        scaled_accel = [scale(x, -1.5, 1.5) for x in accel]
        clamped_accel = [clamp(x) for x in scaled_accel]

        position_osc.tick(clamped_accel[0])
        hue_osc.tick(clamped_accel[1])
        saturation_osc.tick(clamped_accel[1])
        value_osc.tick(clamped_accel[2])

        position = int(position_osc.interpolate(0, LED_COUNT) - 50)
        # position = scale(attitude.Q.as_euler_angles[0], 0, 255)

        bottom_leds = [
            (
                0.4,
                1.0,
                1.0,
            )
            for i in range(position)
        ]
        top_leds = [(0.8, 1.0, 1.0) for i in range(LED_COUNT - position)]
        flush_leds(bottom_leds + top_leds, sacn_sender[1], brightness=BRIGHTNESS)


if __name__ == "__main__":
    main()
