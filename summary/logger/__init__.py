import logging

def setup_logger():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("uvicorn.access")
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    return logger
