import time
from dataclasses import dataclass, field


class BreakerCircuitOpenException(Exception):
    pass


@dataclass
class Breaker:
    """Breaker class - prevents requests to external services from being made if the service is unreliable."""

    failure_amount: int = 5
    failure_period: int = 30
    retry_after: int = 6000
    stable_at: int = 2

    state: str = "Closed"
    window: list = field(default_factory=list)

    def __post_init__(self):
        # This ensures the counter starts fresh based on the user's config
        self.reset_success_counter()

    def __enter__(self):
        if self.state == "Open":
            self.check_retry_period()

            # If state has not been reset, exit early.
            if self.state == "Open":
                self.reset_success_counter()
                raise BreakerCircuitOpenException

        self.check_stability()

    def __exit__(self, exc_type):
        if exc_type is Exception:
            # Process the failure
            self.process_failure()
            # The caught exception should be rethrown for further use in any logic.
            return False
        return True

    def check_failures_have_occurred_in_period(self):
        # Get all failures in the window that fall within the specified failure period.
        now = int(time.time())
        recent_failures = []

        for timestamp in self.window:
            if now - timestamp <= self.failure_period:
                recent_failures.append(timestamp)

        # # This also acts as a way of pruning the window.
        # self.window = recent_failures

        return len(recent_failures) >= self.failure_amount

    def process_failure(self):
        # Add a timestamp to the 'window' array
        self.window.append(int(time.time()))

        # If the request failed when the breaker was Half-Open, reset the state.
        if self.state == "Half-Open":
            self.set_circuit_state("Open")
            return

        if self.check_failures_have_occurred_in_period():
            self.set_circuit_state("Open")

        return

    def check_retry_period(self):
        if len(self.window) == 0:
            return

        most_recent_failure = self.window[-1]

        # Enough time has passed since most recent failure to allow one request through.
        if (int(time.time()) - most_recent_failure) > self.retry_after:
            self.set_circuit_state("Half-Open")

    def check_stability(self):
        self.successes_until_stable += 1
        if self.successes_until_stable == 0:
            self.reset_success_counter()
            self.set_circuit_state("Closed")
        return

    def reset_success_counter(self):
        self.successes_until_stable = -self.stable_at
        return

    def set_circuit_state(self, state: str):
        self.state = state
        return
