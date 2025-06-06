import os
import math
from flask import Flask, render_template, redirect, url_for, request, flash, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import folium
from folium.plugins import MarkerCluster
import json
import csv
from PIL import Image
from chatbot import chatbot  # Make sure to install Pillow for image processing

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management
# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/MINI NEW/MY PROJECT/users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable track modifications
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to save uploaded photos
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Create the uploads folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Define places globally so they can be accessed both for the map and image upload
places = [
    {'name': 'Munnar', 'lat': 10.0889, 'lon': 77.0582, 'description': 'A picturesque hill station known for tea plantations.', 'type': 'Tourist'},
    {'name': 'Alleppey', 'lat': 9.5000, 'lon': 76.3500, 'description': 'Famous for beautiful backwaters and houseboat cruises.', 'type': 'Tourist'},
    {'name': 'Wayanad', 'lat': 11.6827, 'lon': 75.2913, 'description': 'Known for waterfalls, caves, and wildlife sanctuaries.', 'type': 'Tourist'},
    {'name': 'My Home', 'lat': 10.1541, 'lon': 76.3147, 'description': 'This is my home. Coordinates: 10°09\'14.8"N 76°18\'52.8"E', 'type': 'Home'}
]

# Haversine formula to calculate the distance between two geographic coordinates
def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0
    # Convert degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    
    # Differences in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Distance in kilometers
    distance = R * c
    return distance

# Function to extract GPS data from an image's EXIF metadata
def get_gps_from_exif(image):
    try:
        exif_data = image._getexif()
        if not exif_data:
            return None
        gps_info = exif_data.get(34853)  # GPSInfo tag
        if not gps_info:
            return None
        
        def convert_to_degrees(value):
            d, m, s = value
            return d + (m / 60.0) + (s / 3600.0)

        lat = convert_to_degrees(gps_info[2])
        lon = convert_to_degrees(gps_info[4])
        
        if gps_info[1] != "N":
            lat = -lat
        if gps_info[3] != "E":
            lon = -lon
        
        return lat, lon
    except Exception:
        return None

# Function to handle visited state with image validation
def mark_visited_with_image(place_name, uploaded_image):
    try:
        image = Image.open(uploaded_image)
        gps_coords = get_gps_from_exif(image)
        if not gps_coords:
            flash("No GPS data found in the image. Please upload a valid photo.", 'danger')
            return
        
        current_lat, current_lon = gps_coords
        for place in places:
            if place['name'] == place_name:
                # Use the haversine formula to calculate the distance
                distance = haversine(place['lat'], place['lon'], current_lat, current_lon)
                if distance <= 25:  # If the distance is 25 km or less, award points
                    current_user.achievements[place_name] = True
                    current_user.travel_points += 20
                    db.session.commit()
                    flash(f"You have visited {place_name} and earned 20 points!", 'success')
                else:
                    flash(f"The photo's location is {distance:.2f} km away from {place_name}. Please upload a valid photo.", 'danger')
                return
    except Exception as e:
        flash(f"Error processing the image: {e}", 'danger')

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    achievements = db.Column(db.Integer, nullable=True)  # Store achievements as a JSON string
    travel_points = db.Column(db.Integer, default=0)  # Store travel points
    rank = db.Column(db.Integer, nullable=True)

# Create the database and tables
with app.app_context():
    db.create_all()  # Create the database tables

# User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@app.route('/')
def home():
    return render_template('home.html')  # Render the home.html template

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()  # Fetch user from DB
        if user and user.password == password:  # Verify password
            login_user(user)
            flash(f'Login successful! Welcome {username}', 'success')
            return redirect(url_for('index'))  # Redirect to the map route
        else:
            flash('Login failed. Check your username and password.', 'danger')
    return render_template('login.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('login'))
        # Create a new user
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('login.html')  

@app.route('/index')
@login_required
def index():
    return render_template('index.html')

# Map route
@app.route('/map', methods=['GET', 'POST'])
@login_required
def map():
    if request.method == 'POST':
        selected_place = request.form.get('place')
        photo = request.files.get('photo')

        if selected_place and photo:
            # Save the uploaded photo
            photo_filename = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
            photo.save(photo_filename)

            # Validate location and upload photo
            mark_visited_with_image(selected_place, photo_filename)

    # Create the map
    map_object = folium.Map(location=[10.8505, 76.2711], zoom_start=7)
    marker_cluster = MarkerCluster().add_to(map_object)

    for place in places:
        folium.Marker(
            [place['lat'], place['lon']],
            popup=f"{place['name']}: {place['description']}",
            icon=folium.Icon(color="blue")
        ).add_to(marker_cluster)

    # Render the map
    return render_template('map.html', map=map_object._repr_html_())

def show_map():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return "Invalid coordinates!", 400
    return render_template('map.html', lat=lat, lon=lon)

# Route for logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    achievements = json.loads(current_user.achievements) if current_user.achievements else {}
    return render_template('dashboard.html', achievements=achievements, travel_points=current_user.travel_points)


# Achievements route
@app.route('/achievements')
@login_required
def achievements():
    achievements = json.loads(current_user.achievements)  # Convert string back to dictionary
    return render_template('achievements.html', achievements=achievements)

# Leaderboard route
@app.route('/leaderboard')
@login_required
def leaderboard():
    users = User.query.order_by(User.rank.asc()).all()
    return render_template('leaderboard.html', users=users)

@app.route('/recommendations')
@login_required
def recommendations():
    return render_template('recommendations.html', places=places)

@app.route('/chatbot', methods=['GET', 'POST'], endpoint='chatbot')
def handle_chatbot():
    if request.method == 'POST':
        return chatbot()
    else:
        # Handle GET request (e.g., render a chatbot page)
        return render_template('chatbot.html')  # Create a chatbot.html template

# Export achievements route
@app.route('/export')
@login_required
def export():
    achievements = json.loads(current_user.achievements)  # Convert string back to dictionary
    travel_points = current_user.travel_points

    # Create a CSV response
    output = Response(content_type='text/csv')
    output.headers["Content-Disposition"] = "attachment; filename=achievements.csv"
    
    writer = csv.writer(output)
    writer.writerow(['Achievement', 'Status', 'Travel Points'])
    
    for achievement, status in achievements.items():
        writer.writerow([achievement, 'Achieved' if status else 'Not Achieved', travel_points])

    return output

if __name__ == "__main__":
    app.run(debug=True)