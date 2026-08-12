# -*- coding: utf-8 -*-
"""战斗画布 Widget：承载 Game 状态、触摸分发、动画循环、场景渲染"""
from kivy.uix.widget import Widget
from kivy.clock import Clock
from .game import Game
from .scene import SceneRenderer


class GameCanvas(Widget):
    def __init__(self, sound, events, **kw):
        super().__init__(**kw)
        self.sound = sound
        self.events = events      # {on_result, on_pause}
        self.game = Game(SceneRenderer(self), sound)
        self.scene = self.game.renderer
        self.game.on_result = events['on_result']
        self.game.on_pause = events['on_pause']
        self._dt_last = None
        self._running = False
        self._clock_event = None
        self.bind(size=self._on_size)
        self._on_size()

    def _on_size(self, *a):
        self.scene.resize(max(1, self.width), max(1, self.height))
        self.scene.r.resize(max(1, self.width), max(1, self.height))

    def start_level(self, n):
        self.game.start_level(n)
        self._begin()

    def start_arena(self):
        self.game.start_arena()
        self._begin()

    def _begin(self):
        self.scene.resize(max(1, self.width), max(1, self.height))
        self._running = True
        self._dt_last = Clock.get_time()
        if self._clock_event is None:
            self._clock_event = Clock.schedule_interval(self._tick, 1.0 / 60.0)

    def _tick(self, dt):
        if not self._running:
            return
        now = Clock.get_time()
        d = now - self._dt_last
        self._dt_last = now
        if not self.game.paused and not self.game.result_shown:
            self.game.update(min(d, 0.033))
        self.scene.draw_scene(self.game)

    def pause(self):
        self.game.paused = True

    def resume(self):
        self.game.paused = False
        self._dt_last = Clock.get_time()

    def stop(self):
        self._running = False
        if self._clock_event is not None:
            self._clock_event.cancel()
            self._clock_event = None

    # ---------- 触摸 ----------
    def on_touch_down(self, touch):
        if self._running:
            if self.game.on_touch_down(touch.x, touch.y):
                return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._running and self.game.on_touch_move(touch.uid, touch.x, touch.y):
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self._running:
            self.game.on_touch_up(touch.uid, touch.x, touch.y)
        return super().on_touch_up(touch)
