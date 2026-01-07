"""
Database interface for the social media generator.
Handles all database operations using PostgreSQL.
"""

import psycopg2
from psycopg2.extras import RealDictCursor, Json
from typing import Dict, List, Optional
from datetime import datetime

from ..core.config import Config


class Database:
    """Database interface for the social media generator"""

    def __init__(self):
        """Initialize database connection"""
        self.conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            cursor_factory=RealDictCursor,
        )

    def save_post(
        self,
        user_prompt: str,
        platform: str,
        content: str,
        image_path: str,
        image_prompt: str,
        status: str = "draft",
        human_edits: Optional[str] = None,
        generated_content: Optional[str] = None,
        jira_issue_key: Optional[str] = None,
    ) -> int:
        """
        Save a generated post to the database.
        Returns the post ID.
        """
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO generated_posts
                (user_prompt, platform, generated_content, final_content,
                 image_url, image_prompt, status, human_edits, jira_issue_key)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """,
                (
                    user_prompt,
                    platform,
                    generated_content or content,
                    content,
                    image_path,
                    image_prompt,
                    status,
                    human_edits,
                    jira_issue_key,
                ),
            )

            post_id = cur.fetchone()["id"]
            self.conn.commit()

            return post_id

    def save_feedback(
        self,
        post_id: int,
        feedback_type: str,
        edit_details: Optional[Dict] = None,
        rejection_reason: Optional[str] = None,
        created_by: str = "system",
    ):
        """Save feedback on a post"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO post_feedback
                (post_id, feedback_type, edit_details, rejection_reason, created_by)
                VALUES (%s, %s, %s, %s, %s)
            """,
                (
                    post_id,
                    feedback_type,
                    Json(edit_details) if edit_details else None,
                    rejection_reason,
                    created_by,
                ),
            )

            self.conn.commit()

    def update_post_status(self, post_id: int, status: str):
        """Update the status of a post"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE generated_posts
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """,
                (status, post_id),
            )

            self.conn.commit()

    def get_post(self, post_id: int) -> Optional[Dict]:
        """Retrieve a post by ID"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM generated_posts WHERE id = %s
            """,
                (post_id,),
            )

            return cur.fetchone()

    def get_posts(
        self, platform: Optional[str] = None, status: Optional[str] = None, limit: int = 50
    ) -> List[Dict]:
        """Get posts with optional filters"""
        with self.conn.cursor() as cur:
            query = "SELECT * FROM generated_posts WHERE 1=1"
            params: list[str | int] = []

            if platform:
                query += " AND platform = %s"
                params.append(platform)

            if status:
                query += " AND status = %s"
                params.append(status)

            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)

            cur.execute(query, params)
            return cur.fetchall()

    def get_approved_posts(self, platform: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get approved posts, optionally filtered by platform"""
        return self.get_posts(platform=platform, status="approved", limit=limit)

    def save_performance_metrics(self, post_id: int, platform: str, metrics: Dict):
        """Save performance metrics from platform"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO performance_metrics
                (post_id, platform, likes, comments, shares,
                 impressions, clicks, engagement_rate)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    post_id,
                    platform,
                    metrics.get("likes", 0),
                    metrics.get("comments", 0),
                    metrics.get("shares", 0),
                    metrics.get("impressions", 0),
                    metrics.get("clicks", 0),
                    metrics.get("engagement_rate", 0.0),
                ),
            )

            self.conn.commit()

    def get_best_performing_posts(
        self, platform: Optional[str] = None, limit: int = 10
    ) -> List[Dict]:
        """Get top performing posts by engagement rate"""
        with self.conn.cursor() as cur:
            query = """
                SELECT
                    gp.*,
                    pm.engagement_rate,
                    pm.likes,
                    pm.comments,
                    pm.shares
                FROM generated_posts gp
                JOIN performance_metrics pm ON gp.id = pm.post_id
                WHERE gp.status = 'published'
            """
            params: list[str | int] = []

            if platform:
                query += " AND gp.platform = %s"
                params.append(platform)

            query += " ORDER BY pm.engagement_rate DESC LIMIT %s"
            params.append(limit)

            cur.execute(query, params)
            return cur.fetchall()

    def get_analytics_summary(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """Get summary analytics"""
        with self.conn.cursor() as cur:
            query = """
                SELECT
                    COUNT(*) as total_posts,
                    COUNT(CASE WHEN status = 'published' THEN 1 END) as published,
                    COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved,
                    COUNT(CASE WHEN status = 'rejected' THEN 1 END) as rejected,
                    platform,
                    AVG(CASE
                        WHEN generated_content IS NOT NULL AND final_content IS NOT NULL
                        THEN 1
                        ELSE 0
                    END) as edit_rate
                FROM generated_posts
            """
            params = []

            if start_date:
                query += " WHERE created_at >= %s"
                params.append(start_date)

                if end_date:
                    query += " AND created_at <= %s"
                    params.append(end_date)
            elif end_date:
                query += " WHERE created_at <= %s"
                params.append(end_date)

            query += " GROUP BY platform"

            cur.execute(query, params)
            return cur.fetchall()

    def save_quality_check(
        self,
        post_id: int,
        check_type: str,
        passed: bool,
        score: float,
        details: Optional[Dict] = None,
    ):
        """Save quality check results"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO quality_checks
                (post_id, check_type, passed, score, details)
                VALUES (%s, %s, %s, %s, %s)
            """,
                (post_id, check_type, passed, score, Json(details) if details else None),
            )

            self.conn.commit()

    def log_publishing_attempt(
        self,
        post_id: int,
        platform: str,
        status: str,
        platform_post_id: Optional[str] = None,
        error_message: Optional[str] = None,
        attempts: int = 1,
    ):
        """Log a publishing attempt"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO publishing_log
                (post_id, platform, platform_post_id, status, error_message, attempts)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (post_id, platform, platform_post_id, status, error_message, attempts),
            )

            self.conn.commit()

    def close(self):
        """Close database connection"""
        self.conn.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
