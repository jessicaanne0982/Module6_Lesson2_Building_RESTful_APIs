from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
ma = Marshmallow(app)

class MemberSchema(ma.Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    age = fields.Integer(required=True)

    class Meta:
        fields = ("id", "name", "age")

class WorkoutSchema(ma.Schema):
    session_id = fields.Integer(required=True)
    member_id = fields.Integer(required=True)
    session_date = fields.String(required=True)
    session_time = fields.String(required=True)
    activity = fields.String(required=True)
    duration_minutes = fields.Integer(required=True)
    calories_burned = fields.Integer(required=True)

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

# Connect to database
def get_db_connection():
    db_name = "fitness_center_db"
    user = "root"
    password = "my_password" 
    host = "localhost"
 
    try:
        conn = mysql.connector.connect(
            database=db_name,
            user=user,
            password=password,
            host=host
        )
   
        print("Connected to MySQL database successfully")
        return conn
   
    except Error as e:
        print(f"Error: {e}")
        return None

# Flask route to home page
@app.route("/")
def home():
    return "Welcome to the Fitness Management Home Page!"

# Flask route to access the complete list of members from the Members Table of the fitness_management_db
@app.route("/members", methods=["GET"])
def get_members():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error" : "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)
    
        query = "SELECT * FROM Members"
        cursor.execute(query)
        members = cursor.fetchall()
    
        return members_schema.jsonify(members)
   
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Flask route to access one specific member
@app.route("/members/<int:id>", methods=["GET"])
def get_specific_member(id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error" : "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)
    
        member_to_search = (id, )
        cursor.execute("SELECT * FROM Members WHERE id = %s", member_to_search)
        found_member = cursor.fetchone()
    
        return member_schema.jsonify(found_member)
   
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Flask route to add a new member to the Database
@app.route("/members", methods=["POST"])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
   
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error" : "Database connection failed"}), 500
        cursor = conn.cursor()
    
        new_member = (member_data["id"], member_data["name"], member_data["age"])
        query = "INSERT INTO Members(id, name, age) VALUES (%s, %s, %s)"
        cursor.execute(query, new_member)
        conn.commit()
        return jsonify({"message" : "New member added successfully"}), 201
   
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error":"Internal Server Error"}), 500
   
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
 
# Flask route to update a member's information
@app.route("/members/<int:id>", methods=["PUT"])
def update_member(id):
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error" : "Database connection failed"}), 500
        cursor = conn.cursor()

        updated_member = (member_data["name"], member_data["age"], id)
        query = "UPDATE Members SET name = %s, age = %s WHERE id = %s"
        cursor.execute(query, updated_member)
        conn.commit()
        return jsonify({"message":"Member has been updated successfully"}), 201
   
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error":"Internal Server Error"}), 500
   
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
   
# Flask route to delete a member
@app.route("/members/<int:id>", methods=["DELETE"])
def delete_member(id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error" : "Database connection failed"}), 500
        cursor = conn.cursor()
    
        member_to_remove = (id, )
        cursor.execute("SELECT * FROM Members where id = %s", member_to_remove)
        member = cursor.fetchone()
        if not member:
            return jsonify({"error": "Customer not found"}), 404
   
        query = "DELETE FROM Members where id = %s"
        cursor.execute(query, member_to_remove)
        conn.commit()
        return jsonify({"message":"Member successfully deleted from database"}), 200
   
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error":"Internal Server Error"}), 500
   
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Flask route to list all workouts
@app.route("/workouts", methods=["GET"])
def get_all_workouts():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error" : "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)
    
        query = "SELECT * FROM WorkoutSessions"
        cursor.execute(query)
        workouts = cursor.fetchall()
    
        return workouts_schema.jsonify(workouts)
   
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# # Flask route to access the complete list of workouts for a specific member
@app.route("/workouts/<int:id>", methods=["GET"])
def get_member_workouts(id):

    try:
        member_id = id

        conn = get_db_connection()
        if conn is None:
            return jsonify({"error" : "Database connection failed"}), 500
        
        cursor = conn.cursor(dictionary=True)
    
        query = "SELECT * FROM WorkoutSessions WHERE member_id = %s"
        cursor.execute(query, (member_id, ))
        workouts = cursor.fetchall()
    
        return workouts_schema.jsonify(workouts)
   
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Flask route to update a workout's information
@app.route("/workouts/<int:id>", methods=["PUT"])
def update_workout(id):
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error" : "Database connection failed"}), 500
        cursor = conn.cursor()
        session_id = id
        updated_workout = (
                    workout_data["session_id"], 
                    workout_data["member_id"], 
                    workout_data["session_date"], 
                    workout_data["session_time"], 
                    workout_data["activity"], 
                    workout_data["duration_minutes"], 
                    workout_data["calories_burned"], 
                    session_id
                    )

        query = """UPDATE WorkoutSessions SET session_id = %s, member_id = %s, session_date = %s,  
                session_time = %s, activity = %s, duration_minutes = %s, calories_burned = %s 
                WHERE session_id = %s"""
        cursor.execute(query, updated_workout)
        conn.commit()
        return jsonify({"message":"Workout has been updated successfully"}), 201
   
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error":"Internal Server Error"}), 500
   
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Flask route to "schedule" (or add) a workout
@app.route("/workouts", methods=["POST"])
def schedule_workout():
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error" : "Database Connection Failed"}), 500
        cursor = conn.cursor()

        new_workout = (workout_data["session_id"], 
                    workout_data["member_id"],
                    workout_data["session_date"],
                    workout_data["session_time"],
                    workout_data["activity"],
                    workout_data["duration_minutes"],
                    workout_data["calories_burned"]
                       )
        query = """INSERT INTO WorkoutSessions(session_id, member_id, session_date,
                 session_time, activity, duration_minutes, calories_burned) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, new_workout)
        conn.commit()
        return jsonify({"message" : "New workout successfully scheduled"}), 201
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error":"Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected:
            cursor.close()
            conn.close()
            
if __name__ == '__main__':
    app.run(debug=True)
