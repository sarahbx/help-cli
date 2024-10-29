import logging
import multiprocessing
from logging.handlers import QueueHandler, QueueListener

from simple_logger.logger import WrapperLogFormatter, DuplicateFilter


def setup_logging(log_level=logging.INFO) -> QueueListener:
    basic_log_formatter = logging.Formatter(fmt="%(message)s")
    root_log_formatter = WrapperLogFormatter(
        fmt="%(asctime)s %(name)s %(log_color)s%(levelname)s%(reset)s %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={},
    )
    log_stream_handler = logging.StreamHandler()
    log_queue = multiprocessing.Queue(maxsize=-1)
    log_listener = QueueListener(log_queue, log_stream_handler)

    basic_log_queue_handler = QueueHandler(queue=log_queue)
    basic_log_queue_handler.set_name(name="basic")
    basic_log_queue_handler.setFormatter(fmt=basic_log_formatter)

    basic_logger = logging.getLogger("basic")
    basic_logger.setLevel(level=log_level)
    basic_logger.addHandler(hdlr=basic_log_queue_handler)

    root_log_queue_handler = QueueHandler(queue=log_queue)
    root_log_queue_handler.set_name(name="root")
    root_log_queue_handler.setFormatter(fmt=root_log_formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level=log_level)
    root_logger.addHandler(hdlr=root_log_queue_handler)
    root_logger.addFilter(filter=DuplicateFilter())

    root_logger.propagate = False
    basic_logger.propagate = False
    log_listener.start()

    return log_listener
