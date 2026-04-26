# Projegoruntuisleme

## 🖐️ AirDraw: Hand Tracking Drawing App v2
AirDraw, bilgisayarınızın kamerasını kullanarak sadece el hareketlerinizle havada çizim yapmanıza olanak tanıyan, bilgisayarlı görü (Computer Vision) tabanlı interaktif bir sanat uygulamasıdır. MediaPipe ve OpenCV kütüphaneleri kullanılarak geliştirilmiştir.

## ✨ Öne Çıkan Özellikler
- Çift El Desteği: Aynı anda iki elinizle çizim yapabilir veya kontrol sağlayabilirsiniz.

- Dinamik Silgi: Elinizi avuç içi açık şekilde gösterdiğinizde, el boyutunuza göre otomatik büyüyen bir silgi aktif olur.

- Geometrik Şekiller: Sadece serbest çizim değil; Doğru, Daire, Dikdörtgen ve Üçgen modları mevcuttur.

- Gelişmiş Kullanıcı Arayüzü: Metalik yazı efektleri, dinamik renk paleti ve işlem bildirimleri (Toast mesajları).

- Geri Al & Kaydet: Hatalarınızı geri alabilir (Z), çalışmalarınızı PNG olarak kaydedebilirsiniz (S).

## 🎮 Kontroller ve Kullanım
## 🖐️ El Jestleri (İki El İçin de Geçerli)
-    Jest                            |     Eylem
* 1 Parmak (İşaret)               |        Çizim yapar (Serbest Çizim modunda).
* 2 Parmak (İşaret + Orta)        |        Üst şerit üzerinde renk veya silgi seçimi yapar.
* Başparmak + İşaret Parmağı      |       Şekil modlarında (Daire, Kare vb.) boyut/yer belirler."
* Açık Avuç (Orta Parmak Kalkık)  |     Silgi modunda daha geniş bir alanı temizlemek için kullanılır.

## ⌨️ Klavye Kısayolları
- 0 - 4 : Çizim modlarını değiştirir (Serbest, Çizgi, Daire, Dikdörtgen, Üçgen).
- SPACE : Belirlenen şekli tuvale onaylar (şekil modlarındayken).
- S : Çizimi drawings/ klasörüne tarih-saat ismiyle kaydeder.
- Z : Yapılan son işlemi geri alır.
- C : Tüm ekranı temizler.
- + / - : Kalem kalınlığını artırır veya azaltır.
- Q : Uygulamadan çıkış yapar.

## 🚀 Teknik Detaylar
Bu proje aşağıdaki teknolojileri kullanarak gerçek zamanlı görüntü işleme yapar:

- MediaPipe Hands: El üzerindeki 21 farklı eklem noktasını (landmark) milisaniyeler içinde tespit eder.
- OpenCV: Kamera görüntüsünü işler, çizim katmanını (canvas) oluşturur ve maskeleme yöntemiyle görüntüyü birleştirir.
- NumPy: Matris operasyonları ile çizim verilerini yönetir.

  
