from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Database initialization
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Create MEMBER table
    c.execute('''CREATE TABLE IF NOT EXISTS MEMBER (
        MEMBER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        NAME TEXT NOT NULL,
        DOB TEXT,
        JOIN_DATE TEXT,
        EMAIL TEXT
    )''')
    
    # Create MEMBER_PHONE table
    c.execute('''CREATE TABLE IF NOT EXISTS MEMBER_PHONE (
        MEMBER_ID INTEGER,
        PHONE_NUMBER TEXT,
        FOREIGN KEY (MEMBER_ID) REFERENCES MEMBER(MEMBER_ID),
        PRIMARY KEY (MEMBER_ID, PHONE_NUMBER)
    )''')
    
    # Create TRAINER table
    c.execute('''CREATE TABLE IF NOT EXISTS TRAINER (
        TRAINER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        NAME TEXT NOT NULL,
        SPECIALISATION TEXT
    )''')
    
    # Create WORKOUT_PLAN table
    c.execute('''CREATE TABLE IF NOT EXISTS WORKOUT_PLAN (
        Plan_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Plan_name TEXT,
        Description TEXT,
        Intensity_level TEXT,
        Trainer_id INTEGER,
        FOREIGN KEY (Trainer_id) REFERENCES TRAINER(TRAINER_ID)
    )''')
    
    # Create DIET_PLAN table
    c.execute('''CREATE TABLE IF NOT EXISTS DIET_PLAN (
        DietPlan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        DietPlan_name TEXT,
        Diet_Description TEXT,
        Target_Calories INTEGER,
        Trainer_id INTEGER,
        FOREIGN KEY (Trainer_id) REFERENCES TRAINER(TRAINER_ID)
    )''')
    
    # Create MEMBERSHIP table
    c.execute('''CREATE TABLE IF NOT EXISTS MEMBERSHIP (
        Membership_id INTEGER PRIMARY KEY AUTOINCREMENT,
        Membership_type TEXT,
        Start_date TEXT,
        End_date TEXT,
        Payment_type TEXT,
        Payment_amount REAL,
        Status TEXT,
        Member_id INTEGER,
        DietPlan_id INTEGER,
        Trainer_id INTEGER,
        Plan_id INTEGER,
        FOREIGN KEY (Member_id) REFERENCES MEMBER(MEMBER_ID),
        FOREIGN KEY (DietPlan_id) REFERENCES DIET_PLAN(DietPlan_id),
        FOREIGN KEY (Trainer_id) REFERENCES TRAINER(TRAINER_ID),
        FOREIGN KEY (Plan_id) REFERENCES WORKOUT_PLAN(Plan_ID)
    )''')
    
    # Create MEMBER_VITALS table
    c.execute('''CREATE TABLE IF NOT EXISTS MEMBER_VITALS (
        VITALS_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        WEIGHT REAL,
        HEIGHT REAL,
        RECORD_DATE TEXT,
        MEMB_ID INTEGER,
        FOREIGN KEY (MEMB_ID) REFERENCES MEMBER(MEMBER_ID)
    )''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Main route - serve index.html from project root
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# MEMBER CRUD Operations
@app.route('/api/members', methods=['GET', 'POST'])
def members():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        c.execute('INSERT INTO MEMBER (NAME, DOB, JOIN_DATE, EMAIL) VALUES (?, ?, ?, ?)',
                  (data['name'], data['dob'], data['join_date'], data['email']))
        conn.commit()
        member_id = c.lastrowid
        conn.close()
        return jsonify({'message': 'Member added successfully', 'member_id': member_id}), 201
    
    else:
        c.execute('SELECT * FROM MEMBER')
        members = c.fetchall()
        conn.close()
        return jsonify([{
            'member_id': m[0], 'name': m[1], 'dob': m[2], 
            'join_date': m[3], 'email': m[4]
        } for m in members])

@app.route('/api/members/<int:id>', methods=['PUT', 'DELETE'])
def member_detail(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    if request.method == 'PUT':
        data = request.json
        c.execute('UPDATE MEMBER SET NAME=?, DOB=?, EMAIL=? WHERE MEMBER_ID=?',
                  (data['name'], data['dob'], data['email'], id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Member updated successfully'})
    
    elif request.method == 'DELETE':
        c.execute('DELETE FROM MEMBER WHERE MEMBER_ID=?', (id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Member deleted successfully'})

# TRAINER CRUD Operations
@app.route('/api/trainers', methods=['GET', 'POST'])
def trainers():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        c.execute('INSERT INTO TRAINER (NAME, SPECIALISATION) VALUES (?, ?)',
                  (data['name'], data['specialisation']))
        conn.commit()
        trainer_id = c.lastrowid
        conn.close()
        return jsonify({'message': 'Trainer added successfully', 'trainer_id': trainer_id}), 201
    
    else:
        c.execute('SELECT * FROM TRAINER')
        trainers = c.fetchall()
        conn.close()
        return jsonify([{
            'trainer_id': t[0], 'name': t[1], 'specialisation': t[2]
        } for t in trainers])

@app.route('/api/trainers/<int:id>', methods=['PUT', 'DELETE'])
def trainer_detail(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    if request.method == 'PUT':
        data = request.json
        c.execute('UPDATE TRAINER SET NAME=?, SPECIALISATION=? WHERE TRAINER_ID=?',
                  (data['name'], data['specialisation'], id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Trainer updated successfully'})
    
    elif request.method == 'DELETE':
        c.execute('DELETE FROM TRAINER WHERE TRAINER_ID=?', (id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Trainer deleted successfully'})

# MEMBERSHIP CRUD Operations
@app.route('/api/memberships', methods=['GET', 'POST'])
def memberships():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        c.execute('''INSERT INTO MEMBERSHIP 
                     (Membership_type, Start_date, End_date, Payment_type, 
                      Payment_amount, Status, Member_id, DietPlan_id, Trainer_id, Plan_id) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (data['membership_type'], data['start_date'], data['end_date'],
                   data['payment_type'], data['payment_amount'], data['status'],
                   data['member_id'], data.get('dietplan_id'), data.get('trainer_id'), data.get('plan_id')))
        conn.commit()
        membership_id = c.lastrowid
        conn.close()
        return jsonify({'message': 'Membership added successfully', 'membership_id': membership_id}), 201
    
    else:
        c.execute('''SELECT m.*, mem.NAME 
                     FROM MEMBERSHIP m 
                     LEFT JOIN MEMBER mem ON m.Member_id = mem.MEMBER_ID''')
        memberships = c.fetchall()
        conn.close()
        return jsonify([{
            'membership_id': m[0], 'membership_type': m[1], 'start_date': m[2],
            'end_date': m[3], 'payment_type': m[4], 'payment_amount': m[5],
            'status': m[6], 'member_id': m[7], 'member_name': m[11]
        } for m in memberships])

