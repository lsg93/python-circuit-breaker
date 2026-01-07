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
        # Get the last failure_amount of failures in the window
        # And check if the gap in seconds between first and last failure is less than given failure period.

        recent_failures = self.window[-self.failure_amount :]
        first = recent_failures[0]
        last = recent_failures[-1]

        print(recent_failures)
        print({"first": first, "last": last})
        print(self.failure_period)
        print((last - first) > self.failure_period)

        if (last - first) >= self.failure_period:
            return True

        return False

    def process_failure(self):
        # Add a timestamp to the array
        self.window.append(time.time())

        if self.check_failures_have_occurred_in_period():
            self.open_circuit()
            return
        return

    def open_circuit(self):
        self.state = "Open"
        return
