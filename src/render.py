# -*- coding: utf-8 -*-
"""渲染模块：Kivy Canvas 绘制场景、像素海盗、道具、特效
移植自 H5 版 render.js。复杂角色用离屏 Texture 预渲染，场景用 Canvas 原语。
"""
import math
from kivy.graphics import Color, Rectangle, Ellipse, Line, PushMatrix, PopMatrix, Translate, Rotate, Mesh
from kivy.graphics.texture import Texture
from .entities import WORLD_W, WORLD_H
from .physics import WATER_Y


def hx(c):
    """hex 颜色转 0-1 元组"""
    c = c.lstrip('#')
    return (int(c[0:2], 16) / 255, int(c[2:4], 16) / 255, int(c[4:6], 16) / 255)


class CanvasPix:
    """在指定像素画布上绘制像素图（用于预渲染 Texture）。"""
    def __init__(self, w, h):
        self.w = w
        self.h = h
        # 使用 PIL 离屏渲染最稳妥；若未装 PIL 用 numpy。这里用纯 Python 逐像素画布。
        self.data = [[(0, 0, 0, 0) for _ in range(w)] for __ in range(h)]

    def set(self, x, y, color, alpha=1.0):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.data[y][x] = (color[0], color[1], color[2], alpha)

    def fill_rect(self, x0, y0, x1, y1, color, alpha=1.0):
        for y in range(max(0, y0), min(self.h, y1 + 1)):
            for x in range(max(0, x0), min(self.w, x1 + 1)):
                self.set(x, y, color, alpha)

    def fill_circle(self, cx, cy, r, color, alpha=1.0):
        r2 = r * r
        for y in range(max(0, int(cy - r)), min(self.h, int(cy + r) + 1)):
            for x in range(max(0, int(cx - r)), min(self.w, int(cx + r) + 1)):
                dx = x - cx
                dy = y - cy
                if dx * dx + dy * dy <= r2:
                    self.set(x, y, color, alpha)

    def to_texture(self):
        from PIL import Image
        img = Image.new('RGBA', (self.w, self.h))
        px = img.load()
        for y in range(self.h):
            for x in range(self.w):
                c = self.data[y][x]
                px[x, self.h - 1 - y] = (int(c[0] * 255), int(c[1] * 255), int(c[2] * 255), int(c[3] * 255))
        data = img.tobytes()
        tex = Texture.create(size=(self.w, self.h), colorfmt='rgba')
        tex.blit_buffer(data, colorfmt='rgba', bufferfmt='ubyte')
        return tex


# ---------- 预渲染像素海盗 ----------
_PIRATE_TEX = {}


def get_pirate_texture(kind, team, type_key, band):
    """返回海盗纹理。band 为头巾颜色 hex。"""
    key = (kind, team, type_key, band)
    if key in _PIRATE_TEX:
        return _PIRATE_TEX[key]
    # 以 r=22 为基准，画 56x56
    size = 64
    cv = CanvasPix(size, size)
    cx, cy = size / 2, size / 2 + 6
    skin = hx('#f0c38a')
    if kind == 'squid':
        skin = hx('#c98bff')
    band_col = hx(band) if band else hx('#d9301f')
    # 腿
    leg_col = (0.17, 0.14, 0.09, 1)
    cv.fill_rect(int(cx - 10), int(cy + 4), int(cx - 3), int(cy + 18), leg_col)
    cv.fill_rect(int(cx + 3), int(cy + 4), int(cx + 10), int(cy + 18), leg_col)
    # 身体
    body_col = (0.75, 0.22, 0.17, 1)  # 红
    if team == 'blue':
        body_col = (0.16, 0.37, 0.72, 1)
    if kind == 'squid':
        body_col = skin
    cv.fill_rect(int(cx - 12), int(cy - 8), int(cx + 12), int(cy + 8), body_col)
    # 腰带
    cv.fill_rect(int(cx - 12), int(cy + 2), int(cx + 12), int(cy + 6), (0.23, 0.16, 0.06, 1))
    if kind == 'squid':
        # 触手
        tent = (0.48, 0.25, 0.71, 1)
        for i in range(-2, 3):
            tx = cx + i * 7
            cv.fill_rect(int(tx - 2), int(cy + 6), int(tx + 2), int(cy + 18), tent)
        # 眼
        cv.fill_rect(int(cx + 3), int(cy - 14), int(cx + 12), int(cy - 8), (0.05, 0.05, 0.05, 1))
    else:
        # 头
        cv.fill_circle(int(cx), int(cy - 14), 11, skin)
        # 眼睛
        cv.fill_rect(int(cx + 2), int(cy - 17), int(cx + 6), int(cy - 13), (0.05, 0.05, 0.05, 1))
        # 头巾
        cv.fill_rect(int(cx - 12), int(cy - 24), int(cx + 12), int(cy - 16), band_col)
        cv.fill_circle(int(cx), int(cy - 21), 11, band_col)
        # 头巾结
        cv.fill_rect(int(cx - 14), int(cy - 22), int(cx - 11), int(cy - 17), band_col)
        cv.fill_rect(int(cx - 14), int(cy - 22), int(cx - 10), int(cy - 14), band_col)
        if type_key == 'child':
            # 熊孩子大耳朵
            cv.fill_circle(int(cx - 11), int(cy - 20), 4, skin)
            cv.fill_circle(int(cx + 11), int(cy - 20), 4, skin)
    tex = cv.to_texture()
    _PIRATE_TEX[key] = tex
    return tex


