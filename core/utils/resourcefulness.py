import asyncio
import logging
import functools
from typing import Any, Callable, List, TypeVar

T = TypeVar("T")
logger = logging.getLogger("AetherOS.Utils.Resourcefulness")

def relentless_resourcefulness(max_attempts: int = 10):
    """
    Decorator that implements the 'Relentless Resourcefulness' protocol.
    Retries a task with different internal strategies before reporting failure.
    """
    def decorator(func: Callable[..., Any]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            attempts = 0
            last_error = None

            while attempts < max_attempts:
                try:
                    # In a real impl, we'd pass the 'strategy_id' to the function
                    # so it can choose different tools or parameters.
                    result = await func(*args, **kwargs, attempt=attempts)
                    if result:
                        if attempts > 0:
                            logger.info(f"Relentless success on attempt {attempts + 1}")
                        return result
                except Exception as e:
                    attempts += 1
                    last_error = e
                    logger.warning(f"Attempt {attempts} failed: {e}. Trying next approach...")
                    # Delay between retries (could be exponential backoff)
                    await asyncio.sleep(0.5 * attempts)

            logger.error(f"Exhausted all {max_attempts} attempts. Final failure: {last_error}")
            raise last_error
        return wrapper
    return decorator
