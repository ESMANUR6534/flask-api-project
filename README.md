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
2.çevresel değişiklikleri ayarlayın:SECRET_KEY=gizli_anahtariniz DATABASE_URL=sqlite:///instance/users.sqlite3
3. Uygulamayı başlatın: `python main.py`
