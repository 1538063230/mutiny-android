# -*- coding: utf-8 -*-
"""2D 物理引擎：重力、平台碰撞（圆 vs 矩形）、弹性碰撞、爆炸冲击
移植自 H5 版 physics.js"""
import math

GRAVITY = 1100.0      # px/s^2
MAX_SPEED = 2400.0    # 限速防穿透
WATER_Y = 985.0       # 海平面


class Platform:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def dist_to_circle(self, cx, cy, r):
        px = max(self.x, min(cx, self.x + self.w))
        py = max(self.y, min(cy, self.y + self.h))
        return math.hypot(cx - px, cy - py) - r

    def clamp_point(self, cx, cy):
        return (
            max(self.x, min(cx, self.x + self.w)),
            max(self.y, min(cy, self.y + self.h)),
        )

    def contains_point(self, px, py):
        return self.x <= px <= self.x + self.w and self.y <= py <= self.y + self.h


class Body:
    def __init__(self, x, y, r, opts=None):
        opts = opts or {}
        self.x = x
        self.y = y
        self.r = r
        self.vx = 0.0
        self.vy = 0.0
        self.mass = opts.get('mass', r * r * 3)
        self.restitution = opts.get('restitution', 0.35)
        self.friction = opts.get('friction', 0.6)
        self.static = bool(opts.get('static', False))
        self.grounded = False
        self.gravity_scale = opts.get('gravity_scale', 1.0)
        self.on_ground = None
        self.entity = None

    def set_velocity(self, vx, vy):
        self.vx = vx
        self.vy = vy


class World:
    def __init__(self):
        self.bodies = []
        self.platforms = []

    def add_body(self, b):
        self.bodies.append(b)
        return b

    def remove_body(self, b):
        if b in self.bodies:
            self.bodies.remove(b)

    def add_platform(self, p):
        self.platforms.append(p)
        return p

    def ground_at(self, x, y):
        for p in self.platforms:
            if p.x <= x <= p.x + p.w:
                if p.y <= y <= p.y + p.h + 2:
                    return p
        return None

    def step(self, dt):
        bodies = self.bodies
        grav = GRAVITY * dt

        # 积分
        for b in bodies:
            if b.static:
                continue
            b.vy += grav * b.gravity_scale
            b.vx *= pow(0.995, dt * 60)
            sp = math.hypot(b.vx, b.vy)
            if sp > MAX_SPEED:
                k = MAX_SPEED / sp
                b.vx *= k
                b.vy *= k
            b.x += b.vx * dt
            b.y += b.vy * dt
            b.grounded = False
            b.on_ground = None

        # 平台碰撞
        for b in bodies:
            if b.static:
                continue
            for p in self.platforms:
                self._collide_circle_rect(b, p)

        # 实体互碰
        n = len(bodies)
        for i in range(n):
            a = bodies[i]
            if a.static:
                continue
            for j in range(i + 1, n):
                c = bodies[j]
                if c.static:
                    continue
                dx = c.x - a.x
                dy = c.y - a.y
                rr = a.r + c.r
                d2 = dx * dx + dy * dy
                if d2 >= rr * rr or d2 == 0:
                    continue
                d = math.sqrt(d2)
                nx = dx / d
                ny = dy / d
                overlap = (rr - d) * 0.5
                a.x -= nx * overlap
                a.y -= ny * overlap
                c.x += nx * overlap
                c.y += ny * overlap
                rel_v = (c.vx - a.vx) * nx + (c.vy - a.vy) * ny
                if rel_v < 0:
                    m_sum = a.mass + c.mass
                    j_imp = (-(1 + 0.4) * rel_v) / m_sum
                    a.vx -= j_imp * c.mass * nx
                    a.vy -= j_imp * c.mass * ny
                    c.vx += j_imp * a.mass * nx
                    c.vy += j_imp * a.mass * ny

        # 二次碰撞，减少下沉
        for b in bodies:
            if b.static:
                continue
            for p in self.platforms:
                self._collide_circle_rect(b, p)

    def _collide_circle_rect(self, b, p):
        cx, cy = p.clamp_point(b.x, b.y)
        dx = b.x - cx
        dy = b.y - cy
        d2 = dx * dx + dy * dy
        if d2 >= b.r * b.r:
            return
        if d2 == 0:
            left = b.x - p.x
            right = p.x + p.w - b.x
            top = b.y - p.y
            bottom = p.y + p.h - b.y
            m = min(left, right, top, bottom)
            if m == left:
                b.x = p.x - b.r
                b.vx = abs(b.vx) * 0.3
            elif m == right:
                b.x = p.x + p.w + b.r
                b.vx = -abs(b.vx) * 0.3
            elif m == top:
                b.y = p.y - b.r
                b.vy = abs(b.vy) * 0.3
            else:
                b.y = p.y + p.h + b.r
                b.vy = -abs(b.vy) * 0.3
            return
        d = math.sqrt(d2)
        nx = dx / d
        ny = dy / d
        pen = b.r - d
        b.x += nx * pen
        b.y += ny * pen
        vn = b.vx * nx + b.vy * ny
        if vn < 0:
            b.vx -= (1 + b.restitution) * vn * nx
            b.vy -= (1 + b.restitution) * vn * ny
        if abs(ny) > 0.7:
            b.vx *= (1 - b.friction * 0.25)
            b.vy *= 0.3
            b.grounded = True
            b.on_ground = p

    def explode(self, x, y, radius, damage, impulse, on_hit=None):
        for b in self.bodies:
            dx = b.x - x
            dy = b.y - y
            d = math.hypot(dx, dy)
            if d > radius + b.r:
                continue
            fall = max(0.0, 1 - d / (radius + b.r))
            if d > 0.001:
                b.vx += (dx / d) * impulse * fall
                b.vy += (dy / d) * impulse * fall
            else:
                b.vy -= impulse * fall
            if on_hit:
                on_hit(b, fall, d)

    def bodies_at(self, x, y, max_dist):
        out = []
        for b in self.bodies:
            if math.hypot(b.x - x, b.y - y) <= max_dist + b.r:
                out.append(b)
        return out
