"""
Unit tests for the Flask orders application.

The database is mocked so these tests run without a real PostgreSQL instance.
"""

import pytest
from unittest.mock import MagicMock, patch

import app as flask_app


@pytest.fixture
def client():
    flask_app.app.config["TESTING"] = True
    with flask_app.app.test_client() as client:
        yield client


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------

def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_ok_status(client):
    response = client.get("/health")
    data = response.get_json()
    assert data == {"status": "ok"}


# ---------------------------------------------------------------------------
# Order details page — database mocked
# ---------------------------------------------------------------------------

def _make_mock_row(order_id, product_id, unit_price, quantity, discount):
    return {
        "order_id": order_id,
        "product_id": product_id,
        "unit_price": unit_price,
        "quantity": quantity,
        "discount": discount,
    }


@patch("app.get_db_connection")
def test_order_details_renders_table(mock_get_conn, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
    mock_cursor.__exit__ = MagicMock(return_value=False)
    mock_cursor.fetchone.return_value = {"server_name": "10.0.0.4"}
    mock_cursor.fetchall.return_value = [
        _make_mock_row(10248, 11, 14.00, 12, 0.0),
        _make_mock_row(10248, 42, 9.80, 10, 0.0),
    ]
    mock_conn.cursor.return_value = mock_cursor
    mock_get_conn.return_value = mock_conn

    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode()
    assert "Order Details" in html
    assert "Connected to Database Server" in html
    assert "10248" in html
    assert "10.0.0.4" in html


@patch("app.get_db_connection")
def test_order_details_shows_error_on_db_failure(mock_get_conn, client):
    import psycopg2
    mock_get_conn.side_effect = psycopg2.OperationalError("connection refused")

    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode()
    assert "Error:" in html
    assert "connection refused" in html


@patch("app.get_db_connection")
def test_order_details_escapes_output(mock_get_conn, client):
    """Jinja2 auto-escaping must prevent XSS in data values."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
    mock_cursor.__exit__ = MagicMock(return_value=False)
    mock_cursor.fetchone.return_value = {"server_name": "<script>alert(1)</script>"}
    mock_cursor.fetchall.return_value = []
    mock_conn.cursor.return_value = mock_cursor
    mock_get_conn.return_value = mock_conn

    response = client.get("/")
    html = response.data.decode()
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html
