# -*- coding: utf-8 -*-
"""UI 层：主菜单、模式选择、选关、结算、暂停、游戏说明"""
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle, RoundedRectangle
from .levels import TOTAL_LEVELS, get_progress


# ---------- 风格辅助 ----------
def _btn(text, size=0.6, color=(1, 0.55, 0.2, 1), bold=True, font_size=dp(20)):
    b = Button(text=text, font_size=font_size, size_hint=(None, None),
               size=(dp(240), dp(56)), bold=bold, font_name='SimHei')
    b.background_normal = ''
    b.background_color = color
    return b


def _title(txt, size=dp(30)):
    return Label(text=txt, font_size=size, size_hint=(1, None), height=dp(50),
                 color=(1, 0.83, 0.29, 1), bold=True, font_name='SimHei')


class BgLayout(FloatLayout):
    """带背景色的布局"""
    def __init__(self, bg=(0.03, 0.08, 0.18, 1), **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(*bg)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda *a: setattr(self._bg, 'pos', self.pos),
                  size=lambda *a: setattr(self._bg, 'size', self.size))


class MainMenuScreen(Screen):
    def __init__(self, app, **kw):
        super().__init__(name='menu', **kw)
        self.app = app
        self.root = BgLayout()
        self.add_widget(self.root)
        box = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(18),
                        size_hint=(1, 1))
        self.root.add_widget(box)
        box.add_widget(Label(text='海盗军团\n抢宝藏', font_size=dp(46),
                             color=(1, 0.95, 0.84, 1), bold=True,
                             halign='center', font_name='SimHei'))
        box.add_widget(Label(text='Mutiny · 海盗抛射对战', font_size=dp(14),
                             color=(1, 0.86, 0.63, 0.85), font_name='SimHei'))
        box.add_widget(Label(text='', size_hint=(1, 0.5)))
        b_play = _btn('PLAY', color=(1, 0.5, 0.15, 1), font_size=dp(26))
        b_play.bind(on_release=lambda *a: self.app.goto('mode'))
        box.add_widget(b_play)
        b_about = _btn('游戏说明', color=(0.3, 0.45, 0.6, 0.9), font_size=dp(18))
        b_about.bind(on_release=lambda *a: self.app.goto('about'))
        box.add_widget(b_about)
        box.add_widget(Label(text='', size_hint=(1, 0.4)))


class ModeScreen(Screen):
    def __init__(self, app, **kw):
        super().__init__(name='mode', **kw)
        self.app = app
        self.root = BgLayout()
        self.add_widget(self.root)
        box = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(24),
                        size_hint=(1, 1))
        self.root.add_widget(box)
        box.add_widget(Label(text='选择模式', font_size=dp(30), color=(1, 0.83, 0.29, 1), bold=True))
        box.add_widget(Label(text='', size_hint=(1, 0.4)))
        b1 = _btn('1 PLAYER\n单人闯关', font_size=dp(24), size=(dp(260), dp(90)))
        b1.bind(on_release=lambda *a: self.app.open_level_select())
        box.add_widget(b1)
        b2 = _btn('2 PLAYER\n双人对战', color=(0.25, 0.55, 0.9, 1), font_size=dp(24), size=(dp(260), dp(90)))
        b2.bind(on_release=lambda *a: self.app.start_arena())
        box.add_widget(b2)
        box.add_widget(Label(text='', size_hint=(1, 0.3)))
        bb = _btn('返回', color=(0.4, 0.4, 0.45, 0.8), font_size=dp(16))
        bb.bind(on_release=lambda *a: self.app.goto('menu'))
        box.add_widget(bb)


class LevelSelectScreen(Screen):
    def __init__(self, app, **kw):
        super().__init__(name='levels', **kw)
        self.app = app
        self.root = BgLayout()
        self.add_widget(self.root)
        box = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(16))
        self.root.add_widget(box)
        box.add_widget(Label(text='选择关卡', font_size=dp(28), color=(1, 0.83, 0.29, 1), bold=True))
        sv = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(cols=5, spacing=dp(12), padding=dp(8),
                               size_hint_y=None, row_default_height=dp(70), row_force_default=True)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        sv.add_widget(self.grid)
        box.add_widget(sv)
        bb = _btn('返回', color=(0.4, 0.4, 0.45, 0.8), font_size=dp(16))
        bb.bind(on_release=lambda *a: self.app.goto('mode'))
        box.add_widget(bb)

    def rebuild(self):
        self.grid.clear_widgets()
        progress = get_progress()
        for i in range(1, TOTAL_LEVELS + 1):
            unlocked = i <= progress
            b = Button(text=str(i), font_size=dp(20), size_hint=(None, None),
                       size=(dp(62), dp(70)), bold=True, disabled=not unlocked)
            b.background_normal = ''
            b.background_color = (0.23, 0.37, 0.56, 1) if unlocked else (0.15, 0.17, 0.2, 1)
            if unlocked:
                b.bind(on_release=lambda *a, n=i: self.app.start_level(n))
            else:
                b.text = '锁'
            self.grid.add_widget(b)


