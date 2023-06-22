import struct
import serial
from cobs import cobs
from datetime import datetime

AHRS_DEVICE = "/dev/tty.usbserial-0001"
AHRS_BAUDRATE = 115200

DELIMETER_BYTE = b"\x00"

ATTITUDE_SIZE = 3
IMU_SAMPLE_SIZE = 9
TIMING_SIZE = 2

FLOAT_SIZE = 4


def read_ahrs(imu_interface):
    stuffed_data = imu_interface.read_until(DELIMETER_BYTE)[0:-1]
    print(len(stuffed_data))
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
    return report[0:3], report[3:12], report[12:14]


def main():
    ahrs_interface = serial.Serial(AHRS_DEVICE, baudrate=AHRS_BAUDRATE)
    ahrs_interface.read_until(DELIMETER_BYTE)

    counter = 0
    start_time = datetime.now()

    while True:
        counter += 1

        attitude, imu, timing = read_ahrs(ahrs_interface)

        if counter > 10:
            now = datetime.now()
            rate = 1000000 * (counter / (now - start_time).microseconds)
            print(f"{rate:0.2f} Hz {int(attitude[0]) * '*'}")

            counter = 0
            start_time = now


if __name__ == "__main__":
    main()
