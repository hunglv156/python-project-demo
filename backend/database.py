import psycopg2
import psycopg2.extras
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from typing import Generator, Dict, Any, List
import logging
from .config import settings

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.pool = None
    
    def connect(self):
        """Tạo connection pool"""
        try:
            self.pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=settings.get_database_url()
            )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Error creating database connection pool: {e}")
            raise
    
    def close(self):
        """Đóng connection pool"""
        if self.pool:
            self.pool.closeall()
            logger.info("Database connection pool closed")
    
    @contextmanager
    def get_connection(self):
        """Context manager để lấy connection từ pool"""
        conn = None
        try:
            conn = self.pool.getconn()
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                self.pool.putconn(conn)
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Thực thi query và trả về kết quả"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                conn.commit()
                return []
    
    def execute_many(self, query: str, params_list: List[tuple]) -> None:
        """Thực thi nhiều query cùng lúc"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.executemany(query, params_list)
                conn.commit()
    
    def execute_single(self, query: str, params: tuple = None) -> Dict[str, Any]:
        """Thực thi query và trả về 1 kết quả"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                logger.info(f"Executing query: {query}")
                logger.info(f"With params: {params}")
                cursor.execute(query, params)
                if query.strip().upper().startswith('SELECT'):
                    result = cursor.fetchone()
                    logger.info(f"SELECT result: {result}")
                    return result
                elif query.strip().upper().startswith('INSERT'):
                    conn.commit()
                    # For INSERT with RETURNING, fetch the result
                    if 'RETURNING' in query.upper():
                        result = cursor.fetchone()
                        logger.info(f"INSERT RETURNING result: {result}")
                        return result
                    else:
                        logger.info("INSERT without RETURNING")
                        return {}
                else:
                    conn.commit()
                    logger.info("Other query executed")
                    return {}

# Global database instance
db = Database() 