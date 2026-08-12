[app]
title = 海盗军团抢宝藏
package.name = mutiny
package.domain = org.example.mutiny
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,ttc,wav
version = 1.0.0
description = 海盗军团抢宝藏 - 经典抛射对战手游
requirements = python3,kivy==2.3.1,pillow,jnius
presplash.color = #0b1d33
icon.filename = %(source.dir)s/assets/icon.png
orientation = landscape
fullscreen = 0
android.permissions = WAKE_LOCK
android.api = 30
android.minapi = 21
android.archs = arm64-v8a

[buildozer]
log_level = 2
