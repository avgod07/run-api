from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from datetime import datetime, timedelta
from sqlalchemy import func
import requests


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workout.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'youcantfigurethisout' 

db = SQLAlchemy(app)
login_manager = LoginManager(app)

# user redirection if not logged in
login_manager.login_view = 'login' 

# User model 
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)  
    age = db.Column(db.Integer, nullable = False)
    weight = db.Column(db.Float, nullable = False)
    workouts = db.relationship('Workout', backref='user', lazy=True)

# Workout model
class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    duration_minutes = db.Column(db.Integer, nullable=False)
    distance_km = db.Column(db.Float, nullable=False)
    route_nickname = db.Column(db.String(100))
    heart_rate = db.Column(db.Integer)
    date_time = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    calories_burned = db.Column(db.Float)

    def calculate_calories_burned(self):
        calories_per_km = 0.75 * current_user.weight
        return self.distance_km * calories_per_km

# load user into session based on their id
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return "Welcome to the Workout API!"

# registration endpoint
@app.route('/register', methods=['POST'])
def register():
    """
    Registers a new user.
    Expects 'username' and 'password' in JSON payload.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    age = data.get('age')
    weight = data.get('weight')

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists."}), 400

    new_user = User(username = username, password = password, age = age, weight = weight)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully!"}), 201

# login endpoint
@app.route('/login', methods=['POST'])
def login():
    """
    Logs in a user.
    Expects 'username' and 'password'.
    """

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()


    if user and user.password == password:
        login_user(user)
        return jsonify({"message": "Login successful!"}), 200
    else:
        return jsonify({"error": "Invalid username or password."}), 400

# logout endpoint
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    Logs out the current user.
    """

    logout_user()
    return jsonify({"message": "Logout successful!"}), 200

# endpoint to add a workout to the database
@app.route('/workouts', methods=['POST'])
@login_required
def add_workout():
    """
    Adds a new workout for the logged-in user.
    Expects workout
    """
    data = request.get_json()


    new_workout = Workout(
        duration_minutes=data.get('duration_minutes'),
        distance_km=data.get('distance_km'),
        route_nickname=data.get('route_nickname'),
        heart_rate=data.get('heart_rate'),
        date_time=datetime.utcnow(),
        user_id=current_user.id
    )
    new_workout.calories_burned = new_workout.calculate_calories_burned()



    db.session.add(new_workout)
    db.session.commit()

    return jsonify({"message": "Workout added successfully!"}), 201

# endpoint to receive a list of workouts in the database (different per user) 
@app.route('/listed_workouts', methods=['GET'])
@login_required
def get_workouts():
    """
    Retrieves workouts for the logged-in user with optional filtering.
    Query Parameters:
        - start_date (YYYY-MM-DD)
        - end_date (YYYY-MM-DD)
    """
    # parameters to filter the data by date (showcases workouts from start date to one day before the end date)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')


    query = Workout.query.filter_by(user_id=current_user.id)

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            query = query.filter(Workout.date_time >= start_date)
        except ValueError:
            return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD."}), 400

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            query = query.filter(Workout.date_time <= end_date)
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD."}), 400
        
    workouts = query.order_by(Workout.date_time.desc()).all()

    result = []

    # prep data to return in a list
    for workout in workouts:
        result.append({
            "id": workout.id,
            "duration_minutes": workout.duration_minutes,
            "distance_km": workout.distance_km,
            "route_nickname": workout.route_nickname,
            "heart_rate": workout.heart_rate,
            "age": workout.user.age,
            "weight": workout.user.weight,
            "date_time": workout.date_time.strftime('%Y-%m-%d %H:%M:%S'),
            "calories_burned": workout.calories_burned
    })

    return jsonify(result), 200

# endpoint to receive stats on your running for the week
@app.route('/stats/week', methods=['GET'])
@login_required
def stat_week():

    """
    Returns statistics for the logged-in user such as:
    - Total distance run per week
    - Average run duration
    - Total calories burned per week
    """
    today = datetime.utcnow()
    start_of_week = today - timedelta(days=today.weekday())

    total_distance_week = db.session.query(func.sum(Workout.distance_km)).filter(
        Workout.user_id == current_user.id,
        Workout.date_time >= start_of_week
    ).scalar()


    avg_run_duration = db.session.query(func.avg(Workout.duration_minutes)).filter(
        Workout.user_id == current_user.id
    ).scalar()

    total_calories_week = db.session.query(func.sum(Workout.calories_burned)).filter(
        Workout.user_id == current_user.id,
        Workout.date_time >= start_of_week
    ).scalar()



    return jsonify({
        "total_distance_week": total_distance_week,
        "avg_run_duration": avg_run_duration,
        "total_calories_week": total_calories_week,
    }), 200

# endpoint to receive stats on your running for the month
@app.route('/stats/month', methods=['GET'])
@login_required
def stat_month():
    """
    Returns statistics for the logged-in user such as:
    - Total distance run per month
    - Average run duration
    - Total calories burned per month
    """
    today = datetime.utcnow()
    start_of_month = today.replace(day=1)


    total_distance_month = db.session.query(func.sum(Workout.distance_km)).filter(
        Workout.user_id == current_user.id,
        Workout.date_time >= start_of_month
    ).scalar()

    avg_run_duration = db.session.query(func.avg(Workout.duration_minutes)).filter(
        Workout.user_id == current_user.id
    ).scalar()

    total_calories_month = db.session.query(func.sum(Workout.calories_burned)).filter(
        Workout.user_id == current_user.id,
        Workout.date_time >= start_of_month
    ).scalar()

    return jsonify({
        "total_distance_month": total_distance_month,
        "avg_run_duration": avg_run_duration,
        "total_calories_month": total_calories_month
    }), 200

# endpoint to receive recipes based on your running workouts
@app.route('/recipes', methods=['GET'])
@login_required
def get_recipes():
    """
    Fetches the last workout and provides 3 recipes from Spoonacular API based on calories burned.
    """
    last_workout = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.date_time.desc()).first()

    if not last_workout:
        return jsonify({"error": "No workout found for the current user."}), 404

    calories_burned = last_workout.calories_burned

    # Spoonacular API request
    url = 'https://api.spoonacular.com/recipes/findByNutrients'

    params = {
        'apiKey': 'f16ddcdc359d4c26adcd9d6a2a5ef2cc',
        'minCalories': calories_burned - 50,  
        'maxCalories': calories_burned + 50,  
        'number': 2  
    }

    response = requests.get(url, params=params)
    

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch recipes from Spoonacular."}), 500

    recipes = response.json()


    # Format the response
    recipe_list = []
    for recipe in recipes:
        recipe_list.append({
            'title': recipe['title'],
            'calories': recipe['calories'],
            'image': recipe['image']
        })

    return jsonify({

        "calories_burned": calories_burned,
        "recipes": recipe_list
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)