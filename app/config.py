import os


class Config:
    # Redis
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

    # Number of shards
    SHARD_COUNT = 4

    # PostgreSQL shard hosts
    SHARD_HOSTS = [
        os.getenv("DB0_HOST", "db0"),
        os.getenv("DB1_HOST", "db1"),
        os.getenv("DB2_HOST", "db2"),
        os.getenv("DB3_HOST", "db3"),
    ]

    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "snapurl")
