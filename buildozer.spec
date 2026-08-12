[app]
# 应用标题
title = 海盗军团抢宝藏
# 包名
package.name = mutiny
# 包域（需唯一）
package.domain = org.example.mutiny
# 源码目录
source.dir = .
# 包含的资源扩展名（含中文字体）
source.include_exts = py,png,jpg,kv,atlas,ttf,ttc,wav
# 版本
version = 1.0.0


# 依赖（纯 Python + Kivy；pillow 用于纹理生成，jnius 用于安卓系统接口）
requirements = python3,kivy==2.3.1,pillow,jnius

# 预加载页背景色
presplash.color = #0b1d33

# 图标
icon.filename = %(source.dir)s/assets/icon.png

# 屏幕方向：横屏
orientation = landscape
# 非全屏（保留系统栏，更安全）
fullscreen = 0

# 权限：屏幕常亮（防熄屏）
android.permissions = WAKE_LOCK

# Android 目标 API 与最低版本
android.api = 31
android.minapi = 21

# 密钥签名（留空使用 debug 签名，可直接安装）
# android.keystore =

# 生成的 app 元数据由 python-for-android 自动处理
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
# 日志级别
log_level = 1
# 最大并行编译任务数
max_jobs = 2
