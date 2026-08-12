# -*- coding: utf-8 -*-
"""程序化音效：纯 Python 合成各种音效，经 Kivy SoundLoader 播放。
不依赖 numpy，跨桌面/安卓可用，打包更轻量。"""
import os
import tempfile
import wave
import struct
import math
import random

SR = 22050


def _write_wav_16(path, sig):
    """sig: 归一化到 [-1,1] 的 float list"""
    n = len(sig)
    frames = bytearray(n * 2)
    for i, v in enumerate(sig):
        x = max(-1.0, min(1.0, v))
        s = int(x * 32767)
        frames[i * 2] = s & 0xFF
        frames[i * 2 + 1] = (s >> 8) & 0xFF
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(bytes(frames))


class SoundManager:
    def __init__(self):
        self.enabled = True
        self._cache = {}
        self._dir = os.path.join(tempfile.gettempdir(), 'mutiny_sfx')
        try:
            os.makedirs(self._dir, exist_ok=True)
        except Exception:
            pass

    def _tone(self, f0, f1, dur, vol, wave_type='square', delay=0.0):
        n = max(1, int(SR * dur))
        out = []
        phase = 0.0
        f = f0
        df = (max(20, f1) - f0) / n
        for i in range(n):
            if wave_type == 'square':
                w = 1.0 if math.sin(phase) >= 0 else -1.0
            elif wave_type == 'triangle':
                w = 2 / math.pi * math.asin(math.sin(phase))
            elif wave_type == 'sawtooth':
                w = 2 * ((phase / (2 * math.pi)) % 1) - 1
            else:
                w = math.sin(phase)
            env = math.exp(-3.5 * (i / n))
            out.append(vol * w * env)
            phase += 2 * math.pi * f / SR
            f += df
        return out

    def _noise(self, dur, vol, f_from, f_to, kind='lowpass'):
        n = max(1, int(SR * dur))
        out = []
        acc = 0.0
        a = 0.05 + 0.4 * (f_from / 4000.0)
        for i in range(n):
            noise = random.uniform(-1, 1)
            acc += (1 - a) * (noise - acc)
            env = math.exp(-3.0 * (i / n))
            out.append(vol * acc * env)
        return out

    def _mix(self, *sigs):
        maxlen = max(len(s) for s in sigs) if sigs else 0
        out = [0.0] * maxlen
        for s in sigs:
            for i, v in enumerate(s):
                out[i] += v
        return out

    def _render(self, name):
        if name == 'throw':
            return self._noise(0.22, 0.5, 2400, 300)
        if name == 'explosion':
            return self._mix(self._noise(0.9, 1.0, 1200, 60), self._tone(90, 30, 0.8, 0.7, 'sine'))
        if name == 'bigExplode':
            return self._mix(self._noise(1.3, 1.2, 1500, 50), self._tone(70, 24, 1.2, 0.9, 'sine'))
        if name == 'hit':
            return self._mix(self._tone(420, 160, 0.16, 0.6, 'square'), self._noise(0.1, 0.5, 1800, 500))
        if name == 'splash':
            return self._mix(self._tone(700, 180, 0.3, 0.6, 'triangle'), self._noise(0.25, 0.4, 900, 200))
        if name == 'fire':
            return self._noise(0.5, 0.35, 600, 200)
        if name == 'click':
            return self._tone(660, 520, 0.08, 0.4, 'sine')
        if name == 'select':
            return self._tone(520, 760, 0.1, 0.5, 'sine')
        if name == 'win':
            return self._mix(*[self._tone(f, f, 0.22, 0.5, 'square', i * 0.15)
                               for i, f in enumerate([523, 659, 784, 1047])])
        if name == 'lose':
            return self._mix(*[self._tone(f, f * 0.9, 0.3, 0.5, 'triangle', i * 0.22)
                               for i, f in enumerate([440, 349, 262, 196])])
        if name == 'barrel':
            return self._noise(0.15, 0.5, 3000, 800)
        if name == 'anchor':
            return self._mix(self._tone(300, 60, 0.4, 0.7, 'sawtooth'), self._noise(0.3, 0.6, 800, 150))
        return None

    def _ensure(self, name):
        if name in self._cache:
            return self._cache[name]
        path = os.path.join(self._dir, name + '.wav')
        if not os.path.exists(path):
            sig = self._render(name)
            if sig is None:
                return None
            try:
                _write_wav_16(path, sig)
            except Exception:
                return None
        self._cache[name] = path
        return path

    def play(self, name):
        if not self.enabled:
            return
        try:
            path = self._ensure(name)
            if not path:
                return
            from kivy.core.audio import SoundLoader
            sound = SoundLoader.load(path)
            if sound:
                sound.play()
                self._last = sound
        except Exception:
            pass