# ---------- 预渲染道具 ----------
_BOMB_TEX = None
_FIREBOMB_TEX = None
_BARREL_TEX = None
_CRATE_TEX = None
_ANCHOR_TEX = None


def get_bomb_texture():
    global _BOMB_TEX
    if _BOMB_TEX is None:
        cv = CanvasPix(40, 40)
        cv.fill_circle(20, 22, 11, (0.16, 0.16, 0.16, 1))
        cv.fill_circle(17, 19, 4, (0.3, 0.3, 0.3, 1))
        cv.fill_rect(24, 12, 27, 15, (0.16, 0.16, 0.16, 1))
        cv.fill_circle(28, 10, 3, (1.0, 0.48, 0.12, 1))
        _BOMB_TEX = cv.to_texture()
    return _BOMB_TEX


def get_firebomb_texture():
    global _FIREBOMB_TEX
    if _FIREBOMB_TEX is None:
        cv = CanvasPix(36, 36)
        cv.fill_circle(18, 18, 12, (0.72, 0.2, 0.11, 1))
        cv.fill_circle(18, 18, 5, (1.0, 0.82, 0.0, 1))
        _FIREBOMB_TEX = cv.to_texture()
    return _FIREBOMB_TEX


def get_barrel_texture():
    global _BARREL_TEX
    if _BARREL_TEX is None:
        cv = CanvasPix(48, 48)
        brown = (0.48, 0.29, 0.12, 1)
        cv.fill_rect(10, 4, 38, 44, brown)
        cv.fill_rect(10, 4, 38, 10, (0.37, 0.24, 0.10, 1))
        cv.fill_rect(10, 38, 38, 44, (0.37, 0.24, 0.10, 1))
        cv.fill_rect(10, 19, 38, 27, (1.0, 0.84, 0.29, 1))
        # 骷髅
        cv.fill_circle(24, 26, 5, (1, 1, 1, 1))
        cv.fill_rect(22, 25, 24, 24, (0.1, 0.1, 0.1, 1))
        cv.fill_rect(26, 25, 28, 24, (0.1, 0.1, 0.1, 1))
        _BARREL_TEX = cv.to_texture()
    return _BARREL_TEX


def get_crate_texture():
    global _CRATE_TEX
    if _CRATE_TEX is None:
        cv = CanvasPix(48, 48)
        cv.fill_rect(5, 5, 43, 43, (0.66, 0.44, 0.23, 1))
        # 板条
        cv.fill_rect(5, 5, 43, 43, None, 0)
        for y in range(7, 43, 9):
            cv.fill_rect(6, y, 42, y + 5, (0.55, 0.36, 0.18, 1))
        # 交叉
        cv.fill_rect(20, 5, 28, 43, (0.79, 0.63, 0.42, 1))
        cv.fill_rect(5, 20, 43, 28, (0.79, 0.63, 0.42, 1))
        _CRATE_TEX = cv.to_texture()
    return _CRATE_TEX


def get_anchor_texture():
    global _ANCHOR_TEX
    if _ANCHOR_TEX is None:
        cv = CanvasPix(48, 48)
        gray = (0.36, 0.42, 0.48, 1)
        cv.fill_rect(21, 4, 27, 28, gray)
        cv.fill_rect(14, 12, 34, 18, gray)
        cv.fill_rect(14, 16, 18, 30, gray)
        cv.fill_rect(30, 16, 34, 30, gray)
        cv.fill_rect(12, 28, 22, 33, gray)
        cv.fill_rect(26, 28, 36, 33, gray)
        cv.fill_circle(24, 4, 5, (1.0, 0.84, 0.29, 1))
        _ANCHOR_TEX = cv.to_texture()
    return _ANCHOR_TEX


