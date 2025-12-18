from app.config.dbconfig import pg_config
import psycopg2
from typing import Set, Tuple, Optional


class RoomDAO:
    def __init__(self):
        connection_url = (
            f"dbname={pg_config['dbname']} "
            f"user={pg_config['user']} "
            f"password={pg_config['passwd']} "
            f"port={pg_config['port']} "
            f"host={pg_config.get('host', 'localhost')}"
        )
        self.conn = psycopg2.connect(connection_url)

    def get_room_locations(self) -> Set[Tuple[str, str]]:
        with self.conn.cursor() as cur:
            cur.execute("SELECT building, room_number FROM room;")
            return {(row[0], row[1]) for row in cur.fetchall()}

    def create_room(self, building: str, room_number: str, capacity: int) -> int:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO room (building, room_number, capacity)
                VALUES (%s, %s, %s)
                RETURNING rid;
                """,
                (building, room_number, capacity),
            )
            rid = cur.fetchone()[0]
        self.conn.commit()
        return rid

    def get_room(self, rid: int) -> Optional[Tuple]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT rid, building, room_number, capacity
                FROM room
                WHERE rid = %s;
                """,
                (rid,),
            )
            return cur.fetchone()

    def update_room(self, rid: int, building: str, room_number: str, capacity: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE room
                SET building = %s, room_number = %s, capacity = %s
                WHERE rid = %s;
                """,
                (building, room_number, capacity, rid),
            )
            updated = cur.rowcount == 1
        self.conn.commit()
        return updated

    def delete_room(self, rid: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM room WHERE rid = %s;", (rid,))
            deleted = cur.rowcount == 1
        self.conn.commit()
        return deleted

    def is_referenced(self, rid: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM section WHERE roomid = %s;", (rid,))
            return cur.fetchone()[0] > 0

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()


# GLOBAL SYNC FUNCTION — CALL ONCE
def sync_all_sequences():
    dao = RoomDAO()
    try:
        with dao.conn.cursor() as cur:
            cur.execute("""
                SELECT setval(
                    pg_get_serial_sequence('room', 'rid'),
                    COALESCE((SELECT MAX(rid) FROM room), 0) + 1,
                    false
                );
            """)
        dao.conn.commit()
    except Exception as e:
        print("Sequence sync failed:", e)
    finally:
        dao.close()