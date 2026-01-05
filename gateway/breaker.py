import time
from dataclasses import dataclass
from typing import Callable


class BreakerCircuitOpenException(Exception):
    pass


@dataclass
class Breaker:
    """Breaker class - prevents requests to external services from being made if the service is unreliable."""

    callback: Callable
    failure_amount: int = 5
    failure_period: int = 30

    state: str = "Closed"
    window = []  # which type to use?

    def __call__(self):
        if self.state == "Closed":
            try:
                return self.callback()
            except Exception:
                self.process_failure()
        else:
            raise BreakerCircuitOpenException()

    def check_failures_have_occurred_in_period(self):
        return True

    def process_failure(self):
        # Add a timestamp to the array
        print("here??")
        self.window.append(time.time())
        # Look at the count and period properties, and then get the number of timestamps in the array within that threshold
        if (
            len(self.window) >= self.failure_amount
            and self.check_failures_have_occurred_in_period()
        ):
            self.trip_breaker()
            return
        return

    def trip_breaker(self):
        self.state = "Open"
