import psycopg2
from psycopg2 import pool
from flask import current_app
import time
import psycopg2

db_pools = []  # List of connection pools per shard


# def init_db_pools(app):
#     # """
#     # Initialize connection pools for all shards.
#     # Called once at app startup from __init__.py
#     # """
#     # global db_pools
#     # config = app.config

#     # shard_hosts = config["SHARD_HOSTS"]
#     # user = config["POSTGRES_USER"]
#     # pwd = config["POSTGRES_PASSWORD"]
#     # dbname = config["POSTGRES_DB"]

#     # for host in shard_hosts:
#     #     db_pools.append(
#     #         pool.SimpleConnectionPool(
#     #             minconn=2,
#     #             maxconn=10,
#     #             host=host,
#     #             user=user,
#     #             password=pwd,
#     #             dbname=dbname,
#     #             port=5432,
#     #         )
#     #     )
#     global db_pools

#     config = app.config  # ✔️ USE app – DO NOT USE current_app

#     shard_hosts = config["SHARD_HOSTS"]
#     user = config["POSTGRES_USER"]
#     password = config["POSTGRES_PASSWORD"]
#     dbname = config["POSTGRES_DB"]

#     for host in shard_hosts:
#         db_pools.append(
#             pool.SimpleConnectionPool(
#                 minconn=1,
#                 maxconn=5,
#                 host=host,
#                 port=5432,
#                 user=user,
#                 password=password,
#                 dbname=dbname
#             )
#         )
def init_db_pools(app):
    global db_pools

    config = app.config
    shard_hosts = config["SHARD_HOSTS"]
    user = config["POSTGRES_USER"]
    password = config["POSTGRES_PASSWORD"]
    dbname = config["POSTGRES_DB"]

    for host in shard_hosts:
        for attempt in range(15):  # wait up to ~30 seconds
            try:
                conn_pool = pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=5,
                    host=host,
                    port=5432,
                    user=user,
                    password=password,
                    dbname=dbname
                )
                db_pools.append(conn_pool)
                print(f"[DB] Connected to shard {host}")
                break

            except psycopg2.OperationalError:
                print(f"[DB] Waiting for {host} to be ready... (attempt {attempt+1}/15)")
                time.sleep(2)

        else:
            raise RuntimeError(f"Failed to connect to shard {host} after many attempts")


def get_conn(shard_id: int):
    """Retrieve a connection from the appropriate shard pool."""
    return db_pools[shard_id].getconn()


def release_conn(shard_id: int, conn):
    """Return a connection to the appropriate shard pool."""
    db_pools[shard_id].putconn(conn)


# ------------------------------
#       CRUD OPERATIONS
# ------------------------------

def save_url(shard_id: int, short_code: str, long_url: str):
    """
    Insert a new short_code → long_url mapping into the shard.
    """
    conn = get_conn(shard_id)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO urls (short_code, long_url)
            VALUES (%s, %s)
            """,
            (short_code, long_url)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        release_conn(shard_id, conn)


def fetch_url(shard_id: int, short_code: str):
    """
    Fetch the long URL for this short code.
    Returns None if not found.
    """
    conn = get_conn(shard_id)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT long_url FROM urls WHERE short_code = %s",
            (short_code,)
        )
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        cursor.close()
        release_conn(shard_id, conn)


def increment_clicks(shard_id: int, short_code: str):
    """
    Increase click count (analytics).
    """
    conn = get_conn(shard_id)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE urls
            SET clicks = clicks + 1
            WHERE short_code = %s
            """,
            (short_code,)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        release_conn(shard_id, conn)
