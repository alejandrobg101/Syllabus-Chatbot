from app.config.dbconfig import pg_config
import psycopg2
from typing import List, Tuple, Optional


class ClassDAO:
    def __init__(self):
        connection_url = (
            f"dbname={pg_config['dbname']} "
            f"user={pg_config['user']} "
            f"password={pg_config['passwd']} "
            f"port={pg_config['port']} "
            f"host={pg_config.get('host', 'localhost')}"
        )
        self.conn = psycopg2.connect(connection_url)

    def get_ccodes(self) -> List[str]:
        with self.conn.cursor() as cur:
            cur.execute("SELECT ccode FROM class;")
            return [row[0] for row in cur.fetchall()]

    def create_class(self, cname, ccode, cdesc, term, years, cred, csyllabus) -> int:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO class (cname, ccode, cdesc, term, years, cred, csyllabus)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING cid;
                """,
                (cname, ccode, cdesc, term, years, cred, csyllabus)
            )
            cid = cur.fetchone()[0]
        self.conn.commit()
        return cid

    def get_class(self, cid: int) -> Optional[Tuple]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT cid, cname, ccode, cdesc, term, years, cred, csyllabus
                FROM class WHERE cid = %s;
                """,
                (cid,)
            )
            return cur.fetchone()

    def update_class(self, cid: int, cname, ccode, cdesc, term, years, cred, csyllabus) -> bool:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE class
                SET cname = %s, ccode = %s, cdesc = %s, term = %s,
                    years = %s, cred = %s, csyllabus = %s
                WHERE cid = %s;
                """,
                (cname, ccode, cdesc, term, years, cred, csyllabus, cid)
            )
            updated = cur.rowcount == 1
        self.conn.commit()
        return updated

    def delete_class(self, cid: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM class WHERE cid = %s;", (cid,))
            deleted = cur.rowcount == 1
        self.conn.commit()
        return deleted

    def check_referenced(self, cid: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM section WHERE cid = %s;", (cid,))
            sec_cnt = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM requisite WHERE reqid = %s;", (cid,))
            req_cnt = cur.fetchone()[0]
            return (sec_cnt + req_cnt) > 0

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()


def sync_all_sequences():
    """
    Syncs both room_rid_seq and class_cid_seq.
    Safe after data imports.
    """
    try:
        from app.dao.rooms import RoomDAO
        room_dao = RoomDAO()
        with room_dao.conn.cursor() as cur:
            cur.execute("""
                SELECT setval(
                    pg_get_serial_sequence('room', 'rid'),
                    COALESCE((SELECT MAX(rid) FROM room), 0) + 1,
                    false
                );
            """)
        room_dao.conn.commit()
        room_dao.close()
    except Exception as e:
        print("Room sequence sync failed:", e)

    try:
        class_dao = ClassDAO()
        with class_dao.conn.cursor() as cur:
            cur.execute("""
                SELECT setval(
                    pg_get_serial_sequence('class', 'cid'),
                    COALESCE((SELECT MAX(cid) FROM class), 0) + 1,
                    false
                );
            """)
        class_dao.conn.commit()
        class_dao.close()
    except Exception as e:
        print("Class sequence sync failed:", e)