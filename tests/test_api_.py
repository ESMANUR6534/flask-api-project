import pytest
from main import app
from database_models import db, users, Product

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_register_success(client):
    """Başarili Kayit: Tüm alanlar doğru."""
    response = client.post('/register', json={"nm": "esma", "email": "esma@test.com", "password": "123"})
    assert response.status_code == 201

def test_register_fail_missing_field(client):
    """Başarisiz Kayit: Eksik alan (nm yok)."""
    response = client.post('/register', json={"email": "esma@test.com", "password": "123"})
    assert response.status_code == 400

def test_login_success(client):
    """Başarili Giriş: Doğru bilgiler."""
    client.post('/register', json={"nm": "esma", "email": "e@t.com", "password": "123"})
    response = client.post('/login', json={"nm": "esma", "password": "123"})
    assert response.status_code == 200
    assert "access_token" in response.get_json()

def test_login_fail_wrong_password(client):
    """Başarisiz Giriş: Yanliş şifre."""
    client.post('/register', json={"nm": "esma", "email": "e@t.com", "password": "123"})
    response = client.post('/login', json={"nm": "esma", "password": "yanlis_sifre"})
    assert response.status_code == 401

def test_add_product_success(client):
    """Başarili Ürün Ekleme: Geçerli token ve veri."""
    client.post('/register', json={"nm": "esma", "email": "e@t.com", "password": "123"})
    login_res = client.post('/login', json={"nm": "esma", "password": "123"})
    token = login_res.get_json()['access_token']
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post('/product', headers=headers, json={"name": "Klavye", "price": 500})
    assert response.status_code == 201

def test_add_product_fail_unauthorized(client):
    """Başarisiz Ürün Ekleme: Token yok."""
    response = client.post('/product', json={"name": "Fare", "price": 200})
    assert response.status_code == 401

def test_delete_product_success(client):
    """Başarili Ürün Silme: Ürün var ve kullanici yetkili."""
    # Kayıt ve Login
    client.post('/register', json={"nm": "esma", "email": "e@t.com", "password": "123"})
    token = client.post('/login', json={"nm": "esma", "password": "123"}).get_json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    client.post('/product', headers=headers, json={"name": "Monitor", "price": 3000})

    response = client.delete('/product/1', headers=headers)
    assert response.status_code == 200

def test_delete_product_fail_not_found(client):
    """Başarisiz Ürün Silme: Olmayan ürün ID'si (999)."""
    client.post('/register', json={"nm": "esma", "email": "e@t.com", "password": "123"})
    token = client.post('/login', json={"nm": "esma", "password": "123"}).get_json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.delete('/product/999', headers=headers)
    assert response.status_code == 404