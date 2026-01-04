# tests/unit/gateway/breaker_test.py

from unittest.mock import Mock

from gateway.breaker import Breaker


def test_breaker_executes_callback_when_circuit_is_closed():
    cb = Mock(return_value=True)

    @Breaker
    def func():
        return cb()

    result = func()

    cb.assert_called_once()
    assert result


# def test_breaker_state_updates_correctly_after_callback_fails():
#     #todo

# def test_breaker_prevents_callback_from_being_executed_if_failure_state_is_active():
#     #todo

# def test_breaker_failure_state_is_reset_after_successful_request():
#     #todo

#     def test_breaker_accepts_failure_threshold_in_pct():
#     #todo

# def test_breaker_throws_exception_if_callback_result_is_invalid():
#     #todo
