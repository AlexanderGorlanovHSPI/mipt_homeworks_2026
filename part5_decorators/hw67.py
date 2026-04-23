import json
from datetime import UTC, datetime, timedelta
from functools import wraps
from typing import Any, ParamSpec, Protocol, TypeVar, cast
from urllib.request import urlopen

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
INVALID_TRIGGERS_ON = "triggers exeptions must be Exeptions!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."


P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class CallableWithMeta(Protocol[P, R_co]):
    __name__: str
    __module__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


class BreakerError(Exception):
    def __init__(self, function_name: str, block_time: datetime):
        super().__init__(TOO_MUCH)
        self.func_name = function_name
        self.block_time = block_time


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ):
        errors = self._validate_args(critical_count, time_to_recover, triggers_on)

        if errors:
            raise ExceptionGroup(VALIDATIONS_FAILED, errors)

        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on

        self.failure_count: int = 0
        self.blocked_until: datetime | None = None
        self.block_time: datetime | None = None

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            now = datetime.now(UTC)
            function_name = f"{func.__module__}.{func.__name__}"
            self._check_block_state(now, function_name)

            try:
                result = func(*args, **kwargs)
            except Exception as error:
                if isinstance(error, self.triggers_on):
                    self._handle_failure(error, now, function_name)
                raise

            self._reset_breaker()
            return result

        return wrapper

    def _validate_args(
        self,
        critical_count: object,
        time_to_recover: object,
        triggers_on: object,
    ) -> list[ValueError]:
        errors: list[ValueError] = []
        critical_is_valid_type = isinstance(critical_count, int)
        if (not critical_is_valid_type) or (critical_count <= 0):
            errors.append(ValueError(INVALID_CRITICAL_COUNT))

        recover_is_valid_type = isinstance(time_to_recover, int)
        if (not recover_is_valid_type) or (time_to_recover <= 0):
            errors.append(ValueError(INVALID_RECOVERY_TIME))

        triggers_on_is_valid_type = isinstance(triggers_on, Exception)
        if not triggers_on_is_valid_type:
            errors.append(ValueError(INVALID_TRIGGERS_ON))

        return errors

    def _check_block_state(self, now: datetime, function_name: str) -> None:
        if self.blocked_until is None:
            return
        if now < self.blocked_until:
            block_time = now
            if self.block_time is not None:
                block_time = self.block_time
            raise BreakerError(function_name, block_time)
        self._reset_breaker()

    def _handle_failure(self, error: Exception, now: datetime, function_name: str) -> None:
        self.failure_count += 1
        if self.failure_count >= self.critical_count:
            self.block_time = now
            self.blocked_until = now + timedelta(seconds=self.time_to_recover)
            raise BreakerError(function_name, now) from error

    def _reset_breaker(self) -> None:
        self.failure_count = 0
        self.blocked_until = None
        self.block_time = None


circuit_breaker = CircuitBreaker(5, 30, Exception)


# @circuit_breaker
def get_comments(post_id: int) -> Any:
    """
    Получает комментарии к посту

    Args:
        post_id (int): Идентификатор поста

    Returns:
        list[dict[int | str]]: Список комментариев
    """
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
