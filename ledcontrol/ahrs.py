import struct
from collections import namedtuple
import serial
from cobs import cobs
from led_control import timing


DEFAULT_BAUDRATE = 921600

FLOAT_SIZE = 4
DELIMETER_BYTE = b"\x00"

ATTITUDE_SIZE = 3
IMU_SAMPLE_SIZE = 9
TIMING_SIZE = 2


AttitudeSample = namedtuple("AttitudeSample", ["roll", "pitch", "yaw"])
IMUSample = namedtuple(
    "IMUSample", ["gx", "gy", "gz", "ax", "ay", "az", "mx", "my", "mz"]
)
TimingSample = namedtuple("TimingSample", ["fs", "fr"])


def chunker(seq, size):
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))


class SerialAHRS:
    def __init__(self, device=None, baudrate=DEFAULT_BAUDRATE):
        self.interface = serial.Serial(device, baudrate=baudrate)
        self.counter = timing.FrequencyCounter()

    def _read_packet(self):
        field_count = (
            len(AttitudeSample._fields)
            + len(IMUSample._fields)
            + len(TimingSample._fields)
        )
        packet_length = field_count * FLOAT_SIZE

        while True:
            stuffed_packet = self.interface.read_until(DELIMETER_BYTE)

            if len(stuffed_packet) == packet_length + 3:
                break

        packet = cobs.decode(stuffed_packet[0:-1])[1:]

        unpack_float = lambda data: struct.unpack("f", data)[0]
        return [unpack_float(data) for data in chunker(packet, FLOAT_SIZE)]

    def read(self):
        self.counter.tick()
        packet = self._read_packet()
        return (
            AttitudeSample(*packet[0:3]),
            IMUSample(*packet[3:12]),
            TimingSample(*packet[12:14]),
        )
