from flask import jsonify
from app.dao.meeting import MeetingDAO
from datetime import datetime, time, date


def to_iso(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, time):
        # Time only → combine with today's date or a placeholder date
        return datetime.combine(date.today(), value).isoformat()
    return value
class MeetingHandler:

    def build_meeting_dict(self, row):
        result = {}
        result['mid'] = row[0]
        result['ccode'] = row[1]
        result['starttime'] = to_iso(row[2])
        result['endtime'] = to_iso(row[3])
        result['cdays'] = row[4]
        return result

    def build_meeting_attributes(self, mid, ccode, starttime, endtime, cdays):
        result = {}
        result['mid'] = mid
        result['ccode'] = ccode
        result['starttime'] = starttime
        result['endtime'] = endtime
        result['cdays'] = cdays
        return result

    def getMeetingById(self, mid):
        dao = MeetingDAO()
        row = dao.get_meeting(mid)
        if not row:
            return jsonify(Error = "Meeting Not Found"), 404
        else:
            meeting = self.build_meeting_dict(row)
            return jsonify(Meeting = meeting)

    def updateMeetingById (self, mid, meeting_json):
        dao = MeetingDAO()
        ccode = meeting_json["ccode"]
        starttime = datetime.fromisoformat(meeting_json["starttime"])
        endtime = datetime.fromisoformat(meeting_json["endtime"])
        cdays = meeting_json["cdays"]

        if mid and ccode and starttime and endtime and cdays:
            if starttime > endtime:
                return jsonify(Error="Time Conflict"), 409
            elif cdays not in ["MJ", "LMV"]:
                return jsonify(Error="Invalid cdays value"), 409
            elif ccode in dao.get_ccodes():
                return jsonify(Error="Duplicate ccode"), 409
            else:
                status = dao.update_meeting(mid, ccode, starttime, endtime, cdays)
                if status:
                    temp = (mid, ccode, starttime, endtime, cdays)
                    result = self.build_meeting_dict(temp)
                    return jsonify(result)
                else:
                    return jsonify(Error = "Meeting Not Found"), 404
        else:
            return jsonify(Error = "Invalid Request"), 400

    def deleteMeetingById(self, mid):
        dao = MeetingDAO()

        if not dao.get_meeting(mid):
            return jsonify(Error = "Meeting Not Found"), 404
        elif dao.check_FK_for_other_objetcs(mid):
            return jsonify(Error = "ForeignKey Conflict"), 409
        else:
            dao.delete_meeting(mid)
            return jsonify(DeleteStatus = "OK"), 204

    def createMeeting(self, meeting_json):
        dao = MeetingDAO()
        ccode = meeting_json["ccode"]
        starttime = datetime.fromisoformat(meeting_json["starttime"])
        endtime = datetime.fromisoformat(meeting_json["endtime"])
        cdays = meeting_json["cdays"]

        if not all([ccode, starttime, endtime, cdays]):
            dao.close()
            return jsonify(Error="Invalid Request"), 400

        if starttime >= endtime:
            dao.close()
            return jsonify(Error="Time Conflict"), 409
        if cdays not in ["MJ", "LMV"]:
            dao.close()
            return jsonify(Error="Invalid cdays value"), 409
        if ccode in dao.get_ccodes():
            dao.close()
            return jsonify(Error="Duplicate ccode"), 409

        mid = dao.create_meeting(ccode, starttime, endtime, cdays)
        result = self.build_meeting_dict((mid, ccode, starttime, endtime, cdays))
        dao.close()
        return jsonify(Meeting=result), 201
