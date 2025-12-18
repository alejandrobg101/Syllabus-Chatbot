from flask import Flask, jsonify, request, Blueprint

from app.handler.meeting import MeetingHandler
from app.handler.section import SectionHandler
from app.handler.requisite import RequisiteHandler
from app.handler.classes import ClassHandler
from app.handler.rooms import RoomHandler
from app.handler.stats import StatsHandler

# Cross-Origin Resource Sharing
from flask_cors import CORS, cross_origin

# DB sync function
from app.dao.classes import sync_all_sequences

#Chatbot
from app.llm.chatollama import ChatOllamaBot

# Initialize Flask
app = Flask(__name__)
CORS(app)

api = Blueprint('api', __name__, url_prefix='/api')

# Sync sequences at startup
sync_all_sequences()

#Chatbot call
chatbot = ChatOllamaBot()

@api.route('/')
def greeting():
    return 'Hello, this is the project JAC DB Project App!'


# -------------------- MEETING --------------------
@api.route('/meeting/<int:mid>', methods=['GET', 'PUT', 'DELETE'])
def getMeetingById(mid):
    handler = MeetingHandler()
    if request.method == 'GET':
        return handler.getMeetingById(mid)
    elif request.method == 'PUT':
        return handler.updateMeetingById(mid, request.json)
    elif request.method == 'DELETE':
        return handler.deleteMeetingById(mid)
    else:
        return jsonify(Error="Method Not Allowed"), 405

@api.route('/meeting', methods=['POST'])
def createMeeting():
    return MeetingHandler().createMeeting(request.json)


# -------------------- SECTION --------------------
@api.route('/section/<int:sid>', methods=['GET', 'PUT', 'DELETE'])
def getSectionById(sid):
    handler = SectionHandler()
    if request.method == 'GET':
        return handler.getSectionById(sid)
    elif request.method == 'PUT':
        return handler.updateSectionById(sid, request.json)
    elif request.method == 'DELETE':
        return handler.deleteSectionById(sid)
    else:
        return jsonify(Error="Method Not Allowed"), 405

@api.route('/section', methods=['POST'])
def createSection():
    return SectionHandler().createSection(request.json)


# -------------------- REQUISITE --------------------
@api.route('/requisite/<int:classid>/<int:reqid>', methods=['GET', 'DELETE'])
def getRequisiteById(classid, reqid):
    handler = RequisiteHandler()
    if request.method == 'GET':
        return handler.getRequisiteById(classid, reqid)
    elif request.method == 'DELETE':
        return handler.deleteRequisiteById(classid, reqid)
    else:
        return jsonify(Error="Method Not Allowed"), 405

@api.route('/requisite', methods=['POST'])
def createRequisite():
    return RequisiteHandler().createRequisite(request.json)


# -------------------- CLASSES --------------------
@api.route('/classes/<int:cid>', methods=['GET', 'PUT', 'DELETE'])
def handleClassById(cid):
    handler = ClassHandler()
    if request.method == 'GET':
        return handler.getClassById(cid)
    elif request.method == 'PUT':
        return handler.updateClassById(cid, request.json)
    elif request.method == 'DELETE':
        return handler.deleteClassById(cid)
    else:
        return jsonify(Error="Method Not Allowed"), 405

@api.route('/classes', methods=['POST'])
def createClass():
    return ClassHandler().createClass(request.json)


# -------------------- ROOMS --------------------
@api.route('/room/<int:rid>', methods=['GET', 'PUT', 'DELETE'])
def handleRoomById(rid):
    handler = RoomHandler()
    if request.method == 'GET':
        return handler.getRoomById(rid)
    elif request.method == 'PUT':
        return handler.updateRoomById(rid, request.json)
    elif request.method == 'DELETE':
        return handler.deleteRoomById(rid)
    else:
        return jsonify(Error="Method Not Allowed"), 405

@api.route('/room', methods=['POST'])
def createRoom():
    return RoomHandler().createRoom(request.json)


