from flask import jsonify
from app.dao.classes import ClassDAO


class ClassHandler:
    def build_class_dict(self, row):
        return {
            "cid": row[0],
            "cname": row[1],
            "ccode": row[2],
            "cdesc": row[3],
            "term": row[4],
            "years": row[5],
            "cred": row[6],
            "csyllabus": row[7],
        }

    def getClassById(self, cid):
        dao = ClassDAO()
        row = dao.get_class(cid)
        dao.close()
        if not row:
            return jsonify(Error="Class Not Found"), 404
        return jsonify(Class=self.build_class_dict(row))

    def createClass(self, class_json):
        dao = ClassDAO()

        required = ["cname", "ccode", "cdesc", "term", "years", "cred", "csyllabus"]
        if not all(k in class_json for k in required):
            dao.close()
            return jsonify(Error="Invalid Request – missing fields"), 400

        cname = class_json["cname"]
        ccode = class_json["ccode"]
        cdesc = class_json["cdesc"]
        term = class_json["term"]
        years = class_json["years"]
        cred = class_json["cred"]
        csyllabus = class_json["csyllabus"]

        if not ccode:
            dao.close()
            return jsonify(Error="ccode cannot be empty"), 409
        if term not in {"First Semester", "Second Semester", "According to Demand"}:
            dao.close()
            return jsonify(Error="Invalid term value"), 409
        if years not in {"Every Year", "According to Demand", "Odd Years"}:
            dao.close()
            return jsonify(Error="Invalid years value"), 409
        if not isinstance(cred, int) or cred < 0:
            dao.close()
            return jsonify(Error="cred must be a non-negative integer"), 409
        if ccode in dao.get_ccodes():
            dao.close()
            return jsonify(Error="Duplicate ccode"), 409

        cid = dao.create_class(cname, ccode, cdesc, term, years, cred, csyllabus)

        result = self.build_class_dict((cid, cname, ccode, cdesc, term, years, cred, csyllabus))
        dao.close()
        return jsonify(Class=result), 201
    def updateClassById(self, cid, class_json):
        dao = ClassDAO()
        current_row = dao.get_class(cid)
        if not current_row:
            dao.close()
            return jsonify(Error="Class Not Found"), 404

        cur = self.build_class_dict(current_row)

        cname = class_json.get("cname", cur["cname"])
        ccode = class_json.get("ccode", cur["ccode"])
        cdesc = class_json.get("cdesc", cur["cdesc"])
        term = class_json.get("term", cur["term"])
        years = class_json.get("years", cur["years"])
        cred = class_json.get("cred", cur["cred"])
        csyllabus = class_json.get("csyllabus", cur["csyllabus"])

        if not ccode:
            dao.close()
            return jsonify(Error="ccode cannot be empty"), 409

        if term not in {"First Semester", "Second Semester", "According to Demand"}:
            dao.close()
            return jsonify(Error="Invalid term value"), 409

        if years not in {"Every Year", "According to Demand", "Odd Years"}:
            dao.close()
            return jsonify(Error="Invalid years value"), 409

        if not isinstance(cred, int) or cred < 0:
            dao.close()
            return jsonify(Error="cred must be a non-negative integer"), 409

        all_ccodes = dao.get_ccodes()
        if ccode != cur["ccode"] and ccode in all_ccodes:
            dao.close()
            return jsonify(Error="Duplicate ccode"), 409

        ok = dao.update_class(cid, cname, ccode, cdesc, term, years, cred, csyllabus)
        dao.close()
        if not ok:
            return jsonify(Error="Update failed"), 500

        updated = self.build_class_dict(
            (cid, cname, ccode, cdesc, term, years, cred, csyllabus)
        )
        return jsonify(Class=updated), 201

    def deleteClassById(self, cid):
        dao = ClassDAO()
        if not dao.get_class(cid):
            dao.close()
            return jsonify(Error="Class Not Found"), 404

        if dao.check_referenced(cid):
            dao.close()
            return jsonify(Error="Foreign Key Conflict – referenced by section or requisite"), 409

        dao.delete_class(cid)
        dao.close()
        return jsonify(DeleteStatus="OK"), 204