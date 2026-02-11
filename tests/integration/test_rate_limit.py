import os
from slowapi import Limiter
from slowapi.util import get_remote_address

TESTING = os.getenv("TESTING") == "1"

limiter = Limiter(
    key_func=get_remote_address,
    enabled=not TESTING   # 🔥 disable in tests
)