# WORKOUT PLAN CRUD Operations
@app.route('/api/workouts', methods=['GET', 'POST'])
def workouts():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        c.execute('''INSERT INTO WORKOUT_PLAN 
                     (Plan_name, Description, Intensity_level, Trainer_id) 
                     VALUES (?, ?, ?, ?)''',
                  (data['plan_name'], data['description'], 
                   data['intensity_level'], data.get('trainer_id')))
        conn.commit()
        plan_id = c.lastrowid
        conn.close()
        return jsonify({'message': 'Workout plan added successfully', 'plan_id': plan_id}), 201
    
    else:
        c.execute('''SELECT w.*, t.NAME 
                     FROM WORKOUT_PLAN w 
                     LEFT JOIN TRAINER t ON w.Trainer_id = t.TRAINER_ID''')
        workouts = c.fetchall()
        conn.close()
        return jsonify([{
            'plan_id': w[0], 'plan_name': w[1], 'description': w[2],
            'intensity_level': w[3], 'trainer_id': w[4], 'trainer_name': w[5]
        } for w in workouts])

# DIET PLAN CRUD Operations
@app.route('/api/diets', methods=['GET', 'POST'])
def diets():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        c.execute('''INSERT INTO DIET_PLAN 
                     (DietPlan_name, Diet_Description, Target_Calories, Trainer_id) 
                     VALUES (?, ?, ?, ?)''',
                  (data['dietplan_name'], data['diet_description'], 
                   data['target_calories'], data.get('trainer_id')))
        conn.commit()
        dietplan_id = c.lastrowid
        conn.close()
        return jsonify({'message': 'Diet plan added successfully', 'dietplan_id': dietplan_id}), 201
    
    else:
        c.execute('''SELECT d.*, t.NAME 
                     FROM DIET_PLAN d 
                     LEFT JOIN TRAINER t ON d.Trainer_id = t.TRAINER_ID''')
        diets = c.fetchall()
        conn.close()
        return jsonify([{
            'dietplan_id': d[0], 'dietplan_name': d[1], 'diet_description': d[2],
            'target_calories': d[3], 'trainer_id': d[4], 'trainer_name': d[5]
        } for d in diets])

# MEMBER VITALS Operations
@app.route('/api/vitals', methods=['GET', 'POST'])
def vitals():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        c.execute('''INSERT INTO MEMBER_VITALS 
                     (WEIGHT, HEIGHT, RECORD_DATE, MEMB_ID) 
                     VALUES (?, ?, ?, ?)''',
                  (data['weight'], data['height'], data['record_date'], data['memb_id']))
        conn.commit()
        vitals_id = c.lastrowid
        conn.close()
        return jsonify({'message': 'Vitals recorded successfully', 'vitals_id': vitals_id}), 201
    
    else:
        c.execute('''SELECT v.*, m.NAME 
                     FROM MEMBER_VITALS v 
                     LEFT JOIN MEMBER m ON v.MEMB_ID = m.MEMBER_ID''')
        vitals = c.fetchall()
        conn.close()
        return jsonify([{
            'vitals_id': v[0], 'weight': v[1], 'height': v[2],
            'record_date': v[3], 'memb_id': v[4], 'member_name': v[5]
        } for v in vitals])

if __name__ == '__main__':
    app.run(debug=True, port=5000)