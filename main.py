# -*- coding: utf-8 -*-
"""海盗军团抢宝藏（手机版）- 入口
Kivy 实现，目标打包安卓 APK。"""
import os
import sys

# 让 src 可作为包导入（桌面/安卓均可）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 注册中文字体（必须在 import kivy 之前）
from kivy.resources import resource_add_path
_ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
resource_add_path(_ASSETS)  # 让安卓 APK 与桌面都能通过文件名找到资源

from kivy.core.text import LabelBase
if os.path.exists(os.path.join(_ASSETS, 'simhei.ttf')):
    LabelBase.register('SimHei', os.path.join(_ASSETS, 'simhei.ttf'))
    LabelBase.register('Roboto', os.path.join(_ASSETS, 'simhei.ttf'))

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock
from kivy.metrics import dp

from src.gamecanvas import GameCanvas
from src.ui import (MainMenuScreen, ModeScreen, LevelSelectScreen, AboutScreen,
                    PauseScreen, ResultScreen, GameScreen)
from src.audio import SoundManager
from src.levels import TOTAL_LEVELS


class MutinyApp(App):
    title = '海盗军团抢宝藏'

    def build(self):
        # 强制横屏
        try:
            if platform in ('android', 'ios'):
                from kivy.core.window import Window
                from jnius import autoclass
                activity = autoclass('org.kivy.android.PythonActivity').mActivity
                activity.setRequestedOrientation(0)  # SCREEN_ORIENTATION_LANDSCAPE
        except Exception:
            pass

        self.sound = SoundManager()
        self.game_canvas = GameCanvas(
            self.sound,
            {'on_result': self._on_result, 'on_pause': self._on_pause},
        )

        self.current_level = 1
        self.last_mode = 'level'  # 'level' | 'arena'
        self._last_result = None

        self.sm = ScreenManager()
        self.game_screen = GameScreen(self, self.game_canvas)
        self.menu_screen = MainMenuScreen(self)
        self.mode_screen = ModeScreen(self)
        self.level_screen = LevelSelectScreen(self)
        self.about_screen = AboutScreen(self)
        self.pause_screen = PauseScreen(self)
        self.result_screen = ResultScreen(self)

        for s in [self.menu_screen, self.mode_screen, self.level_screen,
                  self.about_screen, self.pause_screen, self.result_screen, self.game_screen]:
            self.sm.add_widget(s)
        self.sm.current = 'menu'
        return self.sm

    # ---------- 进度存储 ----------
    def get_progress(self):
        try:
            if platform == 'android':
                from jnius import autoclass
                act = autoclass('org.kivy.android.PythonActivity').mActivity
                prefs = act.getSharedPreferences('mutiny', 0)
                return prefs.getInt('progress', 1)
        except Exception:
            pass
        try:
            p = os.path.join(os.path.expanduser('~'), '.mutiny_progress')
            if os.path.exists(p):
                return max(1, int(open(p).read().strip()))
        except Exception:
            pass
        return 1

    def save_progress(self, n):
        try:
            if platform == 'android':
                from jnius import autoclass
                act = autoclass('org.kivy.android.PythonActivity').mActivity
                prefs = act.getSharedPreferences('mutiny', 0)
                if prefs.getInt('progress', 1) < n:
                    prefs.edit().putInt('progress', n).commit()
                return
        except Exception:
            pass
        try:
            p = os.path.join(os.path.expanduser('~'), '.mutiny_progress')
            open(p, 'w').write(str(max(1, n)))
        except Exception:
            pass

    # ---------- 导航 ----------
    def goto(self, name):
        self.sm.current = name

    def open_level_select(self):
        self.level_screen.rebuild()
        self.sm.current = 'levels'

    def start_level(self, n):
        self.current_level = n
        self.last_mode = 'level'
        self._start_game()

    def start_arena(self):
        self.last_mode = 'arena'
        self._start_game()

    def _start_game(self):
        # 先显示 game 屏再启动，确保尺寸正确
        self.sm.current = 'game'
        Clock.schedule_once(lambda dt: self._launch(), 0.05)

    def _launch(self):
        if self.last_mode == 'arena':
            self.game_canvas.start_arena()
        else:
            self.game_canvas.start_level(self.current_level)

    # ---------- 战斗回调 ----------
    def _on_pause(self):
        self.sm.current = 'pause'

    def _on_result(self, kind, custom_title):
        self._last_result = {'kind': kind, 'title': custom_title,
                             'arena': self.last_mode == 'arena',
                             'level': self.current_level}
        self.result_screen.show_result(kind, custom_title,
                                       self.last_mode == 'arena', self.current_level)
        self.sm.current = 'result'

    # ---------- UI 回调 ----------
    def resume(self):
        self.game_canvas.resume()
        self.sm.current = 'game'

    def restart(self):
        self.sm.current = 'game'
        Clock.schedule_once(lambda dt: self._launch(), 0.05)

    def next_level(self):
        if self._last_result:
            if self._last_result['kind'] == 'win' and not self._last_result['arena']:
                if self.current_level < TOTAL_LEVELS:
                    self.start_level(self.current_level + 1)
                    return
        self.to_menu()

    def back_from_result(self):
        if self.last_mode == 'arena':
            self.to_menu()
        else:
            self.open_level_select()

    def to_menu(self):
        self.game_canvas.stop()
        self.sm.current = 'menu'

    def on_pause(self):
        # 安卓返回桌面时暂停游戏
        self.game_canvas.pause()
        return True

    def on_resume(self):
        self.game_canvas.resume()


if __name__ == '__main__':
    MutinyApp().run()
