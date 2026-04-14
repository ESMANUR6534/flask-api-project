#  Flask E-Ticaret Backend Projesi

Bu proje, bir staj kapsamında geliştirilen; kullanıcı yetkilendirme (JWT) ve ürün yönetimi (CRUD) işlemlerini içeren bir REST API çalışmasıdır.

## 🛠 Kullanılan Teknolojiler
* **Python** & **Flask**
* **SQLAlchemy** (Veritabanı Yönetimi)
* **PyJWT** (Token Tabanlı Güvenlik)
* **Thunder Client** (API Testleri)

## temel Özellikler! (<Ekran görüntüsü 2026-03-24 125738.png>)
-  Kullanıcı Kaydı ve Giriş İşlemleri
-  JWT Token ile Güvenli Erişim
-  Ürün Listeleme ve Ekleme
- ürün silme(API)
-  Ürün Güncelleme (Update API) -> 
- Hata yönetimi


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
* **Hata Düzeltme:** `register` fonksiyonundaki girintileme (indentation) sorunları giderildi ve verilerin JSON formatında doğru okunması sağlandı.
* **Veritabanı Güncellemesi:** Kullanıcı kayıt ve login işlemleri SQLAlchemy üzerinden `instance/users.sqlite3` veritabanı ile senkronize edildi.
* **Güvenlik:** Şifreler `werkzeug.security` kullanılarak hash'lendi.

## API Testleri ve Sonuçlar

Projenin tüm temel fonksiyonları Postman üzerinden başarıyla test edilmiştir. Teknik kısıtlamalar nedeniyle koleksiyon dosyası yerine test sonuçları ekran görüntüleri ile belgelenmiştir.

### 1. Kullanıcı Kaydı (Register)
`POST /register` endpoint'i üzerinden yeni kullanıcı oluşturulmaktadır.
* **Girdi:** `nm`, `email`, `password` (JSON)
* **Sonuç:** Kullanıcı başarıyla veritabanına kaydedilmektedir.

### 2. Kullanıcı Girişi (Login)
`POST /login` endpoint'i ile kimlik doğrulaması yapılmaktadır.
* **Sonuç:** Başarılı giriş sonrası `access_token` üretilmektedir.

### 3. Profil Bilgileri (Me)
`GET /me` endpoint'i, Bearer Token doğrulaması ile çalışmaktadır.
* **Sonuç:** Token ile yapılan isteklerde kullanıcıya ait `id`, `name` ve `email` bilgileri başarıyla dönmektedir.

---

### Test Ekran Görüntüleri
Aşağıdaki görseller, API'nın çalışma durumunu kanıtlamaktadır:

#### /me Endpoint Test Sonucu
![Postman Me Test Sonucu](<test.png>)
3. Uygulamayı başlatın: `python main.py`
