from flask import jsonify
from app.dao.section import SectionDAO


class SectionHandler:

    def build_section_dict(self, row):
        result = {}
        result['sid'] = row[0]
        result['cid'] = row[1]
        result['mid'] = row[2]
        result['roomid'] = row[3]
        result['semester'] = row[4]
        result['years'] = row[5]
        result['capacity'] = row[6]
        return result

    def build_section_attributes(self, sid, cid, mid, roomid, semester, years, capacity):
        result = {}
        result['sid'] = sid
        result['cid'] = cid
        result['mid'] = mid
        result['roomid'] = roomid
        result['semester'] = semester
        result['years'] = years
        result['capacity'] = capacity
        return result

    def getSectionById(self, sid):
        dao = SectionDAO()
        row = dao.get_section(sid)
        if not row:
            return jsonify(Error="Section Not Found"), 404
        section = self.build_section_dict(row)
        return jsonify(Section=section)

    def createSection(self, section_json):
        dao = SectionDAO()

        cid = section_json["cid"]
        mid = section_json["mid"]
        roomid = section_json["roomid"]
        semester = section_json["semester"]
        semester = semester[0].upper() + semester[1:].lower()
        years = section_json["years"]
        capacity = section_json["capacity"]

        # Foreign key checks
        if cid not in dao.check_cid_existence(cid) or \
           roomid not in dao.check_roomid_existence(roomid) or \
           mid not in dao.check_mid_existence(mid):
            return jsonify(Error="Foreign Key does not exist"), 409

        # Capacity check (fixed logic)
        elif not dao.check_capacity(roomid, capacity):
            return jsonify(Error="Over room capacity"), 409

        # Semester and years validation
        elif semester not in ["Fall", "Spring", "V1", "V2"] or not (years.isdigit() and len(years) == 4):
            return jsonify(Error="Invalid Semester or Years Format"), 409

        # Scheduling conflict check (pass 0 for new section)
        elif not dao.check_scheduling_conflict(0, roomid, mid, semester, years):
            return jsonify(Error="Scheduling Conflict"), 409

        else:
            sid = dao.create_section(roomid, cid, mid, semester, years, capacity)
            row = dao.get_section(sid)
            result = self.build_section_dict(row)
            dao.close()
            return jsonify(Section=result), 201  # ← antes solo {Sid: X}

    def updateSectionById(self, sid, section_json):
        dao = SectionDAO()

        cid = section_json["cid"]
        mid = section_json["mid"]
        roomid = section_json["roomid"]
        semester = section_json["semester"]
        semester = semester[0].upper() + semester[1:].lower()
        years = section_json["years"]
        capacity = section_json["capacity"]

        # Foreign key checks
        if cid not in dao.check_cid_existence(cid) or \
           roomid not in dao.check_roomid_existence(roomid) or \
           mid not in dao.check_mid_existence(mid):
            return jsonify(Error="Foreign Key does not exist"), 409

        # Capacity check
        elif not dao.check_capacity(roomid, capacity):
            return jsonify(Error="Over room capacity"), 409

        # Semester and years validation
        elif semester not in ["Fall", "Spring", "V1", "V2"] or not (years.isdigit() and len(years) == 4):
            return jsonify(Error="Invalid Semester or Years Format"), 409

        # Scheduling conflict check
        elif not dao.check_scheduling_conflict(sid, roomid, mid, semester, years):
            return jsonify(Error="Scheduling Conflict"), 409

        else:
            ok = dao.update_section(sid, roomid, cid, mid, semester, years, capacity)
            if ok:
                row = dao.get_section(sid)
                result = self.build_section_dict(row)
                dao.close()
                return jsonify(Section=result), 200  # ← antes {UpdateStatus: True}
            else:
                dao.close()
                return jsonify(Error="Update failed"), 500

    def deleteSectionById(self, sid):
        dao = SectionDAO()
        if not dao.get_section(sid):
            return jsonify(Error="Section Not Found"), 404
        dao.delete_section(sid)
        return jsonify(DeleteStatus="OK"), 204

    def getStatSectionsByDay(self, year, semester):
        dao = SectionDAO()

        if semester is not None and semester.strip().title() not in ["Fall", "Spring", "V1", "V2"]:
            return jsonify(Error="Invalid Semester"), 400
        elif year is not None and (not year.isdigit() or len(year) != 4):
            return jsonify(Error="Invalid Years Format"), 400

        year_val = year if year is not None else None
        semester_val = semester.strip().title() if semester is not None else None

        return jsonify(dao.get_stat_section_by_day(year_val, semester_val))
