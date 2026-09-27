[app]
title = یادداشت‌های من
package.name = noteapp
package.domain = org.example
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,atlas,db
version = 1.0
requirements = python3,kivy==2.3.0
orientation = portrait
fullscreen = 0
android.api = 35
android.accept_sdk_license = True
android.accept_sdk_license = True
android.minapi = 23
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.private_storage = True

[buildozer]
log_level = 2
warn_on_root = 1

[buildozer:android]
