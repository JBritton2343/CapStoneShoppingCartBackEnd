"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, make_response
from flask_migrate import migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
from flask_jwt_extended import JWTManager, create_access_token
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from functools import wraps
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "060cc30ff52444498fe0b617e4b53519"
jwt = JWTManager(app)
MIGRATE = migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return jsonify({'message': 'Token not found!'}), 401
        
        try:
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message' : 'Token is not valid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated
# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET', "POST"])
@token_required
def handle_hello():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    


    response_body = {
        "msg": "Welcome back /user are you ready to shop again?"
    }

    return jsonify(response_body), 200


@app.route('/signup', methods=['POST'])
def create_user():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message' : 'newuser created'})

@app.route('/user/<public_id', methods=['Delete'])
@token_required
def delete_user(current_user, public_id):
    user=User.query.filter_by(public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'})
    
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message' : 'user has been deleted'})


@app.route('/Items', methods=['GET', "POST"])
def handle_items_selected():
    response_body ={
        
    }
    return jsonify(response_body)

app.route("/token", methods=["POST"])
def create_token():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(username=username, password=password).first()
    if user is None:
        return jsonify({"msg": "Bad username or password"}), 402

    access_token = create_access_token(identify=user.id)
    return jsonify({"token": access_token, "user_id": user.id})

@app.route("/login")
@token_required
def login():
    auth=request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response("user not found", 401, {'www-Authenticate' : "Basic realm='Login required!'"})
    user = User.query.filter_by(name=auth.username).first()
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic Realm="Login required!"'})
    if check_password_hash(user.password, auth.password):
        token=jwt.encode({'public_id' : user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes = 30)})

        return jsonify({'token' : token.decode('UTF-8')})
    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic Realm="Login required!"'})



# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
