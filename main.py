import os
from dotenv import load_dotenv
load_dotenv()
import jwt
import datetime
from functools import wraps
from flask import Flask, redirect, url_for, render_template, request, flash,make_response 
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask import jsonify
from werkzeug.exceptions import HTTPException


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['JWT_SECRET_KEY']=os.getenv('JWT_SECRET_KEY')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100),unique=True, nullable=False)
    email = db.Column(db.String(100))
    password=db.Column(db.String(255),nullable=False)
    refresh_token=db.Column(db.String(255),nullable=True)
    products=db.relationship('Product',backref='owner',lazy=True)
 
    def __init__(self, name, email,password):
        self.name = name
        self.email = email
        self.password= password

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
            data = jwt.decode(token,app.config['SECRET_KEY'],algorithms=["HS256"])
            current_user_id = data["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"message":"Token suresi dolmus!"}),401
        except jwt.InvalidTokenError:
            return jsonify({"message":"gecersiz token!"}),401
        return f(current_user_id,*args, **kwargs)
    return decorated
 

class Product(db.Model):
    product_id=db.Column("id",db.Integer,primary_key=True)
    product_name =db.Column(db.String(100), nullable=False)
    product_price =db.Column(db.Float)
    category = db.Column(db.String(50))
    created_by=db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return jsonify({"status":"error","message":e.description}),e.code
    return jsonify({"status":"error","message":"sunucu hatasi olustu!"}),500

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/view")
def view():
    return render_template("view.html", values=users.query.all())

@app.route("/product/<int:id>", methods=["PATCH"])
@token_required
def update_product(current_user_id,id):
    data = request.get_json()
    product = Product.query.filter_by(product_id=id).first()
    
    if not product:
        return jsonify({"message": "Urun bulunamadi!", "status": "error"}), 404

    if product.created_by != current_user_id:
        return jsonify({"message": "Bu urunu guncelleme yetkiniz yok!", "status": "error"}), 403

    
    try:
        if "name" in data:
            product.product_name = data["name"]
        if "price" in data:
            product.product_price = data["price"]
 
        db.session.commit()
        return jsonify({
            "message": "Urun basariyla guncellendi","status": "success" }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Hata:{str(e)}"}), 500

@app.route("/login", methods=["POST"])
def login():
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
    }, app.config["SECRET_KEY"],algorithm="HS256")
        refresh_token = jwt.encode({
            'user_id' : found_user._id,
            'exp':
datetime.datetime.utcnow() +
datetime.timedelta(days=7)
     }, app.config["SECRET_KEY"],algorithm="HS256")
        
        found_user.refresh_token = refresh_token
        db.session.commit()

        return jsonify({
         "access_token":token,
         "refresh_token":refresh_token
        }),200
    return jsonify({"message":"hatali kullanici adi veya sifre!"}),401

@app.route("/refresh", methods=["POST"])
def refresh():
    data = request.get_json()
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        return jsonify({"message": "Refresh token gerekli!"}), 400

    try:
        decoded = jwt.decode(refresh_token, app.config['SECRET_KEY'], algorithms=["HS256"])
        user_id = decoded['user_id']
        
        user = users.query.get(user_id)
        if not user or user.refresh_token != refresh_token:
            return jsonify({"message": "Gecersiz refresh token!"}), 401

        new_access_token = jwt.encode({
            'user_id': user._id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({"access_token": new_access_token}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Refresh token suresi dolmus, tekrar giris yapin!"}), 401
    except:
        return jsonify({"message": "Gecersiz islem!"}), 401
     

@app.route("/user", methods=["POST","GET"])
@token_required
def user(current_user):
    found_user = users.query.filter_by(_id=current_user).first()
    email = None

    if request.method == "POST":
        email = request.form["email"]
        if found_user:
            found_user.email = email
            db.session.commit()
            flash("E-posta kaydedildi")
            return redirect(url_for("add_product"))
    if found_user:
        email = found_user.email 
    return render_template("user.html", email=email)

@app.route("/product",methods=["POST"])
@token_required
def add_product(current_user_id):
     data= request.get_json()
     if not data :
         return jsonify({"message":"veri gönderilmedi","status":"error"}),400
     product_name=data.get("name")
     product_price=data.get("price")

     if not product_name or not product_price:
        return jsonify({"message":"urun adi ve fiyat bos birakilamaz","status":"error"}),400
     try:
        product_price=float(product_price)
        if product_price <=0:
            return jsonify({"message":"fiyat 0'dan buyuk olmalidir!","status":"error"}),400
     except (ValueError,TypeError):
        return jsonify({"message":"fiyat gecerli bir sayi olmalidir!","status":"error"}),400
    
     new_product=Product(product_name=product_name,product_price=product_price,created_by=current_user_id)
     db.session.add(new_product)
     db.session.commit()

     return jsonify({"message":"urun basariyla eklendi","status":"success","product":{"name":product_name,"price":product_price}}),201

@app.route("/products",methods=["GET"])
def list_products():
    category =request.args.get('category')
    min_price=request.args.get('min_price',type=float)
    max_price=request.args.get('max_price',type=float)

    page = request.args.get('page' ,1, type=int)
    per_page =request.args.get('per_page' ,10, type=int)

    query=Product.query

    if category:
        query=query.filter_by(category=category)
    if min_price is not None:
        query=query.filter(Product.product_price >= min_price)
    if max_price is not None:
        query=query.filter(Product.product_price <= max_price)
     
    paginated_data = query.paginate(page=page,per_page=per_page,error_out=False)

    output=[]
    for p in paginated_data.items:
        output.append({
            "id":p.product_id,
            "name":p.product_name,
            "price":p.product_price,
            "category":p.category
        })
    return jsonify({
        "products":output,
        "total":paginated_data.total,
        "pages":paginated_data.pages,
        "current_page":paginated_data.page
        }),200

@app.route("/register" , methods=["POST"])
def register():
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

@app.route("/logout")
def logout():
    return jsonify({"message":"basariyla cikis yapildi.lutfen istemci tarafindaki tokeni silin."}),200

@app.route("/delete_product/<int:id>",methods=["POST","DELETE"])
@token_required
def delete_product(current_user_id,id):
    product=Product.query.get(id)
    if not product:
        return jsonify({"message":"urun bulunamadi!","status":"error"}),404
    
    if product.created_by != current_user_id:
        return jsonify({"message":"bu urunu silme yetkiniz yok!","status":"error"}), 403
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message":"Ürün başariyla silindi!","status":"success","deleted_id":id}),200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True,host='0.0.0.0')

