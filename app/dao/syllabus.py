from app.config.dbconfig import pg_config
import psycopg2
from typing import List, Tuple
import os


class SyllabusDAO:
    def __init__(self):
        if os.environ.get("DATABASE_URL"):
            self.conn = psycopg2.connect(os.environ["DATABASE_URL"], sslmode="require")
        else:
            connection_url = (
                f"dbname={pg_config['dbname']} user={pg_config['user']} "
                f"password={pg_config['passwd']} port={pg_config['port']} "
                f"host={pg_config.get('host', 'localhost')}"
            )
            self.conn = psycopg2.connect(connection_url)

        with self.conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        self.conn.commit()

    def insert_chunk(self, courseid: int, chunk: str, embedding: List[float]) -> None:
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO syllabus (courseid, chunk, embedding_text)
                VALUES (%s, %s, %s::vector)
                """,
                (courseid, chunk, embedding_str),
            )
        self.conn.commit()

    def get_relevant_chunks(
        self, query_embedding: List[float], courseid: int = None, limit: int = 15
    ) -> List[Tuple[str, int]]:
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        with self.conn.cursor() as cur:
            if courseid:
                cur.execute(
                    """
                    SELECT chunk, courseid
                    FROM syllabus
                    WHERE courseid = %s
                    ORDER BY embedding_text <-> %s::vector
                    LIMIT %s
                    """,
                    (courseid, embedding_str, limit),
                )
            else:
                cur.execute(
                    """
                    SELECT chunk, courseid
                    FROM syllabus
                    ORDER BY embedding_text <-> %s::vector
                    LIMIT %s
                    """,
                    (embedding_str, limit),
                )
            return cur.fetchall()

    def find_course(self, cname: str = None, ccode: str = None, cdesc: str = None) -> int:
        with self.conn.cursor() as cur:
            if cname and ccode:
                cur.execute(
                    "SELECT cid FROM class WHERE cname = %s AND ccode = %s LIMIT 1",
                    (cname.upper(), ccode),
                )
            elif cdesc:
                cur.execute(
                    "SELECT cid FROM class WHERE LOWER(cdesc) LIKE LOWER(%s) LIMIT 1",
                    (f"%{cdesc}%",),
                )
            else:
                return None
            result = cur.fetchone()
            return result[0] if result else None

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()
