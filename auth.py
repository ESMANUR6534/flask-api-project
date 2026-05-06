from flask import Blueprint, request, jsonify, current_app
from database_models import db, users 
import jwt
import datetime
import os
from functools import wraps 
from werkzeug.security import generate_password_hash,check_password_hash
import logging

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization'in request.headers:
            auth_header = request.headers['Authorization']
            try:
              token = auth_header.split(" ") [1]
            except IndexError:
                return jsonify({"message":"token formati gecersiz! (Bearer <token> olmali)"}), 401
        if not token:
         return jsonify({"message":"Token eksik veya giris yapilmadi!"}),401
        try:
            data = jwt.decode(token,current_app.config['SECRET_KEY'],algorithms=["HS256"])
            current_user_id = data["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"message":"Token suresi dolmus!"}),401
        except jwt.InvalidTokenError:
            logging.warning("Gecersiz token ile erisim denendi!")
            return jsonify({"message":"gecersiz token!"}),401
        return f(current_user_id,*args, **kwargs)
    return decorated

@auth_bp.route("/register" , methods=["POST"])
def register():
    """
    Yeni kullanici kaydi olusturur
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            nm:
              type: string
              example: "ahmet123"
            email:
              type: string
              example: "ahmet@mail.com"
            password:
              type: string
              example: "sifre123"
    responses:
      201:
        description: Kayit başaili
    """
    data = request.get_json()
    if not data:
        return jsonify({"message":"JSON verisi bulunamadi"}),400
    
    user_name=data.get("nm")
    user_email=data.get("email")
    raw_password=data.get("password")

    if not user_name or not user_email or not raw_password:
        return jsonify({"message":"Eksik bilgi gonderdiniz"}),400
    hashed_pw=generate_password_hash(raw_password, method='pbkdf2:sha256')

    new_user=users(name=user_name,email=user_email, password=hashed_pw)
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message":"kayit basarili,simdi giris yapabilirsiniz"}),201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message":f"kayit sirasinda hata oldu:{str(e)}"}),500   
    
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Kullanici girişi yapar ve JWT döner
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            nm:
              type: string
              example: "kullanici_adi"
            password:
              type: string
              example: "123456"
    responses:
      200:
        description: Başarili giriş, tokenlar döner
      401:
        description: Hatali kimlik bilgileri
    """
    data =request.get_json()
    user_input=data.get("nm")
    password_input=data.get("password")
    found_user = users.query.filter_by(name=user_input).first()
    
    if found_user and check_password_hash(found_user.password,password_input):
        token =jwt.encode({
            'user_id': found_user._id,
            'exp':
datetime.datetime.utcnow() +
datetime.timedelta(minutes=15)
    }, current_app.config["SECRET_KEY"],algorithm="HS256")
        refresh_token = jwt.encode({
            'user_id' : found_user._id,
            'exp':
datetime.datetime.utcnow() +
datetime.timedelta(days=7)
     }, current_app.config["SECRET_KEY"],algorithm="HS256")
        
        found_user.refresh_token = refresh_token
        db.session.commit()

        return jsonify({
         "access_token":token,
         "refresh_token":refresh_token
        }),200
    return jsonify({"message":"hatali kullanici adi veya sifre!"}),401

@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    """
    Refresh token kullanarak yeni Access Token alir
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            refresh_token:
              type: string
              description: Kullanicinin login sirasinda aldigi refresh token
              example: "eyJhbGciOiJIUzI1Ni..."
    responses:
      200:
        description: Yeni access token basariyla olusturuldu
      401:
        description: Gecersiz veya suresi dolmus refresh token
    """
    data = request.get_json()
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        return jsonify({"message": "Refresh token gerekli!"}), 400

    try:
        decoded = jwt.decode(refresh_token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        user_id = decoded.get('user_id')
 
        user = users.query.filter_by(_id=user_id).first()
        
        if not user:
            return jsonify({"message": "Kullanici bulunamadi!"}), 401

        if user.refresh_token != refresh_token:
            return jsonify({"message": "Token eslesme hatasi!"}), 401
       
        new_access_token = jwt.encode({
            'user_id': user._id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({"access_token": new_access_token}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Refresh token suresi dolmus!"}), 401
    except Exception as e:
        return jsonify({"message": f"Teknik hata: {str(e)}"}), 500

@auth_bp.route("/me", methods=["GET"])
@token_required
def get_me(current_user_id):
    """
    Giriş yapan kullanicinin kendi bilgilerini getirir
    ---
    security:
      - Bearer: []
    responses:
      200:
        description: Kullanici bilgileri
      401:
        description: Yetkisiz erişim
    """
    user = users.query.get(current_user_id)
    return jsonify({
        "id": user._id,
        "name": user.name,
        "email": user.email
    }), 200


@auth_bp.route("/logout", methods=["POST"])
@token_required
def logout(current_user_id):
    """
    Kullanici çikiş yapar ve refresh token'i veritabanindan siler
    ---
    security:
      - Bearer: []
    responses:
      200:
        description: Başariyla çikiş yapildi, refresh token silindi
    """
    user = users.query.get(current_user_id)
    if user:
        user.refresh_token = None
        db.session.commit()
    return jsonify({"message":"basariyla cikis yapildi, refresh token silindi."}),200

