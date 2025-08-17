import logging

def setup_uvicorn_logger(host="127.0.0.1", port=8000):
    logger = logging.getLogger("uvicorn")
    for h in logger.handlers:
        formatter = logging.Formatter(f"%(asctime)s - Uvicorn running on http://{host}:{port} - %(levelname)s - %(message)s")
        h.setFormatter(formatter)
    return logger
