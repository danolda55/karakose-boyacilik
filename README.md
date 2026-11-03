# Karaköse Boyacılık web sitesi

Samsun Atakum boyacı sitesi (statik HTML). `main` dalına yapılan her değişiklik GitHub Actions ile FTP üzerinden cPanel'deki `public_html` klasörüne otomatik yüklenir. FTP hesabının dizini sitenin kök klasörü (xn--karakseboyaclk-zpb56gba.com.tr) olmalıdır.

Gerekli repo secret'ları: `FTP_SERVER`, `FTP_USERNAME`, `FTP_PASSWORD`.
Farklı bir hedef klasör gerekiyorsa repo değişkeni `FTP_SERVER_DIR` ile ayarlanır.
