# XXX Vakfı Bağış Platformu

Bu proje, **çevrimiçi bağışları kolay ve güvenli bir şekilde yönetmeyi** amaçlayan bir bağış platformudur. Kullanıcılar platform üzerinden kampanyalar oluşturabilir ve istedikleri kampanyalara bağışta bulunabilirler.

Bağış süreci şu şekilde işler:
- Yapılan bağışlar **webhook** ile doğrulanır.
- Bağış doğrulandıktan sonra **PDF formatında makbuz** oluşturulur ve bağışçının e-posta adresine gönderilir.
- Doğrulanan tüm bağışlar **anlık olarak** ve **istatistiksel olarak** HTML tabanlı frontend arayüzünde görüntülenir.

##  Mimari Özet
Flask Blueprint yapısını kullanarak authentication, kampanya ve bağış işlemlerini modüler hale getirdim.
Marshmallow şemaları ile request body doğrulaması yaptım, SQLAlchemy ORM veritabanı kullanarak kodun okunabilirliği ve güncellenebilirliğini sağladım  ve Flask-Caching ile sık kullanılan kampanya verilerine erişim sağladım.
Kampanyaların bağış istatistiklerini (tutar ve adet) cache üzerinde tutarak veritabanına yük oluşturmadan anlık olarak ilettim.
Ödeme sağlayıcısından gelen webhook isteklerinin doğrulamasını HMAC ile yaparak güvenli bir entegrasyon sağladım.

### 1- Web Uygulaması Backend,Frontend(Html) API endpointleri
- Authentication işlemleri
- Kampanya oluşturma ve yönetme
- Bağış yapma ve doğrulama
- PDF makbuz oluşturma ve e-posta ile gönderme
- Anlık ve istatistiksel bağış görüntüleme

| Endpoint         | Yöntem | Açıklama                                      |
| ---------------- | ------ | --------------------------------------------- |
| `/auth/register`      | POST   | Yeni üye kaydı oluşturur |
| `/auth/login` | GET    | Üyenin giriş yapması için access_token ve refresh_token döner | 
| `/auth/refresh`   | GET    | Giriş yaptıktan gerektiği durumda refresh_token ile access_token döner|
| `/auth/logout`   | GET    | refresh_token'ı geçersiz sayarak logout işlemi yapar.
| `/api/campaigns`   | POST   | Kampanya oluşturur.
| `/api/campaigns`   | GET    | Kampanyaların listesini döner.
| `/api/campaigns/:id`   | GET    | Kampanyanın detayını döner.
| `/api/campaigns/:id`   | PUT    | Kampanyanın detayını günceller.
| `/api/campaigns/:id`   | DELETE    | Kampanyayı siler.
| `/api/donation`   | POST    | Kampanyaya bağış yapmak için kullanılır.
| `/api/donation/webhook`   | POST    | Ödeme sağlayıcısından gelen webhook doğrulama için kullanılır.
### 2- Worker
- Yapılan bağışın makbuzu oluşturulup mail'e gönderilmesi için asyncio ve aio_pika kullanarak asenkron bir RabbitMQ worker’ı tasarladım.
- Bağış webhook ile doğrulandıktan sonra kuyruğa yazılıyor, sonrasında async olarak pdf ve email işlemleri yapılıyor.

##  Gereksinimler
- Redis Server
- RabbitMQ Server
- MySQL Server
- `requirements.txt` dosyasındaki Python paketleri

##  Kurulum Adımları
### 1- Klonlama
```bash
- git clone https://github.com/Gurkanaydn/donation-platform-flask.git
```
### 3- Mysql veritabanı kurulumu
```bash
- mysql -u <kullanici_adi> -p donation_platform < schema.sql
```
### 3- Paket kurumları
```bash
- python3 -m venv venv
- source venv/bin/activate
- pip3 install -r requirements.txt
```
### 4- Projenin backend'inin çalıştırılması
```bash
python3 run.py
```
### 5- Projenin worker'ının çalıştırılması
```bash
python3 worker/worker.py
```

## ENV DEĞİŞKENLERİ
| Değişken ismi         | Açıklama|
| ---------------- | ------ | 
| `DB_USER`        | Veritabanı kullanıcı adı. |
| `DB_PASSWORD`        | Veritabanı kullanıcı şifresi. |
| `DB_HOST`        | Veritabanı adresi. |
| `DB_NAME`        | Veritabanı ismi. |
| `JWT_SECRET_KEY`        | JWT key'i. |
| `WEBHOOK_SECRET`        | Webhook key'i. |
| `SMTP_SERVER`        | Smtp server adresi. |
| `SMTP_PORT`        | Smtp server portu. |
| `SMTP_SENDER`        | E-Mail'i gönderecek kişinin mail adresi. |
| `SMTP_PASSWORD`        | E- Mail'i gönderecek kişinin şifresi. |
| `REDIS_HOST`        | E- Mail'i gönderecek kişinin şifresi. |
| `REDIS_PORT`        | E- Mail'i gönderecek kişinin şifresi. |
| `RABBITMQ_USER`        | Rabbitmq kullanıcı adı. |
| `RABBITMQ_PASSWORD`        | Rabbitmq kullanıcı şifresi. |
| `RABBITMQ_HOST`        | Rabbitmq server adresi. |


## Test
- python3 -m unittest tests/integration/test_full_process.py