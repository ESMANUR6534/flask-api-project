import jwt
import datetime
from functools import wraps
from flask import Flask, redirect, url_for, render_template, request, flash,make_response 
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask import jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'esmanur_staj_projesi_cok_gizli_anahtar_123456'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100),unique=True, nullable=False)
    email = db.Column(db.String(100))
    password=db.Column(db.String(255),nullable=False)
    products=db.relationship('Product',backref='owner',lazy=True)
 
    def __init__(self, name, email,password):
        self.name = name
        self.email = email
        self.password= password

class Product(db.Model):
    product_id=db.Column("id",db.Integer,primary_key=True)
    product_name =db.Column(db.String(100), nullable=False)
    product_price =db.Column(db.Integer)
    created_by=db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


def token_required(f):
    
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('access_token')
        if not token:
            flash("Giriş yapmadiniz!")
            return redirect(url_for('login'))

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'] ,algorithms=["HS256"])
            current_user = data['user_id']
        except:
            flash("Oturum süresi dolmuş veya geçersiz!")
            return redirect(url_for('login'))

        return f(current_user, *args, **kwargs)

    return decorated

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/view")
def view():
    return render_template("view.html", values=users.query.all())

@app.route("/login", methods=["POST", "GET"])
def login():
    token = request.cookies.get('access_token')
    if token:
        try:
            jwt.decode(token,app.config['SECRET_KEY'] ,algorithms=["HS256"])
            return redirect(url_for("user"))
        except:
            pass
    if request.method == "POST":
        user_input = request.form["nm"]
        password_input=request.form["password"]
        found_user = users.query.filter_by(name=user_input).first()
        
        if found_user and check_password_hash(found_user.password,password_input):
                
            token = jwt.encode({
                'user_id': found_user._id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            }, app.config['SECRET_KEY']  ,algorithm="HS256")

            flash("Giriş başarili!")
            resp = make_response(redirect(url_for("user")))
            resp.set_cookie('access_token', token, httponly=True)
            return resp
        
        else:
            flash("Hatali kullanici adi veya sifre!")
            return redirect(url_for("login"))
    return render_template("login.html")
       

@app.route("/user", methods=["POST", "GET"])
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


@app.route("/register" , methods=["POST", "GET"])
def register():

    if request.method=="POST":
        user_name=request.form["nm"]
        user_email=request.form["email"]
        raw_password=request.form["password"]
        hashed_pw=generate_password_hash(raw_password, method='pbkdf2:sha256')

        new_user=users(name=user_name,email=user_email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash("kayit basarili,simdi giris yapabilirsiniz")
        return redirect(url_for("login"))
    return render_template("register.html")
    

@app.route("/logout")
def logout():
    flash("Çikis yapildi!", "info")
    resp = make_response(redirect(url_for("login")))
    resp.set_cookie('access_token', '', expires=0) 
    return resp

@app.route("/delete_product/<int:id>",methods=["POST","DELETE"])
@token_required
def delete_product(current_user, id):
    product=product.quey.get(id)
    if not product:
        return jsonify({"message":"urun bulunamadi!","status":"error"}),404
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message":"Ürün başariyla silindi!","status":"success","deleted_id":"id"}),200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True,host='0.0.0.0')

