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
        WORKOUT_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        WORKOUT_NAME TEXT,
        WORKOUT_DESCRIPTION TEXT,
        INTENSITY TEXT,
        TRAIN_ID INTEGER,
        FOREIGN KEY (TRAIN_ID) REFERENCES TRAINER(TRAINER_ID)
    )''')
    
    # Create DIET_PLAN table
    c.execute('''CREATE TABLE IF NOT EXISTS DIET_PLAN (
        DIETPLAN_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        DIET_NAME TEXT,
        DIET_DESCRIPTION TEXT,
        TARGET_CALORIES INTEGER,
        T_ID INTEGER,
        FOREIGN KEY (T_ID) REFERENCES TRAINER(TRAINER_ID)
    )''')
    
    # Create MEMBERSHIP table
    c.execute('''CREATE TABLE IF NOT EXISTS MEMBERSHIP (
        MEMBERSHIP_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        MEMBERSHIP_TYPE TEXT,
        START_DATE TEXT,
        END_DATE TEXT,
        PAYMENT_TYPE TEXT,
        PAYMENT_AMOUNT REAL,
        STATUS TEXT,
        MEM_ID INTEGER,
        DIET_ID INTEGER,
        TR_ID INTEGER,
        W_ID INTEGER,
        FOREIGN KEY (MEM_ID) REFERENCES MEMBER(MEMBER_ID),
        FOREIGN KEY (DIET_ID) REFERENCES DIET_PLAN(DIETPLAN_ID),
        FOREIGN KEY (TR_ID) REFERENCES TRAINER(TRAINER_ID),
        FOREIGN KEY (W_ID) REFERENCES WORKOUT_PLAN(WORKOUT_ID)
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
                     (MEMBERSHIP_TYPE, START_DATE, END_DATE, PAYMENT_TYPE, 
                      PAYMENT_AMOUNT, STATUS, MEM_ID, DIET_ID, TR_ID, W_ID) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (data['membership_type'], data['start_date'], data['end_date'],
                   data['payment_type'], data['payment_amount'], data['status'],
                   data['mem_id'], data.get('diet_id'), data.get('tr_id'), data.get('w_id')))
        conn.commit()
        membership_id = c.lastrowid
        conn.close()
        return jsonify({'message': 'Membership added successfully', 'membership_id': membership_id}), 201
    
    else:
        c.execute('''SELECT m.*, mem.NAME 
                     FROM MEMBERSHIP m 
                     LEFT JOIN MEMBER mem ON m.MEM_ID = mem.MEMBER_ID''')
        memberships = c.fetchall()
        conn.close()
        return jsonify([{
            'membership_id': m[0], 'membership_type': m[1], 'start_date': m[2],
            'end_date': m[3], 'payment_type': m[4], 'payment_amount': m[5],
            'status': m[6], 'mem_id': m[7], 'member_name': m[11]
        } for m in memberships])

# WORKOUT PLAN CRUD Operations
@app.route('/api/workouts', methods=['GET', 'POST'])
def workouts():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        c.execute('''INSERT INTO WORKOUT_PLAN 
                     (WORKOUT_NAME, WORKOUT_DESCRIPTION, INTENSITY, TRAIN_ID) 
                     VALUES (?, ?, ?, ?)''',
                  (data['workout_name'], data['workout_description'], 
                   data['intensity'], data.get('train_id')))
        conn.commit()
        workout_id = c.lastrowid
        conn.close()
        return jsonify({'message': 'Workout plan added successfully', 'workout_id': workout_id}), 201
    
    else:
        c.execute('''SELECT w.*, t.NAME 
                     FROM WORKOUT_PLAN w 
                     LEFT JOIN TRAINER t ON w.TRAIN_ID = t.TRAINER_ID''')
        workouts = c.fetchall()
        conn.close()
        return jsonify([{
            'workout_id': w[0], 'workout_name': w[1], 'workout_description': w[2],
            'intensity': w[3], 'train_id': w[4], 'trainer_name': w[5]
        } for w in workouts])

# DIET PLAN CRUD Operations
@app.route('/api/diets', methods=['GET', 'POST'])
def diets():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        c.execute('''INSERT INTO DIET_PLAN 
                     (DIET_NAME, DIET_DESCRIPTION, TARGET_CALORIES, T_ID) 
                     VALUES (?, ?, ?, ?)''',
                  (data['diet_name'], data['diet_description'], 
                   data['target_calories'], data.get('t_id')))
        conn.commit()
        diet_id = c.lastrowid
        conn.close()
        return jsonify({'message': 'Diet plan added successfully', 'diet_id': diet_id}), 201
    
    else:
        c.execute('''SELECT d.*, t.NAME 
                     FROM DIET_PLAN d 
                     LEFT JOIN TRAINER t ON d.T_ID = t.TRAINER_ID''')
        diets = c.fetchall()
        conn.close()
        return jsonify([{
            'diet_id': d[0], 'diet_name': d[1], 'diet_description': d[2],
            'target_calories': d[3], 't_id': d[4], 'trainer_name': d[5]
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