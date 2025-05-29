# 🛡️ Android Malware Analyzer

Bu proje, Android APK dosyalarını sanal bir cihazda (örneğin: `android-x86`) çalıştırarak analiz eden otomatik bir araçtır. Her APK yüklemesinden önce snapshot'a dönülerek temiz bir analiz ortamı sağlanır. APK yüklemesi sonrası yeni kurulan paket tespit edilir, gerekli izinler verilir ve verilen izinlerin log dosyasına kaydı yapılır.

## 📂 Özellikler

- Sanal makine snapshot'ına otomatik geri dönme
- ADB üzerinden cihaza bağlanma
- APK kurulumundan önce ve sonra kurulu paketleri kıyaslama
- Yeni kurulan uygulamaya tüm izinleri verme
- `dumpsys` çıktısı ile verilen izinleri loglama
- Her analiz için zaman damgalı ayrı log dosyası oluşturma

## 🛠️ Gereksinimler

- Python 3.x
- ADB (`android-tools`)
- libvirt + QEMU
- Android-x86 sanal makinesi (`libvirt` üzerinden tanımlı)
- `adb connect` ile bağlanabilecek bir ağ üzerinden çalışan Android cihaz

Python kütüphanelerini kurmak için:

```bash
pip install libvirt-python
```

## 📁 Proje Yapısı

```
.
├── analyzer.py         # Ana Python betiği
├── logs/               # Analiz loglarının kaydedileceği klasör
└── ../viruses/         # APK dosyalarının bulunduğu klasör (parametre ile değiştirilebilir)
```

## 🚀 Kullanım

1. **Snapshot Ayarı:**
   - `libvirt` üzerinde çalışan `android-x86-9.0` isimli bir VM olmalı.
   - Bu VM üzerinde `safe_snapshot` isimli temiz bir snapshot tanımlı olmalı.

2. **APK Dizini:**
   - Analiz edilecek `.apk` dosyalarını `apk_dir` ile belirtilen dizine koyun (`../viruses` olarak ayarlanmış).

3. **Scripti çalıştırma:**

```bash
python3 analyzer.py
```

Her APK için analiz işlemleri yapılır ve sonuçlar `logs/` klasörüne kaydedilir.

## 📋 Log Örneği

Log dosyası örneği:

```
APK: virus_sample.apk
Package: com.malware.sample
<dumpsys çıktısı burada yer alır>
```

## ⚠️ Uyarılar

- Bu araç yalnızca güvenli ve izole ortamlarda kullanılmalıdır.
- Test ettiğiniz APK dosyaları zararlı olabilir. Sanal makinenin ve ağın izole olduğundan emin olun.
- `adb connect` kullanımı için sanal cihazın ADB bağlantısını kabul ettiğinden ve IP adresinin doğru olduğundan emin olun.

## 📄 Lisans

Bu proje eğitim ve analiz amaçlıdır. Geliştiriciler, bu kodun kötüye kullanımından sorumlu tutulamaz.