# result/Either pattern for error

"""Result type for error handling without exceptions."""
from dataclasses import dataclass
from typing import TypeVar, Generic, Union, Callable, Any

T = TypeVar("T")
E = TypeVar("E", bound=Exception)
U = TypeVar("U")


@dataclass(frozen=True)
class Ok(Generic[T]):
    """Represents a successful result."""
    
    value: T
    
    def is_ok(self) -> bool:
        return True
    
    def is_err(self) -> bool:
        return False
    
    def unwrap(self) -> T:
        """Get the value. Safe to call since this is Ok."""
        return self.value
    
    def unwrap_or(self, default: T) -> T:
        """Get the value or default. Returns value since this is Ok."""
        return self.value
    
    def map(self, fn: Callable[[T], U]) -> "Result[U, Any]":
        """Apply function to the value."""
        return Ok(fn(self.value))
    
    def and_then(self, fn: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        """Chain another operation that may fail."""
        return fn(self.value)


@dataclass(frozen=True)
class Err(Generic[E]):
    """Represents a failed result."""
    
    error: E
    
    def is_ok(self) -> bool:
        return False
    
    def is_err(self) -> bool:
        return True
    
    def unwrap(self) -> Any:
        """Attempt to get value. Raises the error since this is Err."""
        raise self.error
    
    def unwrap_or(self, default: T) -> T:
        """Get the value or default. Returns default since this is Err."""
        return default
    
    def map(self, fn: Callable[[Any], U]) -> "Result[U, E]":
        """Apply function to the value. Returns Err since this is Err."""
        return Err(self.error)
    
    def and_then(self, fn: Callable[[Any], "Result[U, E]"]) -> "Result[U, E]":
        """Chain another operation. Returns Err since this is Err."""
        return Err(self.error)


# Union type for Result
Result = Union[Ok[T], Err[E]]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def try_call(fn: Callable[[], T], *exceptions: type[Exception]) -> Result[T, Exception]:
    """
    Execute a function and wrap the result.
    
    Usage:
        result = try_call(lambda: some_risky_operation(), ValueError, IOError)
        if result.is_ok():
            print(result.unwrap())
        else:
            print(f"Error: {result.error}")
    """
    exception_types = exceptions if exceptions else (Exception,)
    try:
        return Ok(fn())
    except exception_types as e:
        return Err(e)


def collect_results(results: list[Result[T, E]]) -> Result[list[T], E]:
    """
    Collect a list of Results into a Result of list.
    Returns first error if any result is Err.
    
    Usage:
        results = [Ok(1), Ok(2), Ok(3)]
        collected = collect_results(results)  # Ok([1, 2, 3])
        
        results = [Ok(1), Err(ValueError("oops")), Ok(3)]
        collected = collect_results(results)  # Err(ValueError("oops"))
    """
    values: list[T] = []
    for result in results:
        if result.is_err():
            return Err(result.error)  # type: ignore
        values.append(result.unwrap())
    return Ok(values)