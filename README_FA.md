# اپ یادداشت‌برداری اندروید با Python + Kivy

## امکانات
- ساخت یادداشت
- ویرایش یادداشت
- حذف یادداشت
- جست‌وجو در عنوان و متن
- ذخیره دائمی با SQLite
- حالت روشن و تاریک
- رابط مناسب موبایل
- کاملاً قابل توسعه

## اجرای روی کامپیوتر

Python 3 را نصب کنید، سپس:

```bash
pip install -r requirements.txt
python main.py
```

## ساخت APK برای اندروید

Buildozer معمولاً روی Linux/WSL راحت‌تر استفاده می‌شود.

```bash
pip install buildozer
buildozer android debug
```

پس از اتمام، فایل APK داخل پوشه `bin/` قرار می‌گیرد.

برای ساخت نسخه Release:

```bash
buildozer android release
```

## نکته
برای انتشار در Google Play، APK/AAB باید با کلید امضای مناسب ساخته و تنظیمات انتشار تکمیل شود.
