from functools import wraps
from datetime import datetime, timedelta


class CircuitBreaker(object):
    def __init__(self, name=None, expected_exception=Exception, max_failure_to_open=3, reset_timeout=10):
        """
        DO NOT ALTER FUNCTION ARGUMENTS AND THEIR DEFAULT VALUES!
        """
        self._name = name
        self._expected_exception = expected_exception
        self._max_failure_to_open = max_failure_to_open
        self._reset_timeout = reset_timeout
        # Set the initial state
        self.close()

    def close(self):
        """
        Your solution must work with this '_is_closed' boolean flag variable only.
        DO NOT SET ANYTHING OTHER THAN True OR False, OR YOU WILL GET ZERO!
        """
        self._is_closed = True
        self._failure_count = 0

    def open(self):
        self._is_closed = False
        self._open_since = datetime.utcnow()

    def __call__(self, func):
        if self._name is None:
            self._name = func.__name__

        @wraps(func)
        def with_circuitbreaker(*args, **kwargs):
            return self.call(func, *args, **kwargs)

        return with_circuitbreaker

    def call(self, func, *args, **kwargs):
        """
        Steps:
        1. If the cricuitbreaker is NOT in the executable state, then
           throw an Exception with this error message format -
            'CircuitBreaker[%s] is OPEN until %s (%d failures, %d sec remaining)'
                          {name}             {open_until} {failure_count}  {open_remaining}
        2. Call the given 'func' and handle the 'expected_exception'.
        """
        if not self.__is_closed == True:
            raise CircuitBreakerError(self)
        try:
            result = func(*args, **kwargs)
        except self._expected_exception:
            self.__failure()
            raise

        self.__success()
        return result


class CircuitBreakerError(Exception):
    def __init__(self, circuit_breaker, *args, **kwargs):
        """
        :param circuit_breaker:
        :param args:
        :param kwargs:
        :return:
        """
        super().__init__(*args, **kwargs)
        self._circuit_breaker = circuit_breaker

    def __str__(self, *args, **kwargs):
        return 'CIRCUIT "%s" OPEN until %s (%d failures, %d sec remaining)' % (
            self._circuit_breaker.name,
            self._circuit_breaker.open_until,
            self._circuit_breaker.failure_count,
            round(self._circuit_breaker.open_remaining)
        )