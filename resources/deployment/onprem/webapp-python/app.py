import os

import psycopg2
import psycopg2.extras
from flask import Flask, render_template

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Database configuration — read from environment variables, never hardcoded.
# Copy .env.example to .env and fill in values for local development.
# ---------------------------------------------------------------------------
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 5432)),
    "dbname": os.environ.get("DB_NAME", "northwind"),
    "user": os.environ.get("DB_USER", "demouser"),
    "password": os.environ.get("DB_PASSWORD", ""),
}


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


@app.route("/")
def order_details():
    server_addr = None
    rows = []
    error = None

    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT inet_server_addr() AS server_name")
            result = cur.fetchone()
            server_addr = result["server_name"] if result else "unknown"

            cur.execute(
                "SELECT order_id, product_id, unit_price, quantity, discount"
                " FROM order_details"
            )
            rows = cur.fetchall()
        conn.close()
    except psycopg2.Error as exc:
        error = str(exc)

    return render_template(
        "orders.html",
        server_addr=server_addr,
        rows=rows,
        error=error,
    )


@app.route("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
