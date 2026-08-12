# -*- coding: utf-8 -*-
"""桌面自动化测试：菜单 -> 关卡1 -> 触摸投掷 -> 截图"""
import os
os.environ['KIVY_METRICS_DENSITY'] = '1'
os.environ['KIVY_METRICS_SCALE'] = '1'
from kivy.config import Config
Config.set('graphics', 'width', '960')
Config.set('graphics', 'height', '540')
Config.set('graphics', 'fullscreen', '0')
Config.set('graphics', 'resizable', '0')
Config.set('input', 'mouse', 'mouse,disable_multitouch')

import main
from kivy.clock import Clock

app = main.MutinyApp()
out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screenshots')
os.makedirs(out_dir, exist_ok=True)


def shot_menu(dt):
    app.sm.current = 'menu'
    app.sm.export_to_png(os.path.join(out_dir, 'menu.png'))
    print('shot: menu.png')


def shot_about(dt):
    app.goto('about')
    app.sm.export_to_png(os.path.join(out_dir, 'about.png'))
    print('shot: about.png')


def shot_levels(dt):
    app.open_level_select()
    app.sm.export_to_png(os.path.join(out_dir, 'levels.png'))
    print('shot: levels.png')


def shot_game(dt):
    app.start_level(1)
    Clock.schedule_once(shot_game2, 0.3)


def shot_game2(dt):
    app.game_canvas.export_to_png(os.path.join(out_dir, 'game_initial.png'))
    print('shot: game_initial.png')

    class MockTouch:
        def __init__(self, x, y, uid):
            self.x = x
            self.y = y
            self.uid = uid
            self.id = uid

        def move(self, pos):
            self.x, self.y = pos

    gc = app.game_canvas
    p = gc.game.players[0]
    sx, sy = gc.scene.world_to_screen(p.x, p.y)
    touch = MockTouch(sx, sy, 1)
    gc.on_touch_down(touch)
    for dx, dy in [(80, 80), (130, 130), (170, 160), (190, 180)]:
        touch.move((sx + dx, sy + dy))
        gc.on_touch_move(touch)
    gc.on_touch_up(touch)

    def after_throw(dt):
        gc.export_to_png(os.path.join(out_dir, 'game_throw.png'))
        print('shot: game_throw.png')

    Clock.schedule_once(after_throw, 1.5)


def finish(dt):
    app.stop()


# 启动后逐张截图
Clock.schedule_once(shot_menu, 0.8)
Clock.schedule_once(shot_about, 1.4)
Clock.schedule_once(shot_levels, 2.0)
Clock.schedule_once(shot_game, 2.8)
Clock.schedule_once(finish, 5.5)

app.run()
print('DONE')