import logging
import time
from functools import wraps

from psutil import cpu_percent, virtual_memory


def _get_machine_stats():
    try:
        return {
            "cpu": f"CPU: {cpu_percent()}%",
            "ram": f"MEM: {virtual_memory().percent}%",
        }

    except Exception as e:
        print(f"Error getting machine stats: {e}")
        return {"cpu": "-", "ram": "-"}


def _colored(text, color_name):
    colors = {
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "magenta": 35,
        "cyan": 36,
        "white": 37,
    }
    color = colors.get(color_name, 37)
    return f"\033[{color}m{text}\033[0m"


class MachineAwareLoggerFormatter(logging.Formatter):
    def format(self, record):
        machine_stats = _get_machine_stats()
        record.cpu = machine_stats["cpu"]
        record.ram = machine_stats["ram"]
        return super().format(record)


def get_logger():
    logger = logging.getLogger(__name__)
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    asctime_str = _colored("%(asctime)s", "blue")
    levelname_str = _colored("%(levelname)s", "green")
    message_str = _colored("%(message)s", "white")
    cpu_str = _colored("%(cpu)s", "yellow")
    ram_str = _colored("%(ram)s", "magenta")
    logger.handlers[0].setFormatter(
        MachineAwareLoggerFormatter(
            f"[{asctime_str}] [{levelname_str}] {message_str} [{cpu_str}] [{ram_str}]"
        )
    )
    return logger


def log_time(logger):
    """
    Logs the time it took to execute a async function
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            result = await func(*args, **kwargs)
            end = time.time()
            logger.info(f"Function {func.__name__} took {end - start} seconds")
            return result

        return wrapper

    return decorator
