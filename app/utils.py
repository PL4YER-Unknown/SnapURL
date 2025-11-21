import random
import string
import hashlib


def generate_code(length=7):
    pool = string.ascii_letters + string.digits
    return ''.join(random.choices(pool, k=length))


def pick_shard(code: str, shard_count: int) -> int:
    """Hash the short code → shard number."""
    h = hashlib.sha256(code.encode()).hexdigest()
    return int(h, 16) % shard_count
