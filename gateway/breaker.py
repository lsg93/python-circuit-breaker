import pprint
import time
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
    retry_after: int = 6000

    state: str = "Closed"
    window: list = field(default_factory=list)

    def __call__(self):
        if self.state != "Open":
            try:
                result = self.callback()

                if self.state == "Half-Open":
                    # Reset window
                    self.window = []
                    self.set_circuit_state("Closed")

                return result
            except Exception as e:
                # Process the failure
                self.process_failure()
                # The caught exception should be rethrown for further use in any logic.
                raise e
        else:
            if self.state == "Open":
                self.check_retry_period()
            raise BreakerCircuitOpenException

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
        # If the gap is more than the failure period, open the circuit and prevent future attempts at running the callback.
        first_failure = failures_slice[0]
        last_failure = failures_slice[-1]

        return last_failure - first_failure <= self.failure_period

    def process_failure(self):
        # Add a timestamp to the 'window' array
        self.window.append(int(time.time()))

        if self.check_failures_have_occurred_in_period():
            pprint.pprint("Failures have happened in given period - open circuit.")
            self.set_circuit_state("Open")

        return

    def check_retry_period(self):
        if len(self.window) == 0:
            return

        most_recent_failure = self.window[-1]

        # Enough time has passed since most recent failure to allow one request through.
        if (int(time.time()) - most_recent_failure) > self.retry_after:
            self.set_circuit_state("Half-Open")

    def set_circuit_state(self, state: str):
        self.state = state
        return
