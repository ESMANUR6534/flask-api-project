#  Flask E-Ticaret Backend Projesi

Bu proje, bir staj kapsamında geliştirilen; kullanıcı yetkilendirme (JWT) ve ürün yönetimi (CRUD) işlemlerini içeren bir REST API çalışmasıdır.

## 🛠 Kullanılan Teknolojiler
* **Python** & **Flask**
* **SQLAlchemy** (Veritabanı Yönetimi)
* **PyJWT** (Token Tabanlı Güvenlik)
* **Thunder Client** (API Testleri)
* **Pytest** (Otomatik Birim ve Entegrasyon Testleri)
* **Flasgger** (Swagger UI ile İnteraktif API Dokümantasyonu)

## temel Özellikler! (<Ekran görüntüsü 2026-03-24 125738.png>)
-Güvenli Yetkilendirme: JWT tabanlı access_token ve refresh_token mekanizması.
-İlişkisel Veritabanı: Kullanıcılar ve ürünler arasında ForeignKey ile kurulan bire-çok (One-to-Many) ilişki.
-Kapsamlı Ürün Yönetimi (CRUD): Ürün ekleme, listeleme, güncelleme ve silme.
-Otomatik Testler: Pytest ile hem başarılı hem de hatalı (fail) senaryoların test edilmesi.
-Hata Yönetimi: Merkezi hata yakalama sistemi (handle_exception).i


##  Başlangıç
Projeyi yerelinizde çalıştırmak için:
1. Bağımlılıkları yükleyin: `pip install -r requirements.txt`


### 2. Çevresel Değişkenleri Ayarlayın
Ana dizinde bir `.env` dosyası oluşturun ve aşağıdaki değişkenleri tanımlayın:
```env
SECRET_KEY=sizin_gizli_anahtariniz
SQLALCHEMY_DATABASE=sqlite:///users.sqlite3
JWT_SECRET_KEY=jwt_ozel_anahtariniz
DEBUG=True

## Son Yapılan Düzenlemeler
***Veritabanı Mimarisi: database_models.py içerisinde ForeignKey('users.id') düzeltmesi yapılarak ürünlerin kullanıcılarla ilişkisi stabilize edildi.***
***Kod Standardı: Tüm API endpointleri için Swagger (OpenAPI) dokümantasyonu tamamlandı.***
***Docker Hazırlığı: requirements.txt dosyasındaki karakter kodlaması (UTF-16 -> UTF-8) ve sürüm yazım hataları giderildi.***

## API Testleri ve Sonuçlar

Test Senaryosu,Endpoint,Beklenen HTTP Kodu,Durum
Başarılı Kullanıcı Kaydı,POST /register,201,✅ Geçti
Eksik Veriyle Kayıt Denemesi,POST /register,400,✅ Geçti
Başarılı Kullanıcı Girişi,POST /login,200,✅ Geçti
Yanlış Şifre/Kullanıcı ile Giriş,POST /login,401,✅ Geçti
Yetkili Ürün Ekleme,POST /product,201,✅ Geçti
Yetkisiz Ürün Ekleme Denemesi,POST /product,401,✅ Geçti
Başarılı Ürün Silme,DELETE /product/1,200,✅ Geçti
Olmayan Ürünü Silme Denemesi,DELETE /product/999,404,✅ Geçti

### Test Ekran Görüntüleri
Aşağıdaki görseller, API'nın çalışma durumunu kanıtlamaktadır:

#### /me Endpoint Test Sonucu
![Postman Me Test Sonucu](<test.png>)
3. Uygulamayı başlatın: `python main.py`
