from app.config.dbconfig import pg_config
import psycopg2

class RequisiteDAO:
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

    def create_requisite(self, classid, reqid, prereq) -> None:
        """Insert (classid, reqid). Validate FKs, no self, no dup, no A↔B cycle."""
        cursor = self.conn.cursor()
        query = "INSERT INTO requisite (classid, reqid, prereq) VALUES (%s, %s, %s) returning *;"
        cursor.execute(query, (classid, reqid, prereq,))
        result = cursor.fetchone()
        self.conn.commit()
        return result

    def get_requisite(self, classid: int, reqid: int) -> dict | None:
        """Return requisite row or None."""
        cursor = self.conn.cursor()
        query = "select reqid, classid, prereq from requisite where classid = %s and reqid = %s;"
        cursor.execute(query, (classid,reqid,))
        result = cursor.fetchone()
        return result

    def update_requisite(self, classid: int, reqid: int, data: dict) -> dict | None:
        """Update requisite row, return updated row."""

    def delete_requisite(self, classid: int, reqid: int) -> None:
        """Delete requisite pair."""
        cursor = self.conn.cursor()
        query = "delete from requisite where classid = %s and reqid = %s;"
        cursor.execute(query, (classid,reqid,))
        rowcount = cursor.rowcount
        self.conn.commit()
        return rowcount == 1

    def check_classid(self, classid):
        cursor = self.conn.cursor()
        query = "select count(*) from class where cid = %s;"
        cursor.execute(query, (classid,))
        count = cursor.fetchone()[0]
        return count > 0

    def check_duplicated(self, classid, reqid):
        cursor = self.conn.cursor()
        query = "select count(*) from requisite where classid = %s and reqid = %s;"
        cursor.execute(query, (classid,reqid, ))
        count = cursor.fetchone()[0]
        return count > 0

    def check_requisite_cycle(self, classid, reqid):
        cursor = self.conn.cursor()
        query = "select count(*) from requisite where classid = %s and reqid = %s and prereq = true;"
        cursor.execute(query, (reqid, classid,))
        count = cursor.fetchone()[0]
        return count > 0