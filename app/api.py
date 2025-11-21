from flask import Blueprint, request, jsonify, redirect
from .utils import generate_code, pick_shard
from .db import save_url, fetch_url, increment_clicks
from .cache import cache_get, cache_set
from .rate_limit import rate_limit
from .models import validate_long_url, InvalidURLError

api_bp = Blueprint("api", __name__)


# -----------------------------------------
#              SHORTEN URL
# -----------------------------------------

@api_bp.route("/shorten", methods=["POST"])
@rate_limit(max_requests=20, window_seconds=60)   # 20 req per minute
def shorten():
    """
    Create a new short URL.
    Expected payload: { "url": "https://example.com" }
    """
    data = request.get_json()

    if not data or "url" not in data:
        return jsonify({"error": "Missing 'url' field"}), 400

    long_url = data["url"]

    # Validate long URL format
    try:
        validate_long_url(long_url)
    except InvalidURLError as e:
        return jsonify({"error": str(e)}), 400

    # Generate short code
    short_code = generate_code()

    # Pick shard
    shard = pick_shard(short_code, shard_count=4)

    # Save to DB
    try:
        save_url(shard, short_code, long_url)
    except Exception:
        return jsonify({"error": "Database error"}), 500

    # Cache the mapping
    cache_set(short_code, long_url)

    return jsonify({
        "short_url": f"https://snap.url/{short_code}",
        "code": short_code
    }), 201


# -----------------------------------------
#             REDIRECT URL
# -----------------------------------------

@api_bp.route("/<short_code>", methods=["GET"])
def redirect_url(short_code):
    """
    Redirect the user from a short code to the actual long URL.
    """

    # Try Redis first
    long_url = cache_get(short_code)
    if long_url:
        # Increment click count (analytics)
        shard = pick_shard(short_code, shard_count=4)
        increment_clicks(shard, short_code)
        return redirect(long_url, code=302)

    # Cache miss → DB
    shard = pick_shard(short_code, shard_count=4)
    long_url = fetch_url(shard, short_code)

    if long_url:
        cache_set(short_code, long_url)
        increment_clicks(shard, short_code)
        return redirect(long_url, code=302)

    return jsonify({"error": "Short URL not found"}), 404


# -----------------------------------------
#          ANALYTICS ENDPOINT
# -----------------------------------------

@api_bp.route("/analytics/<short_code>", methods=["GET"])
def analytics(short_code):
    """
    Get click analytics for a given short URL.
    """
    shard = pick_shard(short_code, shard_count=4)

    conn_url = fetch_url(shard, short_code)
    if not conn_url:
        return jsonify({"error": "Short URL not found"}), 404

    # Fetch click count
    from .db import get_conn, release_conn
    conn = get_conn(shard)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT clicks FROM urls WHERE short_code=%s",
        (short_code,)
    )
    row = cursor.fetchone()
    cursor.close()
    release_conn(shard, conn)

    clicks = row[0] if row else 0

    return jsonify({
        "short_code": short_code,
        "long_url": conn_url,
        "clicks": clicks
    })
