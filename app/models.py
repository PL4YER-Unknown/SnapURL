import re
from dataclasses import dataclass
from urllib.parse import urlparse


# ------------------------------
#      Custom Exceptions
# ------------------------------

class InvalidURLError(Exception):
    pass


# ------------------------------
#           Models
# ------------------------------

@dataclass
class URLRecord:
    """
    Represents a mapping: short_code → long_url.
    Stored in PostgreSQL shards.
    """
    short_code: str
    long_url: str
    clicks: int = 0


@dataclass
class AnalyticsRecord:
    """
    Represents analytics information about a URL.
    Returned to API or dashboard.
    """
    short_code: str
    clicks: int


# ------------------------------
#        Validations
# ------------------------------

def validate_long_url(url: str):
    """
    Validate the long URL before inserting into database.
    """

    if not url or len(url) > 4096:
        raise InvalidURLError("Invalid URL: too long or empty.")

    parsed = urlparse(url)

    if not parsed.scheme or not parsed.netloc:
        raise InvalidURLError("URL must include http/https and domain.")

    # Basic sanity regex
    regex = re.compile(
        r'^(?:http|https)://'
        r'(?:[\w-]+\.)+[a-zA-Z]{2,}'
        r'(?:/[\w\-.~:/?#[\]@!$&\'()*+,;=%]*)?$'
    )

    if not regex.match(url):
        raise InvalidURLError("Invalid URL format.")


# ------------------------------
#     Utility Converters
# ------------------------------

def record_from_row(row):
    """
    Convert DB row to URLRecord object.
    Format: (short_code, long_url, clicks)
    """
    return URLRecord(
        short_code=row[0],
        long_url=row[1],
        clicks=row[2],
    )
