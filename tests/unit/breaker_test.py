import time
from unittest.mock import Mock

import pytest

from breaker.breaker import Breaker, BreakerCircuitOpenException


# Use a specific exception rather than relying on the base Exception class.
# Could end up with false positives otherwise.
class CallbackException(Exception):
    pass


def test_breaker_executes_callback_when_circuit_is_closed():
    cb = Mock(return_value=True)

    breaker = Breaker(callback=cb)
    result = breaker()

    cb.assert_called_once()
    assert result


# I think this is a more robust test for the logic than multiple smaller tests which look @ 'private' properties.
# We immediately 'trip' the breaker by setting its failure threshold to 1
# Then we try again. It should fail, which proves the state update is handled, and that the logic preventing subsequent requests works.
def test_breaker_opens_circuit_and_prevents_subsequent_requests_after_failure_threshold_is_met():
    cb = Mock(return_value=None, side_effect=CallbackException)

    breaker = Breaker(callback=cb, failure_amount=1)
    with pytest.raises(CallbackException):
        breaker()
    with pytest.raises(BreakerCircuitOpenException):
        breaker()

    cb.assert_called_once()


def test_breaker_remains_closed_when_failures_occur_outside_of_given_time_period(
    time_machine,
):
    cb = Mock(return_value=None, side_effect=CallbackException)

    time_machine.move_to(time.time())
    breaker = Breaker(callback=cb, failure_amount=2, failure_period=60 * 60 * 24)
    with pytest.raises(CallbackException):
        breaker()

    time_machine.shift((60 * 60 * 24) + 1)
    with pytest.raises(CallbackException):
        breaker()

    # As there are 2 failures, but they happened far enough from one another, the circuit should still be closed.
    with pytest.raises(CallbackException):
        breaker()


def test_breaker_opens_circuit_only_when_failures_occur_inside_given_time_period(
    time_machine,
):
    cb = Mock(return_value=None, side_effect=CallbackException)

    time_machine.move_to(time.time())
    breaker = Breaker(callback=cb, failure_amount=2, failure_period=60 * 60 * 24)
    with pytest.raises(CallbackException):
        breaker()

    time_machine.shift((60 * 60 * 24) - 1)
    with pytest.raises(CallbackException):
        breaker()

    # The breaker should now be open and not run the callback
    # As there are 2 failures, but they happened far enough from one another it shouldn't open the circuit.
    with pytest.raises(BreakerCircuitOpenException):
        breaker()

    assert cb.call_count == 2


def test_breaker_sets_circuit_to_half_open_after_succesful_callback_when_closed(
    time_machine,
):
    cb = Mock(
        return_value=None, side_effect=[CallbackException, CallbackException, None]
    )

    time_machine.move_to(time.time())
    breaker = Breaker(
        callback=cb, failure_amount=2, failure_period=60 * 60 * 24, retry_after=60
    )
    with pytest.raises(CallbackException):
        breaker()

    time_machine.shift((60 * 60 * 24) - 1)
    with pytest.raises(CallbackException):
        breaker()

    # The breaker should now be half-open, and run the callback
    time_machine.shift(61)
    breaker()

    assert cb.call_count == 3


def test_single_failure_in_half_open_state_opens_circuit(time_machine):
    # We want our mock to fail, then succeed for the purposes of this test.
    cb = Mock(
        return_value=None,
        side_effect=[CallbackException, CallbackException, CallbackException],
    )

    time_machine.move_to(time.time())
    breaker = Breaker(callback=cb, failure_amount=2, failure_period=60, retry_after=60)

    # First two callback attempts should fail with exception from mock.
    # The second should 'trip' the breaker.
    with pytest.raises(CallbackException):
        breaker()
    with pytest.raises(CallbackException):
        breaker()

    # Because the retry timer has elapsed, the breaker state will now be 'Half-Open'.
    # This callback should be attempted, but fail.
    time_machine.shift(61)
    with pytest.raises(CallbackException):
        breaker()

    # Even though our failure threshold should allow for this request,
    # This callback will not be executed by the breaker because the failure in half open state opens the circuit.
    with pytest.raises(BreakerCircuitOpenException):
        breaker()


def test_success_in_half_open_state_closes_circuit_based_on_given_stability_parameter(
    time_machine,
):
    # We want our mock to fail until our breaker gets to half-open state, then succeed.
    cb = Mock(
        return_value=None,
        side_effect=[
            CallbackException,
            None,
            None,
            CallbackException,
        ],
    )

    time_machine.move_to(time.time())
    breaker = Breaker(
        callback=cb, failure_amount=1, failure_period=60, retry_after=60, stable_at=2
    )

    # First callback should fail with exception from mock and open the circuit
    with pytest.raises(CallbackException):
        breaker()

    # Because the retry timer has elapsed, the breaker state will now be 'Half-Open'.
    # These callback should be attempted, and succeed.
    time_machine.shift(61)
    breaker()
    breaker()

    # The previous two successes should trip our breaker back to closed state
    # A final failure should raise the regular exception, not the breaker exception.
    with pytest.raises(CallbackException):
        breaker()
