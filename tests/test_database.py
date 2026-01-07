"""
Unit tests for database operations.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.data.database import Database


@pytest.fixture
def mock_db():
    """Create a mock database instance"""
    with patch("src.data.database.psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        db = Database()
        db.conn = mock_conn
        yield db, mock_cursor


def test_save_post(mock_db):
    """Test saving a post to database"""
    db, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = {"id": 123}

    post_id = db.save_post(
        user_prompt="Test prompt",
        platform="linkedin",
        content="Test content",
        image_path="/path/to/image.jpg",
        image_prompt="Image prompt",
        status="draft",
    )

    assert post_id == 123
    mock_cursor.execute.assert_called_once()


def test_update_post_status(mock_db):
    """Test updating post status"""
    db, mock_cursor = mock_db

    db.update_post_status(123, "approved")

    mock_cursor.execute.assert_called_once()
    assert "UPDATE generated_posts" in str(mock_cursor.execute.call_args)


def test_get_post(mock_db):
    """Test retrieving a post by ID"""
    db, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = {"id": 123, "platform": "linkedin", "content": "Test"}

    post = db.get_post(123)

    assert post["id"] == 123
    assert post["platform"] == "linkedin"


def test_get_approved_posts(mock_db):
    """Test getting approved posts"""
    db, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = [
        {"id": 1, "status": "approved"},
        {"id": 2, "status": "approved"},
    ]

    posts = db.get_approved_posts(platform="linkedin")

    assert len(posts) == 2
    assert all(p["status"] == "approved" for p in posts)


def test_save_feedback(mock_db):
    """Test saving post feedback"""
    db, mock_cursor = mock_db

    db.save_feedback(
        post_id=123,
        feedback_type="approved_with_edits",
        edit_details={"changes": "minor edits"},
        created_by="user@example.com",
    )

    mock_cursor.execute.assert_called_once()


def test_save_performance_metrics(mock_db):
    """Test saving performance metrics"""
    db, mock_cursor = mock_db

    metrics = {
        "likes": 100,
        "comments": 20,
        "shares": 10,
        "impressions": 1000,
        "engagement_rate": 0.13,
    }

    db.save_performance_metrics(123, "linkedin", metrics)

    mock_cursor.execute.assert_called_once()


def test_context_manager(mock_db):
    """Test database context manager"""
    with patch("src.data.database.psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        with Database() as db:
            assert db is not None

        mock_conn.close.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
