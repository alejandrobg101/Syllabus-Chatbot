from app.config.dbconfig import pg_config
import psycopg2

class SectionDAO:
    def __init__(self):
        connection_url = (
            f"dbname={pg_config['dbname']} "
            f"user={pg_config['user']} "
            f"password={pg_config['passwd']} "
            f"port={pg_config['port']} "
            f"host={pg_config.get('host', 'localhost')}"
        )
        self.conn = psycopg2._connect(connection_url)

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()
    def get_all_sections(self):
        """Return all sections."""
        cursor = self.conn.cursor()
        query = "SELECT * FROM section;"
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result


    def create_section(self, roomid, cid, mid, semester, years, capacity) -> int:
        """Insert section, return sid. Validate FKs, capacity, time conflicts."""
        cursor = self.conn.cursor()
        query = "INSERT INTO section (roomid, cid, mid, semester, years, capacity) VALUES (%s, %s, %s, %s, %s, %s) returning *;"
        cursor.execute(query, (roomid, cid, mid, semester, years, capacity,))
        sid = cursor.fetchone()[0]
        self.conn.commit()
        return sid

    def get_section(self, sid: int) -> dict | None:
        """Return section dict or None."""
        cursor = self.conn.cursor()
        query = "select sid, cid, mid, roomid, semester, years, capacity from section where sid = %s;"
        cursor.execute(query, (sid,))
        result = cursor.fetchone()
        return result

    def update_section(self, sid, roomid, cid, mid, semester, years, capacity) -> bool | None:
        """Update section. Re-check conflicts."""
        cursor = self.conn.cursor()
        query = "update section set cid = %s, mid = %s, roomid = %s, semester = %s, years = %s, capacity = %s where sid = %s;"
        cursor.execute(query, (cid, mid, roomid, semester, years, capacity, sid,))
        rowcount = cursor.rowcount
        self.conn.commit()
        return rowcount == 1

    def delete_section(self, sid: int) -> None:
        """Delete section."""
        cursor = self.conn.cursor()
        query = "delete from section where sid = %s;"
        cursor.execute(query, (sid,))
        rowcount = cursor.rowcount
        self.conn.commit()
        return rowcount == 1

    def check_mid_existence(self, mid):
        cursor = self.conn.cursor()
        query = "select mid from meeting;"
        cursor.execute(query, (mid,))
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    def check_roomid_existence(self, roomid):
        cursor = self.conn.cursor()
        query = "select rid from room;"
        cursor.execute(query, (roomid,))
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    def check_cid_existence(self, cid):
        cursor = self.conn.cursor()
        query = "select cid from class;"
        cursor.execute(query, (cid,))
        rows = cursor.fetchall()
        return [row[0] for row in rows]

    def check_capacity(self, roomid, capacity):
        cursor = self.conn.cursor()
        query = "SELECT capacity FROM room WHERE rid = %s;"
        cursor.execute(query, (roomid,))
        row = cursor.fetchone()
        if row is None:
            return False
        elif int(capacity) > int(row[0]):
            return False
        else:
            return True

    def check_scheduling_conflict(self, sid, roomid, mid, semester, years):
        cursor = self.conn.cursor()
        query = """
            SELECT * FROM section
            NATURAL INNER JOIN meeting
            WHERE sid != %s
              AND roomid = %s
              AND cdays = (SELECT cdays FROM meeting WHERE mid = %s)
              AND section.semester = %s
              AND section.years = %s;
        """

        cursor.execute(query, (sid, roomid,mid,semester, years,))
        result = []
        for row in cursor:
            result.append(row)
        if len(result) > 0:
            return False
        else:
            return True

    def get_stat_section_by_day(self, year, semester):
        cursor = self.conn.cursor()
        if semester is not None:
            semester = semester.strip().title()
        query = "select cdays from section natural inner join meeting WHERE (%s IS NULL OR section.years = %s) AND (%s IS NULL OR section.semester = %s);"
        cursor.execute(query, (year, year, semester,semester,))
        result = []
        for row in cursor:
            result.append(row)

        sectionL = 0
        sectionM = 0
        sectionW = 0
        sectionJ = 0
        sectionV = 0
        sectionS = 0
        sectionD = 0

        for row in result:
            cdays = row[0]  # 'MJ', 'LWV', etc.
            if cdays == 'MJ':
                sectionM += 1
                sectionJ += 1
            elif cdays == 'LWV':
                sectionL += 1
                sectionW += 1
                sectionV += 1

        return [
            {"day": "L", "sections": sectionL},
            {"day": "M", "sections": sectionM},
            {"day": "W", "sections": sectionW},
            {"day": "J", "sections": sectionJ},
            {"day": "V", "sections": sectionV},
            {"day": "S", "sections": sectionS},
            {"day": "D", "sections": sectionD}
        ]