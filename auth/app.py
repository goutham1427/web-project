from flask import Flask
from auth.auth import auth  # Import the Blueprint from auth.py

app = Flask(__name__)

app.register_blueprint(auth, url_prefix='/auth')  # Register it with a prefix

if __name__ == '__main__':
    app.run(debug=True)
