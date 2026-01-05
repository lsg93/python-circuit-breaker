from unittest.mock import Mock

import pytest

from gateway.breaker import Breaker, BreakerCircuitOpenException


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
    cb = Mock(return_value=None, side_effect=Exception)

    breaker = Breaker(callback=cb, failure_amount=1)
    breaker()
    with pytest.raises(BreakerCircuitOpenException):
        breaker()

    cb.assert_called_once()


# def test_breaker_opens_circuit_only_when_failures_occur_in_given_time_period():
# todo


# def test_breaker_independently_checks_if_callback_works_while_failure_state_is_active():
#     #todo

# def test_breaker_failure_state_is_reset_after_successful_request():
#     #todo


# stretch goal here...
#     def test_breaker_accepts_failure_threshold_in_pct():
#     #todo
