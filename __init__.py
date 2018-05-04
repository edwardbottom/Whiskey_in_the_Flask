from flask import Flask
from flask_login import LoginManager

#creates the flask app and runs it
app = Flask(__name__)
app.run(debug=True)

from app import routes