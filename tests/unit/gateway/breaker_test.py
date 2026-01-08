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


def test_breaker_remains_closed_when_failures_occur_outside_of_given_time_period(
    time_machine,
):
    cb = Mock(return_value=None, side_effect=Exception)

    time_machine.move_to(0)
    breaker = Breaker(callback=cb, failure_amount=2, failure_period=60 * 60 * 24)
    breaker()

    time_machine.shift((60 * 60 * 24) + 1)
    breaker()

    assert cb.call_count == 2


def test_breaker_opens_circuit_only_when_failures_occur_inside_given_time_period(
    time_machine,
):
    cb = Mock(return_value=None, side_effect=Exception)

    time_machine.move_to(0)
    breaker = Breaker(callback=cb, failure_amount=1, failure_period=60 * 60 * 24)
    breaker()

    time_machine.shift((60 * 60 * 24) + 1)
    with pytest.raises(BreakerCircuitOpenException):
        breaker()

    assert cb.call_count == 1


# def test_breaker_closes_circuit_when_callback_is_succesful_while_circuit_is_open():
#     #todo


# stretch goal here...
#     def test_breaker_accepts_failure_threshold_in_pct():
#     #todo
