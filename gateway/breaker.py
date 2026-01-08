from dataclasses import dataclass, field
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
    window: list = field(default_factory=list)

    def __call__(self):
        if self.state == "Closed":
            try:
                return self.callback()
            except Exception:
                self.process_failure()
        else:
            raise BreakerCircuitOpenException()

    def check_failures_have_occurred_in_period(self):
        # Early return - if the amount of failures does not exceed the defined threshold, no more work needs to be done.
        if len(self.window) < self.failure_amount:
            return

        # Account for a failure threshold of 1 also.
        if self.failure_amount == 1:
            return True

        # Get the last failures in the window specified as the threshold
        # And check if the gap in seconds between first and last failure is less than given failure period.
        failures_slice = self.window[-self.failure_amount :]

        # Calculate the time time between the earliest and most recent failure
        first_failure = failures_slice[0]
        last_failure = failures_slice[-1]

        print(
            f"DEBUG: Window: {self.window} | Threshold: {self.failure_amount} | State: {self.state}"
        )

        return last_failure - first_failure <= self.failure_period

    def process_failure(self):
        # Add a timestamp to the array
        import time

        self.window.append(int(time.time()))
        print(f"appending time {int(time.time())}")

        if self.check_failures_have_occurred_in_period():
            self.open_circuit()
            return
        return

    def open_circuit(self):
        self.state = "Open"
        return
