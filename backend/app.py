from flask import Flask
from environment.config import db_URI, secret
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
import os
# from flask_cors import CORS

app = Flask(__name__, static_folder='dist')

app.config['SQLALCHEMY_DATABASE_URI'] = db_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.update(dict(PREFERRED_URL_SCHEME = 'https'))
# CORS(app)
app.secret_key = secret
# print(app.config)
db = SQLAlchemy(app)

ma = Marshmallow(app)

bcrypt = Bcrypt(app)

from controllers import users, contacts, goog_auth

app.register_blueprint(contacts.router, url_prefix='/api')
app.register_blueprint(users.router, url_prefix='/api')
app.register_blueprint(goog_auth.router, url_prefix='/api')


@app.route('/', defaults={'path': ''}) # homepage
@app.route('/<path:path>') # any other path
def catch_all(path):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'dist/' + path)
    if os.path.isfile(filename): # if path is a file, send it back
        return app.send_static_file(path)
    return app.send_static_file('index.html') # otherwise send back the index.html file


# # ! Hello world flask app to start you off.
# @app.route('/')
# def index():
#     return "Hello, World!"


