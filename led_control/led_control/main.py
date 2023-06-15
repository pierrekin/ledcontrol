import collections
import struct
import colorsys
import serial
import json
from cobs import cobs
from datetime import datetime


WLED_DEVICE = "/dev/tty.usbserial-0001"
WLED_BAUDRATE = 921600

AHRS_DEVICE = "/dev/tty.usbserial-16"
AHRS_BAUDRATE = 921600

LED_COUNT = 120
BRIGHTNESS = 1.0

FLOAT_SIZE = 4
DELIMETER_BYTE = b"\x00"

ATTITUDE_SIZE = 3
IMU_SAMPLE_SIZE = 9
TIMING_SIZE = 2


PACKET_START = b"\xC9"
PACKET_TYPE_DATA_FRAME = b"\xDA"
PACKET_END = b"\x36"

CONVERSION = 2**8 - 1


def build_packet(leds):
    data = b"".join([channel.to_bytes(1, "big") for led in leds for channel in led])
    size_bytes = len(data).to_bytes(2, "big")
    return PACKET_START + PACKET_TYPE_DATA_FRAME + size_bytes + data + PACKET_END


def flush_leds(leds, wled_interface, brightness=1):
    rgb_data = [colorsys.hsv_to_rgb(h, s, v) for (h, s, v) in leds]
    rgb_data_int = [
        (int(r * CONVERSION), int(g * CONVERSION), int(b * CONVERSION))
        for (r, g, b) in rgb_data
    ]
    data = build_packet(rgb_data_int)
    wled_interface.write(data)


def read_ahrs(imu_interface):
    while True:
        stuffed_data = imu_interface.read_until(DELIMETER_BYTE)[0:-1]
        if len(stuffed_data) == 58:
            break

    data = cobs.decode(stuffed_data)[1:]
    report = [
        struct.unpack("f", data[(i * FLOAT_SIZE) : (i * FLOAT_SIZE + FLOAT_SIZE)])[0]
        for i in range(len(data) // FLOAT_SIZE)
    ]
    parts = []
    index = 0
    parts.append(report[index:ATTITUDE_SIZE])
    index += ATTITUDE_SIZE
    parts.append(report[index : index + IMU_SAMPLE_SIZE])
    index += IMU_SAMPLE_SIZE
    parts.append(report[index : index + TIMING_SIZE])
    return parts


def scale(x, input_min, input_max, output_min=0, output_max=1):
    a = output_min
    b = (x - input_min) / (input_max - input_min)
    c = output_max - output_min

    return output_min + b * c


def clamp(x, lower=0, upper=1):
    return min(max(x, lower), upper)


def main():
    ahrs_interface = serial.Serial(AHRS_DEVICE, baudrate=AHRS_BAUDRATE)
    wled_interface = serial.Serial(WLED_DEVICE, baudrate=WLED_BAUDRATE)

    # print(wled_interface.readline(), end="")
    # wled_interface.write("v".encode("ascii"))
    # print(wled_interface.readline(), end="")
    # wled_interface.write(json.dumps({"live": True}).encode("ascii"))

    counter = 0
    start_time = datetime.now()

    while True:
        counter += 1

        if counter > 100:
            now = datetime.now()
            rate = 1000000 * (counter / (now - start_time).microseconds)
            print(f"{rate:0.2f} Hz")

            counter = 0
            start_time = now

        attitude, imu_sample, timing = read_ahrs(ahrs_interface)

        scaled_attitude = [scale(c, -90, 90) for c in attitude]
        clamped_attitude = [clamp(c) for c in scaled_attitude]

        colours = [(i / float(LED_COUNT), 1, 1) for i in range(LED_COUNT)]

        position = int(clamped_attitude[0] * LED_COUNT)

        if counter % 25 == 0:
            flush_leds(
                [colours[(i + position) % 120] for i in range(LED_COUNT)][0:80],
                wled_interface,
                brightness=BRIGHTNESS,
            )


if __name__ == "__main__":
    main()
