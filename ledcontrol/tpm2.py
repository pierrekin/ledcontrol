import colorsys

import serial
from cobs import cobs

from ledcontrol import timing

DEFAULT_SERIAL_DEVICE = "/dev/cu.usbmodem7111101"  # Teensy
DEFAULT_FREQUENCY = 280  # Hz

DEFAULT_BAUDRATE = 105200  # Baud

CONVERSION_FACTOR = 255  # Maxmimum colour channel value per TPM2

PACKET_START = b"\xC9"
PACKET_TYPE_DATA_FRAME = b"\xDA"
PACKET_END = b"\x36"


def build_packet(leds):
    data = b"".join([channel.to_bytes(1, "big") for led in leds for channel in led])
    size_bytes = len(data).to_bytes(2, "big")
    return PACKET_START + PACKET_TYPE_DATA_FRAME + size_bytes + data + PACKET_END


class SerialTPM2:
    def __init__(
        self,
        device=DEFAULT_SERIAL_DEVICE,
        baudrate=DEFAULT_BAUDRATE,
        frequency=DEFAULT_FREQUENCY,
        truncate=None,
        brightness=1,
    ):
        self.interface = serial.Serial(device, baudrate=baudrate)

        self.counter = timing.FrequencyCounter()
        self.ratelimiter = (
            timing.Ratelimiter(frequency=frequency) if frequency is not None else None
        )

        self.truncate = truncate
        self.brightness = brightness

    def _flush_packet(self, packet):
        self.interface.write(packet)

    def flush_rgb(self, rgb_leds, brightness=None):
        brightness = brightness if brightness is not None else self.brightness
        truncated_leds = (
            rgb_leds[0 : self.truncate] if self.truncate is not None else rgb_leds
        )
        rgb_leds_int = [
            (
                int(r * CONVERSION_FACTOR * brightness),
                int(g * CONVERSION_FACTOR * brightness),
                int(b * CONVERSION_FACTOR * brightness),
            )
            for (r, g, b) in truncated_leds
        ]
        packet = build_packet(rgb_leds_int)
        self._flush_packet(packet)

    def flush_hsv(self, hsv_leds, brightness=None, block=False):
        if self.ratelimiter and block:
            self.ratelimiter.wait()
        else:
            if self.ratelimiter and not self.ratelimiter.ready():
                return

        if self.ratelimiter:
            self.ratelimiter.tick()
        self.counter.tick()

        rgb_leds = [colorsys.hsv_to_rgb(h, s, v) for (h, s, v) in hsv_leds]
        self.flush_rgb(rgb_leds, brightness)


class COBSSerialWLED(SerialTPM2):
    def flush_packet(self, packet):
        stuffed_packet = cobs.encode(packet)
        self.interface.write(stuffed_packet)
