from ledcontrol import ahrs, tpm2
from ledcontrol.math import scale, clamp


LED_COUNT = 120
BRIGHTNESS = 0.01


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
    tpm2_interface = tpm2.SerialTPM2(brightness=BRIGHTNESS)
    imu_interface = ahrs.SerialAHRS()

    position_osc = Osc(spring=10, timedelta=0.035, strength=10, drag=0.02)
    hue_osc = Osc(spring=10, timedelta=0.05, strength=5)
    saturation_osc = Osc(spring=10, timedelta=0.05, strength=5)
    value_osc = Osc(spring=10, timedelta=0.05, strength=5)

    while True:
        attitude, imu, timing = imu_interface.sample()

        scaled_accel = [scale(x, -1.5, 1.5) for x in imu]
        clamped_accel = [clamp(x) for x in scaled_accel]

        position_osc.tick(clamped_accel[0])
        hue_osc.tick(clamped_accel[1])
        saturation_osc.tick(clamped_accel[1])
        value_osc.tick(clamped_accel[2])

        position = int(position_osc.interpolate(0, LED_COUNT) - LED_COUNT / 2)

        bottom_leds = [
            (
                0.4,
                1.0,
                1.0,
            )
            for i in range(position)
        ]
        top_leds = [(0.8, 1.0, 1.0) for i in range(LED_COUNT - position)]
        tpm2_interface.flush_hsv(bottom_leds + top_leds)


if __name__ == "__main__":
    main()
