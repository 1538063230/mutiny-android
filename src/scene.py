# -*- coding: utf-8 -*-
"""场景绘制：把 Game 世界渲染到 Kivy Canvas（天空/海/平台/角色/特效/HUD）"""
import math
from .render import Renderer, hx
from .render import (get_pirate_texture, get_bomb_texture, get_firebomb_texture,
                     get_barrel_texture, get_crate_texture, get_anchor_texture)
from .entities import WORLD_W, WORLD_H
from .physics import WATER_Y


class SceneRenderer:
    def __init__(self, widget):
        self.widget = widget
        self.r = Renderer(widget)
        self.time = 0.0

    def resize(self, w, h):
        self.r.resize(w, h)

    # ---- 代理到内部 Renderer，供 Game 调用 ----
    @property
    def cam(self):
        return self.r.cam

    @cam.setter
    def cam(self, v):
        self.r.cam = v

    def _update_cam(self, tx, ty):
        self.r._update_cam(tx, ty)

    def world_to_screen(self, x, y):
        return self.r.world_to_screen(x, y)

    def screen_to_world(self, x, y):
        return self.r.screen_to_world(x, y)

    # ---------- 背景 ----------
    def draw_background(self):
        # 天空
        self.r.rect(-100, 0, WORLD_W + 200, WATER_Y + 200, (0.15, 0.25, 0.45), 1.0)
        # 海
        self.r.rect(-100, WATER_Y, WORLD_W + 200, WORLD_H - WATER_Y + 100, (0.11, 0.35, 0.56), 1.0)
        # 海面深色渐变近似
        self.r.rect(-100, WATER_Y + 40, WORLD_W + 200, WORLD_H - WATER_Y, (0.05, 0.2, 0.42), 1.0)
        # 云（多椭圆叠加，更像云）
        for i in range(3):
            cx = ((i * 700 + self.time * 12) % (WORLD_W + 400)) - 200
            cy = 110 + i * 100
            self.r.ellipse(cx, cy, 80, 24, (1.0, 1.0, 1.0, 1.0), 0.55)
            self.r.ellipse(cx + 60, cy + 8, 60, 20, (1.0, 1.0, 1.0, 1.0), 0.55)
            self.r.ellipse(cx - 50, cy + 10, 55, 18, (1.0, 1.0, 1.0, 1.0), 0.55)
        # 海面波浪
        for row in range(6):
            pts = []
            for x in range(-100, WORLD_W + 150, 90):
                y = WATER_Y + 18 + row * 22 + math.sin(x * 0.02 + self.time * 1.4 + row) * 5
                pts.append((x, y))
            self.r.polyline(pts, (0.62, 0.82, 0.95, 1.0), 2, 0.35)
        # 波光
        for i in range(20):
            px = ((i * 173 + self.time * 40) % (WORLD_W + 200)) - 100
            py = WATER_Y + 20 + ((i * 67) % 60)
            self.r.rect(px, py, 14, 2, (1.0, 1.0, 1.0), 0.3)

    # ---------- 平台 ----------
    def draw_platform(self, p):
        # 主体
        self.r.rect(p.x, p.y, p.w, p.h, hx('#8a5a2b'), 1.0)
        # 顶部木板
        self.r.rect(p.x, p.y, p.w, max(14, p.h * 0.14), hx('#c98a4b'), 1.0)
        # 木板缝
        for x in range(int(p.x) + 26, int(p.x + p.w) - 4, 26):
            self.r.polyline([(x, p.y), (x, p.y + max(14, p.h * 0.14))], (0.25, 0.15, 0.06, 1.0), 1.5, 0.6)
        # 底部土壤
        self.r.rect(p.x + 2, p.y + p.h * 0.55, p.w - 4, p.h * 0.45, (0.35, 0.22, 0.10, 0.6), 1.0)
        # 草皮
        for i in range(max(1, int(p.w // 60))):
            gx = p.x + 12 + i * 60
            self.r.rect(gx, p.y - 3, 14, 4, (0.35, 0.59, 0.24, 1.0), 0.5)

    # ---------- 角色 ----------
    def draw_pirate(self, p):
        if p.dead and p.death_t > 1.2:
            return
        alpha = max(0.0, 1 - p.death_t) if p.dead else 1.0
        band = p.band_color or '#d9301f'
        team = p.team
        tex = get_pirate_texture(p.kind, team, p.type, band)
        size_w = p.body.r * 2.6
        rot = math.pi / 2 if p.dead else 0.0
        # 阴影
        self.r.ellipse(p.x, p.y + p.body.r * 0.92, p.body.r * 0.9, p.body.r * 0.28, (0, 0, 0, 1), 0.22)
        self.r.texture(tex, p.x, p.y - 4, size_w, size_w, rot, alpha)
        # 受击闪白
        if p.flash > 0:
            self.r.circle(p.x, p.y, p.body.r * 1.2, (1, 1, 1, 1), min(1, p.flash * 4))

    # ---------- 道具 ----------
    def draw_bomb(self, b):
        tex = get_bomb_texture()
        self.r.texture(tex, b.x, b.y, 26, 26)

    def draw_firebomb(self, b):
        tex = get_firebomb_texture()
        self.r.texture(tex, b.x, b.y, 26, 26)

    def draw_barrel(self, b):
        tex = get_barrel_texture()
        self.r.texture(tex, b.x, b.y, 34, 34)

    def draw_crate(self, c):
        tex = get_crate_texture()
        self.r.texture(tex, c.x, c.y, 40, 40)

    def draw_anchor(self, a):
        tex = get_anchor_texture()
        rot = math.sin(self.time * 3 + a.body.x) * 0.15
        self.r.texture(tex, a.x, a.y, 36, 44, rot)

    def draw_fire(self, f):
        flicker = math.sin(self.time * 12 + f.seed * 3) * 0.2
        k = 1 + flicker
        alpha = min(1.0, f.life / 1.5)
        # 地面余烬
        self.r.circle(f.x, f.y, f.r * 0.9, (0.3, 0.08, 0.0, 1.0), 0.5)
        # 火苗（多层圆）
        for i in range(4):
            a = (i / 4) * math.pi * 2 + f.seed
            dx = math.cos(a) * f.r * 0.4
            dy = math.sin(a) * f.r * 0.28
            hgt = f.r * (0.6 + 0.3 * math.sin(self.time * 9 + i * 2 + f.seed)) * k
            self.r.ellipse(f.x + dx, f.y + dy - hgt * 0.5, hgt * 0.4, hgt * 0.7,
                           (1.0, 0.48, 0.12, 1.0), alpha * 0.9)
            self.r.ellipse(f.x + dx, f.y + dy - hgt * 0.4, hgt * 0.22, hgt * 0.4,
                           (1.0, 0.83, 0.29, 1.0), alpha)
            self.r.ellipse(f.x + dx, f.y + dy - hgt * 0.3, hgt * 0.1, hgt * 0.2,
                           (1.0, 0.97, 0.82, 1.0), alpha)

    def draw_treasure(self, t):
        sparkle = (math.sin(self.time * 3 + t.sparkle) + 1) / 2
        # 木箱底
        self.r.rect(t.x - 20, t.y - 4, 40, 10, hx('#b8860b'), 1.0)
        # 金币
        for i in range(t.n):
            gx = t.x - 10 + i * 10
            gy = t.y - 8 - abs(gx - t.x) * 0.2
            self.r.circle(gx, gy, 6, hx('#ffd700'), 1.0)
            self.r.circle(gx, gy, 3.5, hx('#b8860b'), 0.6)
        if sparkle > 0.75:
            self.r.circle(t.x + 12, t.y - 16, 6, (1.0, 1.0, 1.0, 1.0), sparkle - 0.5)

    # ---------- 粒子 ----------
    def draw_particles(self, particles):
        for p in particles.list:
            a = p.life / p.max_life if p.fade else 1.0
            self.r.rect(p.x - p.size / 2, p.y - p.size / 2, p.size, p.size,
                        self._parse_color(p.color), max(0, min(1, a)))

    def _parse_color(self, color):
        if isinstance(color, tuple):
            return color
        return hx(color)

    # ---------- 爆炸环 ----------
    def draw_effects(self, effects):
        for e in effects:
            t = e['t'] / e['dur']
            k = 1 - t
            col = hx(e['color'])
            self.r.circle(e['x'], e['y'], e['radius'] * (0.3 + 0.7 * t), col, max(0, k * 0.7))

    # ---------- 血条 ----------
    def draw_health_bar(self, p):
        w = p.body.r * 2.1
        x = p.x - w / 2
        y = p.y - p.body.r - 16
        col = hx('#ff5a4a')
        if p.team == 'blue':
            col = hx('#4aa3ff')
        self.r.rect(x - 1, y - 1, w + 2, 7, (0, 0, 0, 1), 0.55)
        ratio = max(0, p.hp / p.max_hp)
        if ratio > 0:
            self.r.rect(x, y, w * ratio, 5, col, 1.0)
        self.r.polyline([(x - 1, y - 1), (x + w + 1, y - 1), (x + w + 1, y + 6), (x - 1, y + 6), (x - 1, y - 1)],
                        (1.0, 1.0, 1.0, 1.0), 1, 0.6)

    # ---------- 瞄准线 ----------
    def draw_aim(self, p, sx, sy, curx, cury, dragging):
        if p.weapon == 'move':
            w_cur = self.r.screen_to_world(curx, cury)
            self.r.polyline([(p.x, p.y), w_cur], (1.0, 1.0, 1.0, 1.0), 2, 0.5, dash_len=8)
            self.r.circle(w_cur[0], w_cur[1], 9, (0.5, 0.86, 0.5, 1.0), 1.0)
        elif p.weapon != 'anchor' and dragging:
            w_start = self.r.screen_to_world(sx, sy)
            w_cur = self.r.screen_to_world(curx, cury)
            vx = (w_start[0] - w_cur[0]) * 0.95
            vy = (w_start[1] - w_cur[1]) * 0.95
            sp = math.hypot(vx, vy)
            max_sp = p.throw_speed
            if sp > max_sp:
                k = max_sp / sp
                vx *= k
                vy *= k
            if sp >= 300:
                self._draw_trajectory(p.x, p.y - 6, vx, vy)

    def _draw_trajectory(self, sx, sy, vx, vy):
        pts = []
        px, py = sx, sy
        pvx, pvy = vx, vy
        dt = 0.05
        for _ in range(28):
            pvy += 1100 * dt
            px += pvx * dt
            py += pvy * dt
            if py >= WATER_Y:
                break
            pts.append((px, py))
        if pts:
            self.r.polyline(pts, (1.0, 1.0, 1.0, 1.0), 2.5, 0.9, dash_len=10)
            self.r.circle(pts[-1][0], pts[-1][1], 6, hx('#ffd54a'), 0.9)

    # ---------- 主场景 ----------
    def draw_scene(self, game):
        self.time = game.time
        # 清空 canvas
        self.widget.canvas.clear()
        self.r.cam = {'x': 0, 'y': 0, 'scale': max(self.r.w / WORLD_W, self.r.h / WORLD_H) * 1.02}

        self.draw_background()
        for p in game.world.platforms:
            self.draw_platform(p)
        for t in game.treasures:
            self.draw_treasure(t)
        for f in game.fires:
            self.draw_fire(f)
        for c in game.crates:
            self.draw_crate(c)
        for b in game.barrels:
            self.draw_barrel(b)
        for p in game.players:
            self.draw_pirate(p)
        for p in game.enemies:
            self.draw_pirate(p)
        for p in game.blue_team:
            self.draw_pirate(p)
        for pr in game.projectiles:
            if pr.kind == 'bomb':
                self.draw_bomb(pr)
            elif pr.kind == 'firebomb':
                self.draw_firebomb(pr)
            elif pr.kind == 'anchor':
                self.draw_anchor(pr)
        self.draw_particles(game.particles)
        self.draw_effects(game.effects)

        # 血条
        for p in game.players + game.enemies + game.blue_team:
            if not p.dead:
                self.draw_health_bar(p)

        # 瞄准线
        for aim in game.aims.values():
            if aim['p'].dead or not aim['p'].alive:
                continue
            self.draw_aim(aim['p'], aim['sx'], aim['sy'], aim['cx'], aim['cy'], aim['dragging'])

        # 选中高亮
        if game.selected and not game.selected.dead and game.selected.alive:
            self.r.circle(game.selected.x, game.selected.y, game.selected.body.r + 7, hx('#ffe9a0'), 0.8)

        # HUD（屏幕坐标）
        self._draw_hud(game)

    def _draw_hud(self, game):
        w = self.r.w
        h = self.r.h
        s = min(1.0, w / 420.0)
        game.hud_buttons = []

        # 顶部横幅（屏幕坐标，用屏幕矩形）
        self._srect(0, 0, w, 34 * s + 8, (0.04, 0.08, 0.16), 0.6)
        title = ('双人对战' if game.mode == 'arena' else
                 '第 %d 关 · %s' % (game.level_number, game.level_name))
        # 标题文本（用简单近似：Kivy Label 太重，战斗内省略详细文字，用图标）
        self._text(title, w / 2, 18 * s, 15 * s, (1.0, 0.91, 0.79, 1.0))

        # 敌人数量
        if game.mode == 'level':
            alive = sum(1 for p in game.enemies if not p.dead)
            self._text('敌人 %d' % alive, w - 60 * s, 18 * s, 15 * s, hx('#ffd54a'))

        # 暂停按钮
        pb = {'id': 'pause', 'x': w - 46 * s, 'y': 5 * s, 'w': 38 * s, 'h': 30 * s}
        self._srect(pb['x'], pb['y'], pb['w'], pb['h'], (1, 1, 1), 0.14, radius=8 * s)
        self._srect(pb['x'] + 12 * s, pb['y'] + 8 * s, 4 * s, 14 * s, (1, 1, 1, 1), 1.0)
        self._srect(pb['x'] + 21 * s, pb['y'] + 8 * s, 4 * s, 14 * s, (1, 1, 1, 1), 1.0)
        game.hud_buttons.append(pb)

        # 小地图
        self._draw_minimap(game, s)

        # 武器栏
        if game.selected and not game.selected.dead and game.selected.alive:
            self._draw_weapon_bar(game, s)
            if game.selected.weapon == 'anchor':
                self._text('点击任意位置召唤船锚', w / 2, h - 78 * s, 14 * s, (1, 1, 1, 1), 0.9)

    def _draw_minimap(self, game, s):
        mw = 118 * s
        mh = 64 * s
        mx = 8 * s
        my = 42 * s
        kx = mw / WORLD_W
        ky = mh / WORLD_H
        self._srect(mx - 2, my - 2, mw + 4, mh + 4, (0.03, 0.08, 0.15), 0.75, radius=6 * s)
        for p in game.world.platforms:
            self._srect(mx + p.x * kx, my + p.y * ky, p.w * kx, p.h * ky, hx('#96643a'), 0.9)
        self._srect(mx, my + WATER_Y * ky, mw, mh - WATER_Y * ky, (0.16, 0.43, 0.7), 0.7)
        for p in game.players:
            if not p.dead:
                self._srect(mx + p.x * kx - 1.5, my + p.y * ky - 1.5, 3, 3, (0.35, 1.0, 0.35), 1.0)
        for p in game.blue_team:
            if not p.dead:
                self._srect(mx + p.x * kx - 1.5, my + p.y * ky - 1.5, 3, 3, (0.29, 0.64, 1.0), 1.0)
        for p in game.enemies:
            if not p.dead:
                self._srect(mx + p.x * kx - 2, my + p.y * ky - 2, 4, 4, (1.0, 0.35, 0.29), 1.0)

    def _draw_weapon_bar(self, game, s):
        w = self.r.w
        h = self.r.h
        n = len(game.weapons)
        bw = 54 * s
        bh = 52 * s
        gap = 8 * s
        total = n * bw + (n - 1) * gap
        x0 = (w - total) / 2
        y0 = h - bh - 12 * s
        self._srect(x0 - 10 * s, y0 - 8 * s, total + 20 * s, bh + 16 * s, (0.04, 0.08, 0.16), 0.75, radius=12 * s)
        for i, wd in enumerate(game.weapons):
            x = x0 + i * (bw + gap)
            active = game.selected.weapon == wd
            col = (1.0, 0.82, 0.35, 0.4) if active else (1, 1, 1, 0.08)
            self._srect(x, y0, bw, bh, col, 1.0, radius=10 * s, border=(1, 1, 1, 0.25) if not active else (1.0, 0.82, 0.35, 1.0))
            self._text(WEAPON_ICONS.get(wd, wd), x + bw / 2, y0 + 28 * s, 14 * s,
                       (1.0, 0.82, 0.35, 1.0) if active else (0.84, 0.9, 1.0, 1.0))
            game.hud_buttons.append({'id': 'weapon_' + wd, 'x': x, 'y': y0, 'w': bw, 'h': bh})

    # ---------- 屏幕坐标辅助 ----------
    def _srect(self, x, y, w, h, rgb, alpha=1.0, radius=0, border=None):
        from kivy.graphics import Color, Rectangle
        with self.widget.canvas:
            Color(*rgb, a=alpha)
            Rectangle(pos=(x, y), size=(w, h))
        if border:
            from kivy.graphics import Line
            with self.widget.canvas:
                Color(*border, a=alpha)
                Line(rectangle=(x, y, w, h), width=1)

    def _text(self, s, cx, cy, size, rgb, alpha=1.0):
        """用 Canvas Label 渲染文本（中心对齐）。"""
        from kivy.graphics import Color, Rectangle
        from kivy.core.text import Label as CoreLabel
        lbl = CoreLabel(text=s, font_size=size, color=(*rgb, alpha),
                        halign='center', valign='middle', font_name='SimHei')
        lbl.refresh()
        tex = lbl.texture
        if not tex:
            return
        with self.widget.canvas:
            Color(1, 1, 1, 1)
            Rectangle(texture=tex, pos=(cx - tex.width / 2, cy - tex.height / 2),
                      size=(tex.width, tex.height))


from .game import WEAPON_NAMES as _wn
from .game import WEAPON_ICONS as _wi
WEAPON_NAMES = _wn
WEAPON_ICONS = _wi