def _tex(tex, x, y, size_w, size_h, rot=0.0):
    """在指定 Canvas 上贴图，world 坐标中心 (x,y)，宽高 size。返回 Kivy 指令列表。
    实际由 Renderer 调用写入 canvas。"""
    pass


class Renderer:
    def __init__(self, widget):
        self.widget = widget
        self.w = 1
        self.h = 1
        self.cam = {'x': 0, 'y': 0, 'scale': 1}

    def resize(self, w, h):
        self.w = w
        self.h = h

    def _update_cam(self, tx, ty):
        scale = max(self.w / WORLD_W, self.h / WORLD_H) * 1.02
        self.cam['scale'] = scale
        view_w = self.w / scale
        view_h = self.h / scale

        def clamp(v, lo, hi):
            return max(lo, min(hi, v))

        cx = tx
        cy = ty
        if view_w >= WORLD_W:
            cx = WORLD_W / 2
        else:
            cx = clamp(cx, view_w / 2, WORLD_W - view_w / 2)
        if view_h >= WORLD_H:
            cy = WORLD_H / 2
        else:
            cy = clamp(cy, view_h * 0.4, WORLD_H - view_h / 2)
        self.cam['x'] = cx - view_w / 2
        self.cam['y'] = cy - view_h / 2

    def world_to_screen(self, wx, wy):
        s = self.cam['scale']
        return ((wx - self.cam['x']) * s, (wy - self.cam['y']) * s)

    def screen_to_world(self, sx, sy):
        s = self.cam['scale']
        return (self.cam['x'] + sx / s, self.cam['y'] + sy / s)

    # ---------- 原语（世界坐标，写入 canvas） ----------
    def rect(self, x, y, w, h, rgb, alpha=1.0):
        x0, y0 = self.world_to_screen(x, y)
        x1, y1 = self.world_to_screen(x + w, y + h)
        with self.widget.canvas:
            Color(*rgb, a=alpha)
            Rectangle(pos=(min(x0, x1), min(y0, y1)), size=(abs(x1 - x0), abs(y1 - y0)))

    def circle(self, x, y, r, rgb, alpha=1.0, segments=24):
        cx, cy = self.world_to_screen(x, y)
        s = self.cam['scale']
        rr = max(0.6, r * s)
        with self.widget.canvas:
            Color(*rgb, a=alpha)
            Ellipse(pos=(cx - rr, cy - rr), size=(rr * 2, rr * 2), segments=segments)

    def ellipse(self, x, y, rx, ry, rgb, alpha=1.0, rot=0.0, segments=24):
        cx, cy = self.world_to_screen(x, y)
        s = self.cam['scale']
        w = max(0.6, rx * s * 2)
        h = max(0.6, ry * s * 2)
        with self.widget.canvas:
            PushMatrix()
            Translate(cx, cy)
            if rot:
                Rotate(angle=math.degrees(rot), origin=(0, 0))
            Color(*rgb, a=alpha)
            Ellipse(pos=(-w / 2, -h / 2), size=(w, h), segments=segments)
            PopMatrix()

    def polyline(self, wpts, rgb, width=1.0, alpha=1.0, dash_len=None, dash_off=0.0):
        if len(wpts) < 2:
            return
        pts = []
        s = self.cam['scale']
        for wx, wy in wpts:
            sx, sy = self.world_to_screen(wx, wy)
            pts.extend([sx, sy])
        with self.widget.canvas:
            Color(*rgb, a=alpha)
            Line(points=pts, width=max(1.0, width * s),
                 dash_length=dash_len * s if dash_len else None,
                 dash_offset=dash_off * s if dash_len else None)

    def texture(self, tex, x, y, world_w, world_h, rot=0.0, alpha=1.0):
        """贴纹理，中心 (x,y)，世界尺寸 world_w x world_h"""
        cx, cy = self.world_to_screen(x, y)
        s = self.cam['scale']
        w = world_w * s
        h = world_h * s
        if w < 1 or h < 1:
            return
        with self.widget.canvas:
            PushMatrix()
            Translate(cx, cy)
            if rot:
                Rotate(angle=math.degrees(rot), origin=(0, 0))
            Color(1, 1, 1, a=alpha)
            Rectangle(texture=tex, pos=(-w / 2, -h / 2), size=(w, h))
            PopMatrix()
