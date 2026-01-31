# LogGuard: Log Analysis & Monitoring Tool

**LogGuard**, Linux tabanlı sistemler için geliştirilmiş, hafif mimariye sahip, konteynerize edilmiş bir log analiz ve izleme aracıdır. Sistem kayıtlarının statik analizi ve gerçek zamanlı takibi amacıyla tasarlanmıştır.

Proje dış bağımlılıkları minimize ederek Docker üzerinde çalışacak şekilde yapılandırılmıştır.

## Proje Özeti
LogGuard, Linux tabanlı sistemlerdeki karmaşık log verilerini anlamlandırmak ve güvenlik tehditlerini tespit etmek amacıyla geliştirilmiş, Docker mimarisi üzerinde çalışan modüler bir analiz ve izleme aracıdır. Teorik işleyişi bakımından "Adli Bilişim (Forensics)" ve "Aktif Savunma" prensiplerini bir araya getiren yazılım; statik analiz modülüyle geçmişe dönük verileri önceden tanımlanmış tehdit imzalarıyla (pattern matching) karşılaştırarak anomalileri tespit ederken, canlı izleme modülüyle veri akışını gerçek zamanlı (real-time) dinleyerek olası saldırı girişimlerini anında yakalar ve operatöre bildirir. Kullanıcı tarafından yapılandırılabilen harici bir kural setine dayalı olarak çalışan tespit motoru, elde edilen kritik bulguları geçici bellekten kalıcı CSV raporlarına dönüştürerek sistem yöneticilerine sürdürülebilir, kanıta dayalı ve hızlı bir denetim mekanizması sunar.

## Proje Mimarisi
     Dosya     |    Açıklama 
`log_guard.py` | Uygulamanın temel mantığını içeren ana Python modülü. 
`filter_rules.txt` | Tehdit desenlerinin ve etiketlerinin tanımlandığı konfigürasyon dosyası. 
`Dockerfile` | Uygulamanın izole ortamda derlenmesi ve çalıştırılması için gerekli imaj tanımı. 
`scan_results.csv` | Analiz sonuçlarının dışa aktarıldığı rapor dosyası.


## Çalışma Mantığı ve Modüller
LogGuard, kullanıcı etkileşimli bir menü üzerinden yönetilir. Her bir modül, farklı bir siber güvenlik ihtiyacını karşılamak üzere tasarlanmıştır. Aşağıda sistemin teorik işleyişi açıklanmıştır:

### 1. Hedef Log Seçimi (Target Selection)
Bu seçenek, programın **"Gözlem Alanını"** belirler. İşletim sistemleri; kullanıcı girişleri sistem hataları veya ağ trafiği için farklı dosyalar tutar. Bu modül kullanıldığında, LogGuard aktif veri akışını keser ve işaretçisini seçilen yeni dosyaya odaklar. Böylece programı yeniden başlatmaya gerek kalmadan denetim mekanizması farklı bir veri kaynağına yönlendirilmiş olur.

**Önemli Not (Custom Log Paths):** Varsayılan olarak sistemde `/var/log/auth.log`, `/var/log/syslog` gibi standart yollar tanımlıdır. Farklı bir dizindeki veya özel bir uygulamaya ait log dosyasının taranması isteniyorsa kaynak kod içerisindeki `TARGET_LOGS` listesine ilgili dosya yolu manuel olarak eklenmeli ve Docker imajı yeniden derlenmelidir.

### 2. Geçmişe Dönük Tarama (Static Analysis)
Bu modül **"Adli Bilişim"** mantığıyla çalışır. Amaç, geçmişte sistemde bir sızma girişimi veya hata olup olmadığını tespit etmektir. Program seçilen dosyanın tamamını okur ve `filter_rules.txt` dosyasındaki imzalarla karşılaştırır. Eşleşen şüpheli durumlar filtrelenerek geçici belleğe (RAM) kaydedilir.

### 3. Veri Dışa Aktarımı (Data Persistence)
Bu modül, **"Raporlama ve Arşivleme"** işlevini görür. Bellek üzerindeki veriler uçucudur; güvenlik denetimlerinde ise kanıtların saklanması esastır. Tarama sonucunda elde edilen bulgular bu modül sayesinde yapılandırılmış `.csv` formatına dönüştürülerek diske yazılır ve kalıcı hale getirilir.

### 4. Canlı İzleme (Real-Time Monitoring)
Bu modül, **"Aktif Savunma"** mantığıyla çalışır. Geçmişle ilgilenmez, "şu an" odaklıdır. Program, dosyanın sonuna (`EOF`) konumlanır ve beklemeye başlar. İşletim sistemi dosyaya yeni bir satır yazdığı anda LogGuard bu satırı yakalar, analiz eder ve kural setine uyuyorsa operatöre anlık uyarı üretir.

## 🛠 Kurulum ve Derleme (Build)
Uygulamanın çalıştırılabilmesi için sistemde **Docker** servisinin kurulu olması gerekmektedir.

Uygulama imajının oluşturulması için proje dizininde aşağıdaki komut çalıştırılmalıdır:

docker build -t log-guard .

Geliştiren: Burak ASLAN