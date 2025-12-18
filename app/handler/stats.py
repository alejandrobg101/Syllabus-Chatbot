# app/handler/stats.py

from flask import jsonify
from app.dao.stats import StatsDAO


class StatsHandler:
    def __init__(self):
        self.dao = StatsDAO()

    def top_classes_by_avg_duration(self, year=None, semester=None, limit=1):
        try:
            data = self.dao.top_classes_by_avg_duration(year, semester, limit)
            self.dao.close()
            return jsonify(data), 200
        except ValueError as e:
            self.dao.close()
            message = str(e)
            if message == "Invalid limit":
                return jsonify(Error=message), 409
            elif message == "Invalid Years Format":
                return jsonify(Error=message), 409
            else:
                return jsonify(Error=message), 400
        except Exception as e:
            self.dao.close()
            return jsonify(Error=str(e)), 500

    def classes_without_prereqs(self):
        try:
            data = self.dao.classes_without_prereqs()
            self.dao.close()
            return jsonify(data), 200
        except Exception as e:
            self.dao.close()
            return jsonify(Error=str(e)), 500

    def top_rooms_by_utilization(self, year=None, semester=None, limit=None):
        try:
            if year is not None:
                year_str = str(year).strip()
                if not (year_str.isdigit() and len(year_str) == 4):
                    return jsonify(Error="Invalid year: must be a 4-digit number"), 409
                year = year_str  # normalized

            if limit is None:
                limit = 5
            if not isinstance(limit, int):
                return jsonify(Error="Invalid limit: must be an integer"), 400
            if limit < 1 or limit > 10:
                return jsonify(Error="Invalid limit: must be between 1 and 10"), 409

            valid_semesters = {'Fall', 'Spring', 'V1', 'V2'}
            if semester and semester not in valid_semesters:
                return jsonify(Error="Invalid semester value"), 400

            data = self.dao.top_rooms_by_utilization(year, semester, limit)
            return jsonify(data), 200

        except Exception as e:
            return jsonify(Error=str(e)), 500
        finally:
            self.dao.close()

    def multi_room_classes(self, year=None, semester=None, limit=None, orderby=None):
        try:
            if year is not None:
                year_str = str(year).strip()
                if not (year_str.isdigit() and len(year_str) == 4):
                    return jsonify(Error="Invalid year: must be a 4-digit number"), 409
                year = year_str

            if limit is None:
                parsed_limit = 5
            else:
                if not isinstance(limit, int):
                    return jsonify(Error="limit must be an integer"), 400
                parsed_limit = limit

            if parsed_limit < 1 or parsed_limit > 10:
                return jsonify(Error="Invalid limit: must be between 1 and 10"), 409

            if orderby is None:
                orderby = "desc"
            orderby = orderby.lower()
            if orderby not in ("asc", "desc"):
                return jsonify(Error="orderby must be 'asc' or 'desc'"), 400

            data = self.dao.multi_room_classes(year, semester, parsed_limit, orderby)
            self.dao.close()
            return jsonify(data), 200

        except Exception as e:
            self.dao.close()
            return jsonify(Error=str(e)), 500

    def top_departments_by_sections(self, year=None, semester=None, limit=None):
        try:
            if year is not None:
                year_str = str(year).strip()
                if not (year_str.isdigit() and len(year_str) == 4):
                    return jsonify(Error="Invalid year: must be a 4-digit number"), 409
                year = year_str

            if limit is None:
                limit_value = 5
            else:
                if not isinstance(limit, int):
                    return jsonify(Error="limit must be an integer"), 400
                limit_value = limit

            if limit_value < 1 or limit_value > 10:
                return jsonify(Error="Invalid limit: must be between 1 and 10"), 409

            data = self.dao.top_departments_by_sections(year, semester, limit_value)
            self.dao.close()
            return jsonify(data), 200

        except Exception as e:
            self.dao.close()
            return jsonify(Error=str(e)), 500


        except Exception as e:
            self.dao.close()
            return jsonify(Error=str(e)), 500