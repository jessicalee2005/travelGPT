import logging

# Create a custom logger
logger = logging.getLogger(__name__)

# Set the log level to DEBUG
logger.setLevel(logging.DEBUG)

# Create handlers
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add handler to the logger
logger.addHandler(handler)

# Export the logger
__all__ = ['logger']