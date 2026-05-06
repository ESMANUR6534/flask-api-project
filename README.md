#  Flask E-Ticaret Backend Projesi

Bu proje, bir staj kapsamında geliştirilen; modern yazılım standartlarına (CI/CD, Docker, Loglama) uygun, JWT tabanlı yetkilendirme ve ilişkisel veritabanı yönetimini içeren kapsamlı bir REST API çalışmasıdır.

## 🛠 Kullanılan TPython** & **Flask**
* Backend: Python & Flask
* Veritabanı: SQLAlchemy (SQLite ile ilişkisel modelleme)
* Güvenlik: PyJWT (Access & Refresh Token) ve Werkzeug Password Hashing
* Test: Pytest (Birim ve Entegrasyon Testleri)
* Otomasyon: GitHub Actions (CI/CD Pipeline)
* Konteynerleştirme: Docker
* Dokümantasyon: Flasgger (Swagger UI)

## temel Özellikler! (<Ekran görüntüsü 2026-03-24 125738.png>)
* Gelişmiş Yetkilendirme: JWT tabanlı access_token ve refresh_token mekanizması.
* İlişkisel Veritabanı: Kullanıcılar ve ürünler arasında ForeignKey ile kurulan bire-çok (One-to-Many) ilişki.
* Merkezi Loglama: Hatalı giriş denemeleri ve sistem hatalarının app.log dosyasına otomatik kaydedilmesi.
* Hata Yönetimi: Tüm hataları yakalayan ve kullanıcıya temiz JSON dönen merkezi sistem.

## CI/CD ve Otomasyon
Bu projede GitHub Actions kullanılarak profesyonel bir hat (pipeline) kurulmuştur:
* Otomatik Test: Her push işleminde Pytest senaryoları otomatik çalışır.
* Docker Build: Testler geçerse, projenin Docker imajı başarıyla derlenip derlenmediği kontrol edilir.

##  Başlangıç
Projeyi yerelinizde çalıştırmak için:
1. Bağımlılıkları yükleyin: `pip install -r requirements.txt`
2. uygulamayı başlatın: `python main.py`
* Docker ile çalıştırma:
Imaj oluşturma:`docker build -t flask-api-app` 
Çalıştırma:`docker run -p 5000:5000 flask-api-app`


### 2. Çevresel Değişkenleri Ayarlayın
Ana dizinde bir `.env` dosyası oluşturun ve aşağıdaki değişkenleri tanımlayın:
```env
SECRET_KEY=sizin_gizli_anahtariniz
SQLALCHEMY_DATABASE=sqlite:///users.sqlite3
JWT_SECRET_KEY=jwt_ozel_anahtariniz
DEBUG=True

### Son Yapılan Düzenlemeler
* Kod Standartları: Dairesel import (circular import) hataları database_models.py ayrıştırılarak giderildi.
* Dosya Güvenliği: .gitignore eklenerek hassas log (app.log) ve cache dosyalarının sızması engellendi.
* Dokümantasyon: Tüm API uç noktaları için Swagger UI üzerinden interaktif test imkanı sağlandı.

##  API Testleri ve Sonuçlar 

Test Senaryosu,Endpoint,Beklenen HTTP Kodu,Durum
Başarılı Kullanıcı Kaydı,POST /register,201,✅ Geçti
Eksik Veriyle Kayıt Denemesi,POST /register,400,✅ Geçti
Başarılı Kullanıcı Girişi,POST /login,200,✅ Geçti
Yanlış Şifre/Kullanıcı ile Giriş,POST /login,401,✅ Geçti
Yetkili Ürün Ekleme,POST /product,201,✅ Geçti
Yetkisiz Ürün Ekleme Denemesi,POST /product,401,✅ Geçti
Başarılı Ürün Silme,DELETE /product/1,200,✅ Geçti
Olmayan Ürünü Silme Denemesi,DELETE /product/999,404,✅ Geçti

örnek:
#kullanıcı kaydı(Post/Register)
{
    "username:"yeni_kullanici",
    "password":123
}

#ürün ekleme(Post/Product)
{
    "name":"armut",
    "price":89
}

### 3. Uygulamayı başlatın: `python main.py`
