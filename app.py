from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_login import current_user
from routes.speech import speech
from routes.image import img
from routes.auth import auth
from flask_swagger import swagger
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from models.model import User, Role, Resource
from models.connection import db  # Use the already initialized db from models.connection
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import random

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with the app
db.init_app(app)
migrate = Migrate(app, db)

class ProtectedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))

admin = Admin(app, name='Admin dashboard')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Role, db.session))
admin.add_view(ModelView(Resource, db.session))

app.register_blueprint(speech)
app.register_blueprint(img)
app.register_blueprint(auth)

@app.route("/myprompts")
def my_prompts():
    if current_user.is_authenticated:
        image=Resource.query.filter_by(userID=current_user.id, audio=False).all()
        audio=Resource.query.filter_by(userID=current_user.id, audio=True).all()
        return render_template("prompts.html", images=image, audios=audio)
    else:
        return redirect(url_for('auth.login', next=request.url))

@app.route('/swagger')
def swagger_spec():
    swag = swagger(app)
    swag['info']['title'] = "My API"
    swag['info']['description'] = "This is the API documentation"
    return jsonify(swag)

@app.route("/processing")
def processing():
    return render_template("loader.html")

@app.route("/", methods=["GET"])
def index():
    images=Resource.query.filter_by(audio=False).all()
    showed_images = []
    if len(images)>10:
        random.shuffle(images)
        showed_images = images[0:10]
    else:
        showed_images = images

    
    audios = Resource.query.filter_by(audio=True).all()
    showed_audios = []
    if len(audios)>10:
        random.shuffle(audios)
        showed_audios = audios[0:10]
    else:
        showed_audios = showed_audios
    return render_template("index.html", audios=showed_audios, images=showed_images)

@app.route("/newuser", methods=["GET"])
def formuser():
    return render_template("auth/signup.html")

@app.route("/newuser", methods=["POST"])
def newuser():
    # Creazione di un nuovo utente con una password criptata
    user = User(username='testuser', email='test@example.com')
    user.set_password('mysecretpassword')

    # Aggiunta dell'utente al database
    db.session.add(user)
    db.session.commit()

    # Verifica della password
    if user.check_password('mysecretpassword'):
        print("Password corretta!")
    else:
        print("Password errata!")

# flask_login user loader block
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.execute(stmt).scalar_one_or_none()
    
    # return User.query.get(int(user_id))   # legacy
    return user

if __name__ == '__main__':
    app.run(debug=True)