class AboutScreen(Screen):
    def __init__(self, app, **kw):
        super().__init__(name='about', **kw)
        self.app = app
        self.root = BgLayout()
        self.add_widget(self.root)
        box = BoxLayout(orientation='vertical', spacing=dp(14), padding=dp(24))
        self.root.add_widget(box)
        box.add_widget(_title('游戏说明'))
        info = ('目标：消灭所有敌人，夺回宝藏！\n\n'
                '操作：点击选中海盗，选择道具后按住拖拽瞄准，松手投掷。\n\n'
                '道具：炸弹(范围爆炸)、燃烧弹(地面火焰)、\n'
                '      火药桶(引爆大爆炸)、板条箱(掩体)、船锚(天降)。\n\n'
                '注意：你和敌人掉进海里都会被淘汰！')
        lbl = Label(text=info, font_size=dp(16), color=(1, 0.91, 0.79, 1),
                    halign='center', valign='middle', font_name='SimHei')
        lbl.bind(size=lambda *a: setattr(lbl, 'text_size', lbl.size))
        box.add_widget(lbl)
        bb = _btn('返回', color=(0.4, 0.4, 0.45, 0.8), font_size=dp(16))
        bb.bind(on_release=lambda *a: self.app.goto('menu'))
        box.add_widget(bb)


class PauseScreen(Screen):
    def __init__(self, app, **kw):
        super().__init__(name='pause', **kw)
        self.app = app
        self.root = BgLayout()
        self.add_widget(self.root)
        box = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(24), size_hint=(1, 1))
        self.root.add_widget(box)
        box.add_widget(Label(text='暂停', font_size=dp(30), color=(1, 0.83, 0.29, 1), bold=True))
        box.add_widget(Label(text='', size_hint=(1, 0.5)))
        b1 = _btn('继续游戏', color=(1, 0.5, 0.15, 1), font_size=dp(20))
        b1.bind(on_release=lambda *a: self.app.resume())
        box.add_widget(b1)
        b2 = _btn('重新开始', color=(0.25, 0.55, 0.9, 1), font_size=dp(20))
        b2.bind(on_release=lambda *a: self.app.restart())
        box.add_widget(b2)
        b3 = _btn('返回主菜单', color=(0.4, 0.4, 0.45, 0.8), font_size=dp(16))
        b3.bind(on_release=lambda *a: self.app.to_menu())
        box.add_widget(b3)
        box.add_widget(Label(text='', size_hint=(1, 0.4)))


class ResultScreen(Screen):
    def __init__(self, app, **kw):
        super().__init__(name='result', **kw)
        self.app = app
        self.root = BgLayout()
        self.add_widget(self.root)
        self.box = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(24), size_hint=(1, 1))
        self.root.add_widget(self.box)
        self.title = Label(text='', font_size=dp(40), color=(1, 0.83, 0.29, 1), bold=True)
        self.box.add_widget(self.title)
        self.sub = Label(text='', font_size=dp(16), color=(1, 0.91, 0.79, 1),
                         halign='center', valign='middle')
        self.sub.bind(size=lambda *a: setattr(self.sub, 'text_size', self.sub.size))
        self.box.add_widget(self.sub)
        self.box.add_widget(Label(text='', size_hint=(1, 0.5)))
        self.b_next = _btn('下一关', color=(1, 0.5, 0.15, 1), font_size=dp(22))
        self.b_next.bind(on_release=lambda *a: self.app.next_level())
        self.box.add_widget(self.b_next)
        self.b_replay = _btn('重新挑战', color=(0.25, 0.55, 0.9, 1), font_size=dp(20))
        self.b_replay.bind(on_release=lambda *a: self.app.restart())
        self.box.add_widget(self.b_replay)
        self.b_exit = _btn('返回', color=(0.4, 0.4, 0.45, 0.8), font_size=dp(16))
        self.b_exit.bind(on_release=lambda *a: self.app.back_from_result())
        self.box.add_widget(self.b_exit)

    def show_result(self, kind, custom_title, is_arena, level_number):
        self.kind = kind
        self.is_arena = is_arena
        self.level_number = level_number
        self.title.text = '胜利！' if kind == 'win' else '战败'
        self.title.color = (1, 0.83, 0.29, 1) if kind == 'win' else (1, 0.48, 0.42, 1)
        if kind == 'win':
            self.sub.text = custom_title or ('第 %d 关通关！你夺回了宝藏！' % level_number)
        else:
            self.sub.text = custom_title or '全军覆没，宝藏被夺走了…'
        if is_arena:
            self.b_next.opacity = 0
            self.b_next.disabled = True
        else:
            self.b_next.opacity = 1
            self.b_next.disabled = False
            self.b_next.text = ('🏁 全部通关！' if kind == 'win' and level_number >= TOTAL_LEVELS else '下一关')
        self.b_replay.text = '再战一局' if is_arena else '重新挑战'


class GameScreen(Screen):
    """战斗画面：承载 GameCanvas 与触摸处理"""
    def __init__(self, app, game_canvas, **kw):
        super().__init__(name='game', **kw)
        self.app = app
        self.add_widget(game_canvas)
