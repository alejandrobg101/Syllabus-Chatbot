# app/handler/rooms.py
from flask import jsonify
from app.dao.rooms import RoomDAO


class RoomHandler:
    def build_room_dict(self, row):
        return {
            "rid": row[0],
            "building": row[1],
            "room_number": row[2],
            "capacity": row[3],
        }

    def getRoomById(self, rid):
        dao = RoomDAO()
        row = dao.get_room(rid)
        if not row:
            return jsonify(Error="Room Not Found"), 404
        return jsonify(Room=self.build_room_dict(row))

    def createRoom(self, room_json):
        dao = RoomDAO()

        required = ["building", "room_number", "capacity"]
        if not all(k in room_json for k in required):
            return jsonify(Error="Missing required fields"), 400

        building = room_json["building"]
        room_number = room_json["room_number"]
        capacity = room_json["capacity"]

        if not building or not room_number:
            return jsonify(Error="building and room_number cannot be empty"), 400

        if not isinstance(capacity, int) or capacity < 0:
            return jsonify(Error="capacity must be a non-negative integer"), 400

        if (building, room_number) in dao.get_room_locations():
            return jsonify(Error="Room (building, room_number) already exists"), 409

        rid = dao.create_room(building, room_number, capacity)
        result = self.build_room_dict((rid, building, room_number, capacity))
        dao.close()
        return jsonify(Room=result), 201   # ← Antes solo {rid: X}

    def updateRoomById(self, rid, room_json):
        dao = RoomDAO()
        current_row = dao.get_room(rid)
        if not current_row:
            return jsonify(Error="Room Not Found"), 404

        cur = self.build_room_dict(current_row)
        building = room_json.get("building", cur["building"])
        room_number = room_json.get("room_number", cur["room_number"])
        capacity = room_json.get("capacity", cur["capacity"])

        if not building or not room_number:
            return jsonify(Error="building and room_number cannot be empty"), 400

        if not isinstance(capacity, int) or capacity < 0:
            return jsonify(Error="capacity must be a non-negative integer"), 400

        new_pair = (building, room_number)
        old_pair = (cur["building"], cur["room_number"])
        if new_pair != old_pair and new_pair in dao.get_room_locations():
            return jsonify(Error="Room (building, room_number) already exists"), 409

        ok = dao.update_room(rid, building, room_number, capacity)
        if not ok:
            return jsonify(Error="Update failed"), 500

        updated = self.build_room_dict((rid, building, room_number, capacity))
        return jsonify(Room=updated)

    def deleteRoomById(self, rid):
        dao = RoomDAO()
        if not dao.get_room(rid):
            return jsonify(Error="Room Not Found"), 404

        if dao.is_referenced(rid):
            return jsonify(Error="Foreign Key Conflict – referenced by a section"), 409

        dao.delete_room(rid)
        return jsonify(DeleteStatus="OK"), 204