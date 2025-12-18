# app/dao/stats.py

from app.config.dbconfig import pg_config
import psycopg2
from typing import List, Dict, Optional


class StatsDAO:
    def __init__(self):
        connection_url = "dbname=%s user=%s password=%s host=%s port=%s" % (
            pg_config['dbname'],
            pg_config['user'],
            pg_config['passwd'],
            pg_config['host'],
            pg_config['port']
        )
        self.conn = psycopg2.connect(connection_url)

    # ------------------------------------------------------------------
    # 1. Top classes by average meeting duration
    # ------------------------------------------------------------------
    def top_classes_by_avg_duration(
            self,
            year: Optional[str] = None,
            semester: Optional[str] = None,
            limit: int = 1
    ) -> List[Dict]:

        # --- Validate limit ---
        if limit < 1 or limit > 10:
            raise ValueError("Invalid limit")

        query = """
            SELECT
                c.cid,
                (c.cname::text || ' ' || c.ccode) AS fullcode,
                ROUND(AVG(EXTRACT(EPOCH FROM (m.endtime - m.starttime)) / 60), 1) AS avg_minutes
            FROM class c
            JOIN section s ON s.cid = c.cid
            JOIN meeting m ON s.mid = m.mid
            WHERE 1=1
        """
        params = []

        if year:
            query += " AND s.years = %s"
            params.append(year)
        if semester:
            query += " AND s.semester = %s"
            params.append(semester)

        query += """
            GROUP BY c.cid, c.ccode
            HAVING COUNT(m.mid) > 0
            ORDER BY avg_minutes DESC
            LIMIT %s
        """
        params.append(limit)

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

        # --- Handle empty results (invalid year/semester) ---
        if not rows:
            raise ValueError("Invalid Years Format")

        result = []
        for row in rows:
            result.append({
                "cid": row[0],
                "fullcode": row[1],
                "avg_minutes": float(row[2])
            })
        cursor.close()
        return result

    # ------------------------------------------------------------------
    # 2. Classes without prerequisites
    # ------------------------------------------------------------------
    def classes_without_prereqs(self) -> List[Dict]:
        query = """
            SELECT c.cid, c.ccode
            FROM class c
            LEFT JOIN requisite r ON r.classid = c.cid
            WHERE r.classid IS NULL
            ORDER BY c.ccode
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append({
                "cid": row[0],
                "fullcode": row[1]
            })
        cursor.close()
        return result


    # ------------------------------------------------------------------
    # 3. Top rooms by average utilization (capacity proxy)
    # ------------------------------------------------------------------

    def top_rooms_by_utilization(
            self,
            year: Optional[str] = None,
            semester: Optional[str] = None,
            limit: Optional[int] = None
    ) -> List[Dict]:
        """
        utilization = AVG(section.capacity / room.capacity)
        Optional filters: year, semester
        Optional limit: if provided
        """

        query = """
            SELECT
                r.rid,
                r.building,
                r.room_number,
                ROUND(
                    AVG(
                        CAST(s.capacity AS FLOAT)
                        / NULLIF(r.capacity, 0)
                    )::numeric,
                    2
                ) AS utilization
            FROM section s
            JOIN room r ON s.roomid = r.rid
            WHERE 1=1
        """
        params = []

        if year:
            query += " AND s.years = %s"
            params.append(year)

        if semester:
            query += " AND s.semester = %s"
            params.append(semester)

        query += """
            GROUP BY r.rid, r.building, r.room_number
            ORDER BY utilization DESC
        """

        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        result = [
            {
                "rid": row[0],
                "building": row[1],
                "room_number": row[2],
                "utilization": float(row[3]) if row[3] is not None else None
            }
            for row in rows
        ]
        cursor.close()
        return result

    # ------------------------------------------------------------------
    # 4. Multi-room classes (distinct rooms per class)
     # ------------------------------------------------------------------
    def multi_room_classes(
            self,
            year: Optional[str] = None,
            semester: Optional[str] = None,
            limit: Optional[int] = None,
            orderby: str = "desc"
    ) -> List[Dict]:
        """
        Returns classes that use more than one distinct room.
        Optional filters: year, semester.
        Optional limit: if provided (no limit otherwise)
        orderby: 'asc' or 'desc' on distinct_rooms.
        """

        order_dir = "ASC" if (orderby and orderby.lower() == "asc") else "DESC"

        query = """
            SELECT
                c.cid,
                (c.cname::text || ' ' || c.ccode) AS fullcode,
                COUNT(DISTINCT s.roomid) AS distinct_rooms
            FROM class c
            JOIN section s ON s.cid = c.cid
            WHERE 1=1
        """
        params = []

        if year:
            query += " AND s.years = %s"
            params.append(year)

        if semester:
            query += " AND s.semester = %s"
            params.append(semester)

        query += f"""
            GROUP BY c.cid, c.ccode, c.cname
            HAVING COUNT(DISTINCT s.roomid) > 1
            ORDER BY distinct_rooms {order_dir}, c.ccode
        """

        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()

        result = [
            {
                "cid": row[0],
                "fullcode": row[1],
                "distinct_rooms": row[2]
            }
            for row in rows
        ]
        return result

    # ------------------------------------------------------------------
    # 5. Top departments by sections (from class.cname)
    # ------------------------------------------------------------------
    def top_departments_by_sections(
            self,
            year: Optional[str] = None,
            semester: Optional[str] = None,
            limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Returns top departments (from class.cname) by number of sections.
        Optional filters: year, semester.
        Optional limit: default None (no limit), capped at 5 if given.
        """

        query = """
            SELECT
                c.cname AS dept_code,
                COUNT(*) AS sections
            FROM class c
            JOIN section s ON s.cid = c.cid
            WHERE 1=1
        """
        params = []

        if year:
            query += " AND s.years = %s"
            params.append(year)

        if semester:
            query += " AND s.semester = %s"
            params.append(semester)

        query += """
            GROUP BY c.cname
            ORDER BY sections DESC, dept_code
        """

        # Only add LIMIT if explicitly provided
        if limit is not None:
            limit = min(max(limit, 1), 5)
            query += " LIMIT %s"
            params.append(limit)

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()

        result = [
            {
                "fullcode": row[0],
                "sections": row[1]
            }
            for row in rows
        ]
        return result

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()