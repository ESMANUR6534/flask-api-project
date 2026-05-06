from database_models import db, users, Product 
from flask import Flask, render_template, jsonify
from werkzeug.exceptions import HTTPException
from flasgger import Swagger
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(
   filename='app.log',
   level=logging.INFO,
   format='%(asctime)s - %(levelname)s - %(message)s'
)
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['JWT_SECRET_KEY']=os.getenv('JWT_SECRET_KEY')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
      return jsonify({"status":"error","message":e.description}),e.code
    logging.error(f"Sunucu Hatasi:{str(e)}")
    return jsonify({"status":"error","message":"sunucu hatasi olustu!"}),500


 


db.init_app(app)

@app.route("/")
def home():
  return render_template("home.html")

@app.route("/view")
def view():
  return render_template("view.html", values=users.query.all())


swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Token girin: Bearer <TOKEN>"
        }
    }
}

swagger = Swagger(app, config=swagger_config)

from auth import auth_bp
from products import product_bp

app.register_blueprint(auth_bp)
app.register_blueprint(product_bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True,host='0.0.0.0')

