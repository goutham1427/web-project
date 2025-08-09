from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from transcription import transcribe_audio, save_transcription, translate_text
from transcription.live_transcription import start_live_transcription

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this to a more secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Define User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return redirect(url_for("login"))

# 🟢 User Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")

        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please login.", "success")
        return redirect(url_for("login"))
    
    return render_template("register.html")

# 🟢 User Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials!", "danger")
    
    return render_template("login.html")

# 🟢 Dashboard (Transcription Page)
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("transcription.html", username=current_user.username)

# 🟢 Transcription Route (Redirects to Output Page)
@app.route("/transcribe", methods=["POST"])
@login_required
def transcribe_audio_route():
    if 'audiofile' not in request.files:
        flash("No file uploaded!", "danger")
        return redirect(url_for("dashboard"))

    file = request.files['audiofile']
    if file.filename == '':
        flash("Invalid file!", "danger")
        return redirect(url_for("dashboard"))

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        transcription_result = transcribe_audio(filepath)
        if transcription_result:
            save_transcription(transcription_result)
            session["transcription_result"] = transcription_result  # Store result in session
            return redirect(url_for("output"))  # Redirect to output page
        else:
            flash("Transcription failed!", "danger")

    return redirect(url_for("dashboard"))

# 🟢 Output Page
@app.route("/output")
@login_required
def output():
    transcription_result = session.get("transcription_result", "")
    return render_template("output.html", transcription_result=transcription_result)

# 🟢 Logout Route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))

# Run the app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True, port=5000)
