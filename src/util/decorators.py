import random
import sys
import time

from functools import wraps


def retry_on_error(max_retries=2, wait_time=None):
    """
    A decorator that retries a function call a specified number of times
    if an exception occurs.

    Args:
        max_retries (int): The maximum number of times to retry the function.
        wait_time (int): The time in seconds to wait between retries. If not provided, a random value between 10 and 20 seconds is used.
    """
    if wait_time is None:
        wait_time = random.randint(10, 20)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            max_attempts = max_retries + 1
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        sys.__stdout__.write(
                            f"{func.__name__} failed with: {e}. Retrying in {wait_time} seconds...\n"
                        )
                        sys.__stdout__.flush()
                        time.sleep(wait_time)
                    else:
                        sys.__stdout__.write(
                            f"{func.__name__} failed after {max_attempts} attempts.\n"
                        )
                        sys.__stdout__.flush()
            raise last_exception

        return wrapper

    return decorator