# -------------------- STATS --------------------
# Existing stats endpoint (sections by day)
@api.route('/stats/sections-by-day', methods=['GET'])
def getStatSectionsByDay():
    if request.method == 'GET':
        year = request.args.get("year")
        semester = request.args.get("semester")
        return SectionHandler().getStatSectionsByDay(year, semester)
    else:
        return jsonify(Error="Method Not Allowed"), 405


@api.route('/stats/top-classes-by-avg-duration', methods=['GET'])
def top_classes_by_avg_duration_route():
    year = request.args.get('year')
    semester = request.args.get('semester')
    limit_str = request.args.get('limit', '1')

    try:
        limit = int(limit_str)
    except ValueError:
        return jsonify(Error="limit must be an integer"), 400

    valid_semesters = {'Fall', 'Spring', 'V1', 'V2'}
    if semester and semester not in valid_semesters:
        return jsonify(Error="semester must be one of: Fall, Spring, V1, V2"), 400

    return StatsHandler().top_classes_by_avg_duration(year, semester, limit)


@api.route('/stats/classes-without-prereqs', methods=['GET'])
def classes_without_prereqs_route():
    return StatsHandler().classes_without_prereqs()


# ---- NEW ROUTES FROM MERGED FILE ----
@api.route('/stats/top-rooms-by-utilization', methods=['GET'])
def top_rooms_by_utilization_route():
    year = request.args.get('year')
    semester_raw = request.args.get('semester')
    semester = semester_raw.strip().title() if semester_raw else None
    limit_str = request.args.get('limit')

    try:
        limit = int(limit_str) if limit_str else None
    except ValueError:
        return jsonify(Error="limit must be an integer"), 400

    valid_semesters = {'Fall', 'Spring', 'V1', 'V2'}
    if semester and semester not in valid_semesters:
        return jsonify(Error="semester must be one of: Fall, Spring, V1, V2"), 400

    return StatsHandler().top_rooms_by_utilization(year, semester, limit)


@api.route('/stats/multi-room-classes', methods=['GET'])
def multi_room_classes_route():
    year = request.args.get('year')
    semester_raw = request.args.get('semester')
    semester = semester_raw.strip().title() if semester_raw else None
    limit_str = request.args.get('limit')
    orderby = request.args.get('orderby')

    try:
        limit = int(limit_str)
        # Enforce max limit of 10
        if limit > 10:
            limit = 10
        elif limit < 1:
            limit = 1
    except ValueError:
        return jsonify(Error="limit must be an integer"), 400

    valid_semesters = {'Fall', 'Spring', 'V1', 'V2'}
    if semester and semester not in valid_semesters:
        return jsonify(Error="semester must be one of: Fall, Spring, V1, V2"), 400

    if orderby and orderby.lower() not in ('asc', 'desc'):
        return jsonify(Error="orderby must be 'asc' or 'desc'"), 400

    return StatsHandler().multi_room_classes(year, semester, limit, orderby)


@api.route('/stats/top-departments-by-sections', methods=['GET'])
def top_departments_by_sections_route():
    year = request.args.get('year')
    semester_raw = request.args.get('semester')
    semester = semester_raw.strip().title() if semester_raw else None
    limit_str = request.args.get('limit')

    limit = None
    if limit_str:
        try:
            limit = int(limit_str)
        except ValueError:
            return jsonify(Error="limit must be an integer"), 400

    valid_semesters = {'Fall', 'Spring', 'V1', 'V2'}
    if semester and semester not in valid_semesters:
        return jsonify(Error="semester must be one of: Fall, Spring, V1, V2"), 400

    return StatsHandler().top_departments_by_sections(year, semester, limit)

@api.route('/chat', methods=['POST'])
def chat_endpoint():

    if not request.is_json:
        return jsonify(Error="Request must be JSON"), 400

    data = request.get_json()
    question = data.get('question', '').strip()

    if not question:
        return jsonify(Error="Field 'question' is required"), 400

    try:
        answer = chatbot.ask(question)
        return jsonify({
            "question": question,
            "answer": answer
        })
    except Exception as e:
        print(f"Chatbot error: {e}")
        return jsonify(Error="Internal chatbot error"), 500

app.register_blueprint(api)

# -------------------- MAIN --------------------
if __name__ == '__main__':
    app.run()