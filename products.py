from flask import Blueprint, request, jsonify
from models import db, users, Product
from auth import token_required

product_bp = Blueprint('product', __name__)


@product_bp.route("/product",methods=["POST"])
@token_required
def add_product(current_user_id):
    """
    Yeni bir ürün ekler
    ---
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            name:
              type: string
              example: "Masa"
            price:
              type: number
              example: 450.00
    responses:
      201:
        description: Ürün başariyla eklendi
      400:
        description: Geçersiz veri girişi
    """
         
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

@product_bp.route("/products",methods=["GET"])
def list_products():
    """
    Ürünleri listeler ve filtreler
    ---
    parameters:
      - name: category
        in: query
        type: string
      - name: min_price
        in: query
        type: number
      - name: page
        in: query
        type: integer
        default: 1
    responses:
      200:
        description: Ürün listesi döner
    """
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

@product_bp.route("/product/<int:id>", methods=["PATCH"])
@token_required
def update_product(current_user_id,id):
    """
    Mevcut bir ürünü günceller
    ---
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Güncellenecek ürünün ID'si
      - name: body
        in: body
        required: true
        schema:
          properties:
            name:
              type: string
              example: "Güncellenmiş Masa"
            price:
              type: number
              example: 550.00
    responses:
      200:
        description: Ürün başariyla güncellendi
      404:
        description: Ürün bulunamadi
    """
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


@product_bp.route("/delete_product/<int:id>",methods=["DELETE"])
@token_required
def delete_product(current_user_id,id):
    """
    Ürünü siler
    ---
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Silme başarili
    """
    product=Product.query.get(id)
    if not product:
        return jsonify({"message":"urun bulunamadi!","status":"error"}),404
    
    if product.created_by != current_user_id:
        return jsonify({"message":"bu urunu silme yetkiniz yok!","status":"error"}), 403
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message":"Ürün başariyla silindi!","status":"success","deleted_id":id}),200
