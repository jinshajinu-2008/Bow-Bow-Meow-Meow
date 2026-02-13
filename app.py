import sqlite3
from flask import Flask, request, jsonify, g
from flask_cors import CORS

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

DATABASE = 'pets.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # Create Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fullname TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        # Create Pets Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                age INTEGER,
                breed TEXT,
                animal_type TEXT,
                location TEXT,
                image_url TEXT,
                FOREIGN KEY (owner_id) REFERENCES users (id)
            )
        ''')

        # Create Matches Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                pet_id INTEGER NOT NULL,
                status TEXT NOT NULL, -- 'liked' or 'passed'
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (pet_id) REFERENCES pets (id)
            )
        ''')
        
        db.commit()

# --- API Endpoints ---

@app.route('/')
def index():
    return app.send_static_file('match_maker.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO users (fullname, email, password) VALUES (?, ?, ?)',
                       (data['fullname'], data['email'], data['password']))
        db.commit()
        user_id = cursor.lastrowid
        return jsonify({'success': True, 'user_id': user_id, 'message': 'User registered successfully!'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Email already exists!'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/register-pet', methods=['POST'])
def register_pet():
    data = request.json
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO pets (owner_id, name, age, breed, animal_type, location, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (data['owner_id'], data['name'], data['age'], data['breed'], data['animal_type'], data['location'], 'https://place.dog/300/400')) # Placeholder image for now
        db.commit()
        return jsonify({'success': True, 'message': 'Pet registered successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/pets', methods=['GET'])
def get_pets():
    # Simple logic: return all pets except the user's own (if we had login session)
    # For now, just return all pets. In a real app, filter by location/preference.
    current_user_id = request.args.get('user_id')
    
    db = get_db()
    cursor = db.cursor()
    
    # Get pets that haven't been swiped on by this user
    query = '''
        SELECT p.* FROM pets p
        WHERE p.id NOT IN (
            SELECT pet_id FROM matches WHERE user_id = ?
        )
        AND p.owner_id != ?
    '''
    
    # If no user_id provided (e.g. testing), just return all
    if not current_user_id:
        cursor.execute('SELECT * FROM pets')
    else:
        cursor.execute(query, (current_user_id, current_user_id))
        
    pets = cursor.fetchall()
    pets_list = [dict(pet) for pet in pets]
    
    return jsonify({'success': True, 'pets': pets_list})

@app.route('/swipe', methods=['POST'])
def swipe():
    data = request.json
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO matches (user_id, pet_id, status) VALUES (?, ?, ?)',
                       (data['user_id'], data['pet_id'], data['status']))
        db.commit()
        
        is_match = False
        if data['status'] == 'liked':
            # Check if it's a mutual match (simplified: does the pet owner like the user's pet?)
            # For this MVP, we'll just say "It's a Match!" if you like them.
            is_match = True
            
        return jsonify({'success': True, 'match': is_match})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    init_db()
    print("Database initialized.")
    app.run(debug=True, port=5000)
