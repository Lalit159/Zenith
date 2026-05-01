"""
Configuration module for Zenith order matching engine.
Loads settings from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# SERVER CONFIGURATION
# ============================================================================
SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))


# ============================================================================
# ORDER MATCHING ENGINE CONFIGURATION
# ============================================================================
# Maximum number of active orders before warning
MAX_ACTIVE_ORDERS_WARNING = int(os.getenv("MAX_ACTIVE_ORDERS_WARNING", "10000"))

# Timeout for order processing (in seconds)
ORDER_TIMEOUT = float(os.getenv("ORDER_TIMEOUT", "60.0"))

# ============================================================================
# STRESS TEST CONFIGURATION
# ============================================================================
STRESS_TEST_NUM_ORDERS = int(os.getenv("STRESS_TEST_NUM_ORDERS", "1000"))


def get_config_summary() -> dict:
    """Return a dictionary of all configuration values."""
    return {
        "Server": f"{SERVER_HOST}:{SERVER_PORT}"
    }
