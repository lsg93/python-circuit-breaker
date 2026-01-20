import time
from dataclasses import dataclass, field
from enum import Enum


class BreakerState(Enum):
    CLOSED = "Closed"
    OPEN = "Open"
    HALF_OPEN = "Half-Open"


class BreakerCircuitOpenException(Exception):
    pass


@dataclass
class Breaker:
    """Breaker class - designed to prevent requests to external services from being made if the service is unreliable.
    It should be used as a context manager.
    """

    failure_amount: int = 5
    failure_period: int = 30
    retry_after: int = 6000
    stable_at: int = 2

    state: str = BreakerState.CLOSED
    window: list = field(default_factory=list)

    def __post_init__(self):
        self.reset_success_counter()

    def __enter__(self):
        if self.state == BreakerState.OPEN:
            self.check_retry_period()

            # If state has not been reset, exit early.
            if self.state == BreakerState.OPEN:
                self.reset_success_counter()
                raise BreakerCircuitOpenException

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Process the failure
            self.process_failure()
            # The caught exception should be rethrown for further use in any logic.
            return False

        # Update success amount since no exception was raised.
        self.check_stability()

        return True

    def check_failures_have_occurred_in_period(self):
        # Get all failures in the window that fall within the specified failure period.
        now = int(time.time())
        recent_failures = []

        for timestamp in self.window:
            if now - timestamp <= self.failure_period:
                recent_failures.append(timestamp)

        # This also acts as a way of pruning the window.
        self.window = recent_failures

        return len(recent_failures) >= self.failure_amount

    def process_failure(self):
        # Add a timestamp to the 'window' array
        self.window.append(int(time.time()))

        # If the request failed when the breaker was Half-Open, reset the state.
        if self.state == BreakerState.HALF_OPEN:
            self.set_circuit_state(BreakerState.OPEN)
            return

        if self.check_failures_have_occurred_in_period():
            self.set_circuit_state(BreakerState.OPEN)

        return

    def check_retry_period(self):
        if len(self.window) == 0:
            return

        most_recent_failure = self.window[-1]

        # Enough time has passed since most recent failure to allow one request through.
        if (int(time.time()) - most_recent_failure) > self.retry_after:
            self.set_circuit_state(BreakerState.HALF_OPEN)

    def check_stability(self):
        self.successes_until_stable += 1
        if self.successes_until_stable == 0:
            self.reset_success_counter()
            self.set_circuit_state(BreakerState.CLOSED)
        return

    def reset_success_counter(self):
        self.successes_until_stable = -self.stable_at
        return

    def set_circuit_state(self, state: BreakerState):
        self.state = state
        return
