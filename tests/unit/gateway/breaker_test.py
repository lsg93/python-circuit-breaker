import time
from unittest.mock import Mock

import pytest

from gateway.breaker import Breaker, BreakerCircuitOpenException


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

    assert cb.call_count == 2


def test_breaker_opens_circuit_only_when_failures_occur_inside_given_time_period(
    time_machine,
):
    cb = Mock(return_value=None, side_effect=CallbackException)

    time_machine.move_to(0)
    breaker = Breaker(callback=cb, failure_amount=2, failure_period=60 * 60 * 24)
    with pytest.raises(CallbackException):
        breaker()

    time_machine.shift((60 * 60 * 24) + 1)
    with pytest.raises(CallbackException):
        breaker()

    # The breaker should remain open and attempt to run the callback
    # As there are 2 failures, but they happened far enough from one another it shouldn't open the circuit.
    with pytest.raises(CallbackException):
        breaker()

    assert cb.call_count == 3


# Use a specific exception rather than relying on the base Exception class.
# Could end up with false positives otherwise.
class CallbackException(Exception):
    pass


def test_breaker_enters_half_open_state_based_on_given_retry_parameter(
    time_machine,
):
    # We want our mock to fail, then succeed for the purposes of this test.
    cb = Mock(return_value=None, side_effect=[CallbackException, None, None])

    time_machine.move_to(time.time())
    breaker = Breaker(callback=cb, failure_amount=1, failure_period=60, retry_after=60)

    # First callback should fail with exception from mock and close the circuit
    with pytest.raises(CallbackException):
        breaker()

    # Second callback should not be attempted and raise a Breaker exception
    # But simultaneously set the state of the breaker to 'Half-Open' due to the retry timer elapsing
    time_machine.shift(61)
    with pytest.raises(BreakerCircuitOpenException):
        breaker()

    # This call should be executed succesfully as the state has been set to half open
    assert breaker() is None

    # This might be a good candidate for some table-driven stuff...
    # This final call should either work or fail depending on the test we want to carry out
    # For now, we're just testing that a success in Half-Open state closes the circuit again.
    # But we could also test that a failure here raises an exception.
    assert breaker() is None

    assert cb.call_count == 3


# stretch goal here...
#     def test_breaker_accepts_failure_threshold_in_pct():
#     #todo
