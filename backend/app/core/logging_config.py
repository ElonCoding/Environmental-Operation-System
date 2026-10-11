import logging
import sys

def setup_logging(debug: bool = False):
    level = logging.DEBUG if debug else logging.INFO
    log_format = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
