
from app.config.dbconfig import pg_config
import psycopg2

class MeetingDAO:
    def __init__(self):
        connection_url = (
            f"dbname={pg_config['dbname']} "
            f"user={pg_config['user']} "
            f"password={pg_config['passwd']} "
            f"port={pg_config['port']} "
            f"host={pg_config.get('host', 'localhost')}"
        )
        self.conn = psycopg2._connect(connection_url)

    # --- Add this ---
    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()
    def get_all_meetings(self):
        cursor = self.conn.cursor()
        query = "SELECT * FROM meeting;"
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def get_ccodes(self):
        cursor = self.conn.cursor()
        query = "SELECT ccode FROM meeting;"
        cursor.execute(query)
        rows = cursor.fetchall()
        return [row[0] for row in rows]


    def create_meeting(self, ccode, starttime, endtime, cdays) -> int:
        """Insert meeting, return mid."""
        # Make sure the sequence is in sync before inserting
        self.sync_meeting_sequence()

        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO meeting (ccode, starttime, endtime, cdays)
                VALUES (%s, %s, %s, %s)
                RETURNING mid;
                """,
                (ccode, starttime, endtime, cdays)
            )
            mid = cursor.fetchone()[0]

        self.conn.commit()
        return mid

    def get_meeting(self, mid: int) -> dict | None:
        """Return meeting dict or None."""
        cursor = self.conn.cursor()
        query = "select mid, ccode, starttime, endtime, cdays from meeting where mid = %s;"
        cursor.execute(query, (mid,))
        result = cursor.fetchone()
        return result

    def update_meeting(self, mid: int, ccode, starttime, endtime, cdays) -> bool | None:
        """Update meeting, return updated dict."""
        cursor = self.conn.cursor()
        query = "update meeting set ccode = %s, starttime = %s, endtime = %s, cdays = %s where mid = %s;"
        cursor.execute(query, (ccode, starttime, endtime, cdays, mid))
        rowcount = cursor.rowcount
        self.conn.commit()
        return rowcount == 1

    def delete_meeting(self, mid: int) -> bool:
        """Delete meeting."""
        cursor = self.conn.cursor()
        query = "delete from meeting where mid = %s;"
        cursor.execute(query, (mid, ))
        rowcount = cursor.rowcount
        self.conn.commit()
        return rowcount == 1

    def check_FK_for_other_objetcs(self, mid):
        cursor = self.conn.cursor()
        query = "SELECT COUNT(*) FROM meeting NATURAL INNER JOIN section WHERE mid = %s;"
        cursor.execute(query, (mid,))
        count = cursor.fetchone()[0]
        return count != 0

    @staticmethod
    def sync_meeting_sequence():
        """Sync the meeting_mid_seq after imports to prevent duplicate key errors."""
        from app.dao.meeting import MeetingDAO
        dao = MeetingDAO()
        try:
            with dao.conn.cursor() as cur:
                cur.execute("""
                     SELECT setval(
                         pg_get_serial_sequence('meeting', 'mid'),
                         COALESCE((SELECT MAX(mid) FROM meeting), 0) + 1,
                         false
                     );
                 """)
                print("meeting_mid_seq synced to:", cur.fetchone()[0])
            dao.conn.commit()
        except Exception as e:
            print("Meeting sequence sync failed:", e)
        finally:
            dao.close()