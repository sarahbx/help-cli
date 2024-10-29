#!/usr/bin/env python3
import config
from hey_clipy.__main__ import main
from hey_clipy.logger import setup_logging

if __name__ == "__main__":
    log_listener = setup_logging()
    main(config=config)
    log_listener.stop()

