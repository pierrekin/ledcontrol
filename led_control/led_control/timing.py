import time
from datetime import datetime, timedelta


DEFAULT_PERIOD = timedelta(seconds=1)


class FrequencyCounter:
    def __init__(self, period=DEFAULT_PERIOD):
        self.last_reset = datetime.now()
        self.count = 0
        self.ratelimiter = Ratelimiter(period=period)

    def tick(self):
        self.count += 1

    def sample(self):
        now = datetime.now()
        frequency = self.count / (now - self.last_reset).total_seconds()
        self.count = 0
        self.last_reset = now
        self.ratelimiter.tick()
        return frequency

    def ready(self):
        return self.ratelimiter.ready()


class Ratelimiter:
    def __init__(self, period=None, frequency=None):
        self.last_event = datetime.now()
        assert period is not None or frequency is not None
        self.period = period if period is not None else timedelta(seconds=1 / frequency)

    def tick(self):
        self.last_event = datetime.now()

    def ready(self):
        since_last_event = datetime.now() - self.last_event
        return self.period < since_last_event

    def wait(self):
        since_last_event = datetime.now() - self.last_event
        to_sleep = self.period - since_last_event

        if to_sleep.total_seconds() > 0:
            time.sleep(to_sleep.total_seconds())
