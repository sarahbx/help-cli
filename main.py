#!/usr/bin/env python3
import config
from help_cli.__main__ import main
from help_cli.logger import setup_logging

if __name__ == "__main__":
    log_listener = setup_logging()
    main(config=config)
    log_listener.stop()

