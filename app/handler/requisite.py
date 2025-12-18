from flask import jsonify
from app.dao.requisite import RequisiteDAO

class RequisiteHandler:

    def build_requisite_dict(self, row):
        result = {}
        result['reqid'] = row[0]
        result['classid'] = row[1]
        result['prereq'] = row[2]
        return result

    def build_requisite_attributes(self, reqid, classid, prereq):
        result = {}
        result['reqid'] = reqid
        result['classid'] = classid
        result['prereq'] = prereq
        return result

    def getRequisiteById(self, classid, reqid):
        dao = RequisiteDAO()
        row = dao.get_requisite(classid, reqid)
        if not row:
            return jsonify(Error="Requisite Not Found"), 404
        else:
            requisite = self.build_requisite_dict(row)
            return jsonify(Requisite=requisite)

    def deleteRequisiteById(self, classid, reqid):
        dao = RequisiteDAO()
        if dao.delete_requisite(classid, reqid):
            return jsonify(DeleteStatus="OK"), 204
        else:
            return jsonify(Error="Requisite Not Found"), 404


    def createRequisite(self, section_json):
        dao = RequisiteDAO()
        classid = section_json["classid"]
        reqid = section_json["reqid"]
        prereq = section_json["prereq"]

        if not dao.check_classid(classid) or not dao.check_classid(reqid):
            return jsonify(Error="ForeignKey does not exist"), 409
        elif dao.check_duplicated(classid, reqid):
            return jsonify(Error="Duplicate Requisite"), 409
        elif classid == reqid:
            return jsonify(Error="Self Requisite Not Allowed"), 409
        elif prereq == True and dao.check_requisite_cycle(classid, reqid):
            return jsonify(Error="Requisite Cycle Not Allowed"), 409
        else:
            row = dao.create_requisite(classid, reqid, prereq)
            result = self.build_requisite_dict(row)
        dao.close()
        return jsonify(Requisite=result), 201