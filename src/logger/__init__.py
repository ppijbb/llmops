import logging


def _server_logger():
    # logger name
    # logger_name = "uvicorn.access"
    logger_name = "ray.serve"
    
    return logging.getLogger(logger_name)

def setup_logger():
    logging.basicConfig(level=logging.INFO)
    logger = _server_logger()
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    return logger

def get_logger():
    return _server_logger() if _server_logger().hasHandlers() else setup_logger()
