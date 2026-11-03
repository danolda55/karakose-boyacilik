# Karaköse Boyacılık web sitesi

Samsun Atakum boyacı sitesi (statik HTML). `main` dalına yapılan her değişiklik GitHub Actions ile FTP üzerinden cPanel'deki `public_html` klasörüne otomatik yüklenir.

Gerekli repo secret'ları: `FTP_SERVER`, `FTP_USERNAME`, `FTP_PASSWORD`.
FTP hesabı doğrudan `public_html` klasörüne açılıyorsa repo değişkeni `FTP_SERVER_DIR` = `./` olarak ayarlanır.
