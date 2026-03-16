import jwt
import datetime
from functools import wraps
from flask import Flask, redirect, url_for, render_template, request, flash,make_response ,jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = "cok-gizli-anahtar" 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

    def __init__(self, name, email):
        self.name = name
        self.email = email

class Product(db.Model):
    product_id=db.Column("id",db.Integer,primary_key=True)
    product_name =db.Column(db.String(100))
    product_price =db.Column(db.Integer)
    created_by=db.Column(db.Integer,db.ForeignKey('users.id'))


def token_required(f):
    
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('access_token')
        if not token:
            flash("Giriş yapmadiniz!")
            return redirect(url_for('login'))

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['user']
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
    if request.method == "POST":
        user_input = request.form["nm"]
        
        found_user = users.query.filter_by(name=user_input).first()
        if not found_user:
            usr = users(user_input, "")
            db.session.add(usr)
            db.session.commit()

        token = jwt.encode({
            'user': user_input,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        flash("Giriş başarili!")
        resp = make_response(redirect(url_for("user")))
       
        resp.set_cookie('access_token', token, httponly=True)
        return resp


    token = request.cookies.get('access_token')
    if token:
        return redirect(url_for("user"))
    
    return render_template("login.html")

@app.route("/user", methods=["POST", "GET"])
@token_required
def user(current_user):
    email = None
    found_user = users.query.filter_by(name=current_user).first()

    if request.method == "POST":
        email = request.form["email"]
        if found_user:
            found_user.email = email
            db.session.commit()
            flash("E-posta kaydedildi")
    else:
        email = found_user.email if found_user else None

    return render_template("user.html", email=email)

@app.route("/product",methods=["POST", "GET"])
@app.route("/")
@token_required
def product(current_user):
    
    if request.method=="POST":
        product_name=request.form["name"]
        product_price=request.form["price"]

        new_product=Product(product_name=product_name,product_price=product_price,created_by=current_user)
        db.session.add(new_product)
        db.session.commit()
        flash("ürün basariyla eklendi")
        return redirect(url_for("product"))
    all_products=Product.query.filter_by(created_by=current_user).all()
    return render_template("product.html",products=all_products)

    
@app.route("/register" , methods=["POST", "GET"])
def register():
    if request.method=="POST":
        user_name=request.form["nm"]
        user_email=request.form["email"]
        new_user=users(name=user_name,email=user_email)
        db.session.add(new_user)
        db.session.commit()
        flash("kayit basarili,simdi giris yapabilirsiniz")
        return redirect(url_for("login"))
    return render_template("login.html")
    



@app.route("/logout")
def logout():
    flash("Çikis yapildi!", "info")
    resp = make_response(redirect(url_for("login")))
    resp.set_cookie('access_token', '', expires=0) 
    return resp

@app.route("/delete/<int:id>")
@token_required
def delete_product(current_user,id):
    
    product_to_delete=Product.query.filter_by(product_id=id, created_by=current_user).first()
    if product_to_delete:
        db.session.delete(product_to_delete)
        db.session.commit()
        flash("urun basariyla silindi!")
        return redirect(url_for("product"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True,host='0.0.0.0')

