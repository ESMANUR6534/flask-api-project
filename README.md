# Flask JWT Auth & Docker Project 🚀

Bu proje, staj sürecimin ilk haftasında geliştirdiğim; güvenli kimlik doğrulama (JWT), veritabanı yönetimi (SQLAlchemy) ve modern dağıtım (Docker) standartlarını içeren bir web uygulamasıdır.

## 🛠️ Özellikler
- **JWT (JSON Web Token):** Güvenli oturum yönetimi ve çerez tabanlı kimlik doğrulama.
- **Password Hashing:** Kullanıcı şifreleri veritabanında güvenli bir şekilde saklanır.
- **SQLAlchemy:** SQLite veritabanı ile kullanıcı verileri yönetimi.
- **Dockerize:** Uygulama, Docker konteyneri sayesinde her ortamda tek komutla çalışabilir.

## 🐳 Docker ile Çalıştırma
Sisteminize Docker kuruluysa şu komutlarla projeyi ayağa kaldırabilirsiniz:

1. İmajı oluşturun:
```bash
docker build -t flask-staj-projesi .