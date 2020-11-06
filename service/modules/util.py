""" Utiliy functions """
from time import perf_counter
import sentry_sdk
def timer(func):
    """
        decorator to calculate runtime
    """
    def wrapper(*args, **kwargs):
        start_time = perf_counter()
        result = func(*args, **kwargs)
        end_time = perf_counter()
        run_time = end_time - start_time
        print(f"{func.__name__!r} finished in {run_time:.4f} secs")
        with sentry_sdk.configure_scope() as scope:
            scope.set_extra(f"timer_{func.__name__}", f"{run_time:.4f}" + ' secs')
        return result
    return wrapper
