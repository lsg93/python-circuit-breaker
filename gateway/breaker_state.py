from dataclasses import dataclass
from time import time


@dataclass
class Breaker:
    """Breaker class - prevents requests to external services from being made if the service is unreliable."""

    callback: Callable
    failure_amount: int = 5
    failure_period: int = 30

    def __post_init__(self):
        self.window = []  # This will track the long term progress of requests.
        self.state = "Closed"  # Breaker state - if false, circuit is 'closed' and working - should be an enum I think.

    def __call__(self):
        try:
            if self.state == "Closed":
                return self.callback()
        except Exception:
            self.process_failure()
        return

    def process_failure(self):
        # Add a timestamp to the array
        self.window.append(time.time())
        # Look at the count and period properties, and then get the number of timestamps in the array within that threshold
        if len(self.window)

        # if the count happens within the given period, call trip_breaker.
        pass

    def trip_breaker(self):
        self.state = "Open"
