# -*- coding: utf-8 -*-
"""桌面调试启动脚本：横屏小窗口，3 秒后自动关闭"""
import os
os.environ['KIVY_METRICS_DENSITY'] = '1'
os.environ['KIVY_METRICS_SCALE'] = '1'
from kivy.config import Config
Config.set('graphics', 'width', '960')
Config.set('graphics', 'height', '540')
Config.set('graphics', 'fullscreen', '0')
Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('graphics', 'resizable', '0')

import main

app = main.MutinyApp()


def auto_quit(dt):
    app.stop()


from kivy.clock import Clock
if os.environ.get('MUTINY_AUTOQUIT'):
    Clock.schedule_once(auto_quit, 4)

app.run()
print('APP RAN OK')
