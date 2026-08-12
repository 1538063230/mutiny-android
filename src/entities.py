# -*- coding: utf-8 -*-
"""实体系统：海盗、炸弹、燃烧弹、火焰、火药桶、板条箱、船锚、粒子
移植自 H5 版 entities.js"""
import math
from .physics import Body, WATER_Y

WORLD_W = 2000
WORLD_H = 1100


# ---------- 海盗类型 ----------
PIRATE_TYPES = {
    'child':  {'hp': 45,  'speed': 240, 'radius': 18, 'band': '#e5602a', 'ai_cd': (2.6, 4.0), 'throw_spd': 800,  'kind': 'child'},
    'squid':  {'hp': 55,  'speed': 210, 'radius': 20, 'band': None,      'ai_cd': (2.2, 3.4), 'throw_spd': 860,  'kind': 'squid'},
    'pirate': {'hp': 75,  'speed': 260, 'radius': 21, 'band': '#1d5fe0', 'ai_cd': (1.9, 3.0), 'throw_spd': 940,  'kind': 'pirate'},
    'elite':  {'hp': 110, 'speed': 280, 'radius': 22, 'band': '#121212', 'ai_cd': (1.5, 2.4), 'throw_spd': 1020, 'kind': 'pirate'},
    'player': {'hp': 100, 'speed': 280, 'radius': 22, 'band': '#d9301f', 'ai_cd': None,      'throw_spd': 1300, 'kind': 'pirate'},
}

WEAPONS = [
    ('move',     '移动',  'walk'),
    ('bomb',     '炸弹',  'bomb'),
    ('firebomb', '燃烧弹', 'fire'),
    ('crate',    '板条箱', 'crate'),
    ('barrel',   '火药桶', 'barrel'),
    ('anchor',   '船锚',  'anchor'),
]


class Pirate:
    def __init__(self, x, y, opts=None):
        opts = opts or {}
        t = PIRATE_TYPES.get(opts.get('type'), PIRATE_TYPES['player'])
        self.kind = t['kind']
        self.body = Body(x, y, opts.get('radius', t['radius']), {'mass': 60, 'restitution': 0.3, 'friction': 0.9})
        self.body.entity = self
        self.type = opts.get('type', 'player')
        self.team = opts.get('team', 'enemy')
        self.hp = t['hp']
        self.max_hp = t['hp']
        self.speed = t['speed']
        self.alive = True
        self.dead = False
        self.face = 1
        self.weapon = 'bomb'
        self.throw_cd = 0.0
        self.move_target = None
        self.is_moving = False
        self.flash = 0.0
        self.jump_cd = 0.0
        self.squash = 0.0
        self.band_color = t['band']
        self.skin_color = '#f0c38a'
        self.throw_speed = t['throw_spd']
        self.walk_frame = 0.0
        self.death_t = 0.0
        self.cause = 'hp'
        # AI
        self.ai_t = 0.0
        self.ai_cd = list(t['ai_cd']) if t['ai_cd'] else None

    @property
    def x(self):
        return self.body.x

    @property
    def y(self):
        return self.body.y

    def move_to(self, tx, ty):
        self.move_target = (tx, min(ty, WATER_Y - 40))
        self.is_moving = True

    def stop_moving(self):
        self.move_target = None
        self.is_moving = False

    def hurt(self, dmg, from_x=None, from_y=None):
        if self.dead:
            return
        self.hp -= dmg
        self.flash = 0.18
        self.squash = 0.35
        if from_x is not None and from_y is not None:
            dx = self.x - from_x
            dy = self.y - from_y
            d = math.hypot(dx, dy) or 1
            self.body.vx += (dx / d) * 60
            self.body.vy += (dy / d) * 60
        if self.hp <= 0:
            self.kill()

    def kill(self, cause='hp'):
        if self.dead:
            return
        self.dead = True
        self.alive = False
        self.death_t = 0.0
        self.cause = cause

    def update(self, dt, world, game):
        self.throw_cd = max(0.0, self.throw_cd - dt)
        self.flash = max(0.0, self.flash - dt)
        self.squash = max(0.0, self.squash - dt)
        self.jump_cd = max(0.0, self.jump_cd - dt)

        if self.dead:
            self.body.vy += (400 if self.cause == 'water' else 120) * dt
            self.death_t += dt
            return

        # 落水
        if self.body.y - self.body.r > WATER_Y:
            if game:
                game.on_drown(self)
            return

        # 移动控制
        if self.is_moving and self.move_target:
            tx, ty = self.move_target
            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy)
            direction = 1 if dx > 0 else -1
            self.face = direction
            if dist > 14:
                self.body.vx = direction * self.speed
                self.walk_frame += dt * 6
                if self.body.grounded and self.jump_cd <= 0:
                    ahead_x = self.x + direction * (self.body.r + 8)
                    on_ground = self.body.on_ground
                    at_edge = (on_ground is None or
                               ahead_x < on_ground.x + 2 or
                               ahead_x > on_ground.x + on_ground.w - 2)
                    wall = any(
                        ahead_x >= p.x and ahead_x <= p.x + p.w and
                        self.y - 8 < p.y + p.h and self.y + 8 > p.y
                        for p in world.platforms
                    )
                    need_up = ty < self.y - 40
                    need_down = ty > self.y + 60
                    if need_up and (wall or at_edge):
                        self.body.vy = -780
                        self.jump_cd = 0.6
                    elif need_down and at_edge:
                        self.body.vy = 60
            else:
                self.stop_moving()
                self.body.vx = 0
        else:
            self.body.vx = 0


# ---------- 炸弹 ----------
class Bomb:
    def __init__(self, x, y, vx, vy, opts=None):
        opts = opts or {}
        self.body = Body(x, y, 11, {'mass': 8, 'restitution': 0.4, 'friction': 0.2})
        self.body.entity = self
        self.body.set_velocity(vx, vy)
        self.kind = 'bomb'
        self.fuse = opts.get('fuse', 2.4)
        self.damage = opts.get('damage', 55)
        self.radius = opts.get('radius', 165)
        self.impulse = opts.get('impulse', 460)
        self.owner = opts.get('owner')
        self.exploded = False
        self.hit_owner_cd = 0.3

    @property
    def x(self):
        return self.body.x

    @property
    def y(self):
        return self.body.y

    def update(self, dt, world, game):
        self.fuse -= dt
        if self.fuse <= 0:
            game.explode_at(self.x, self.y, self.radius, self.damage, self.impulse, self)
            self.exploded = True
            return
        # 落水
        if self.body.y - self.body.r > WATER_Y:
            self.exploded = True
            game.particles.water(self.x, self.y, 8)
            game.sound.play('splash')
            return
        # 撞击实体 -> 短引信
        near = world.bodies_at(self.x, self.y, 30)
        for b in near:
            if b is self.body:
                continue
            ent = b.entity
            if ent and getattr(ent, 'kind', None) and ent.kind != 'fire':
                d = math.hypot(b.x - self.x, b.y - self.y)
                if d < b.r + self.body.r + 2:
                    if self.owner and b.entity is self.owner and self.hit_owner_cd > 0:
                        continue
                    self.fuse = min(self.fuse, 0.3)
                    break


# ---------- 燃烧弹 ----------
class FireBomb:
    def __init__(self, x, y, vx, vy, opts=None):
        opts = opts or {}
        self.body = Body(x, y, 10, {'mass': 6, 'restitution': 0.35, 'friction': 0.2})
        self.body.entity = self
        self.body.set_velocity(vx, vy)
        self.kind = 'firebomb'
        self.owner = opts.get('owner')
        self.ignited = False

    @property
    def x(self):
        return self.body.x

    @property
    def y(self):
        return self.body.y

    def update(self, dt, world, game):
        if self.body.grounded and not self.ignited:
            self.ignited = True
            game.spawn_fire(self.x, self.y + 4)
            world.explode(self.x, self.y, 80, 2, 120, lambda b, fall, d: (
                b.entity.ignite(game) if b.entity and getattr(b.entity, 'kind', None) == 'barrel'
                and not b.entity.igniting else None
            ))
            game.particles.spark(self.x, self.y, 18, '#ff7b1f')


# ---------- 火焰 ----------
class Fire:
    def __init__(self, x, y, opts=None):
        opts = opts or {}
        self.x = x
        self.y = y
        self.kind = 'fire'
        self.life = opts.get('life', 6.0)
        self.r = 34
        self.tick = 0
        self.seed = random_num()
        self.damage = 14
        self.owner_team = opts.get('owner_team')

    def update(self, dt, world, game):
        self.life -= dt
        self.tick -= dt
        if self.tick <= 0:
            self.tick = 0.32
            game.damage_area(self.x, self.y, self.r + 6, self.damage, 40)
            game.particles.flame(self.x + (random_num() - 0.5) * 20, self.y - random_num() * 14, 3, '#ff8a1f')


# ---------- 火药桶 ----------
class Barrel:
    def __init__(self, x, y):
        self.body = Body(x, y, 17, {'mass': 26, 'restitution': 0.3, 'friction': 0.5})
        self.body.entity = self
        self.kind = 'barrel'
        self.hp = 50
        self.igniting = False
        self.ignite_t = 0
        self.dead = False

    @property
    def x(self):
        return self.body.x

    @property
    def y(self):
        return self.body.y

    def ignite(self, game):
        if self.igniting:
            return
        self.igniting = True
        self.ignite_t = 0.5
        game.sound.play('barrel')

    def update(self, dt, world, game):
        if self.igniting:
            self.ignite_t -= dt
            game.particles.flame(self.x, self.y - 10, 4, '#ffd000')
            if self.ignite_t <= 0:
                game.explode_at(self.x, self.y, 235, 95, 700, self)
                self.body.static = True
                self.dead = True
        # 落水
        if self.body.y - self.body.r > WATER_Y + 20:
            self.dead = True
            game.particles.water(self.x, self.y, 10)
            game.sound.play('splash')

    def hurt(self, dmg):
        self.hp -= dmg
        if self.hp <= 0 and not self.igniting:
            self.igniting = True


# ---------- 板条箱 ----------
class Crate:
    def __init__(self, x, y):
        self.body = Body(x, y, 20, {'mass': 34, 'restitution': 0.25, 'friction': 0.7})
        self.body.entity = self
        self.kind = 'crate'
        self.hp = 60
        self.dead = False

    @property
    def x(self):
        return self.body.x

    @property
    def y(self):
        return self.body.y

    def hurt(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.dead = True

    def update(self, dt, world, game):
        if self.hp <= 0:
            self.dead = True
        if self.body.y - self.body.r > WATER_Y + 20:
            self.dead = True


# ---------- 天降船锚 ----------
class Anchor:
    def __init__(self, x, y):
        self.body = Body(x, y, 24, {'mass': 90, 'restitution': 0.05, 'friction': 0.2})
        self.body.entity = self
        self.body.set_velocity(0, 1080)
        self.kind = 'anchor'
        self.dead = False
        self.hit_set = set()

    @property
    def x(self):
        return self.body.x

    @property
    def y(self):
        return self.body.y

    def update(self, dt, world, game):
        if self.dead:
            return
        if self.body.y - self.body.r > WATER_Y + 20:
            self.dead = True
            game.particles.water(self.x, self.y, 14)
            game.sound.play('splash')
            return
        near = world.bodies_at(self.x, self.y, 40)
        for b in near:
            if b is self.body:
                continue
            ent = b.entity
            if ent and getattr(ent, 'alive', None) is not False and ent not in self.hit_set and ent is not self:
                if ent.kind in ('pirate', 'barrel', 'crate'):
                    d = math.hypot(b.x - self.x, b.y - self.y)
                    if d < b.r + self.body.r:
                        self.hit_set.add(ent)
                        ent.hurt(70, self.x, self.y)
                        b.vx += (b.x - self.x) / d * 260 if d > 0 else 0
                        b.vy -= 300
                        game.particles.spark(self.x, self.y, 14, '#ffd54a')
                        game.sound.play('hit')
        if self.body.grounded and self.body.vy < 100:
            self.dead = True
            game.particles.spark(self.x, self.y + self.body.r, 12, '#c8a24a')
            game.sound.play('anchor')


# ---------- 宝藏 ----------
class Treasure:
    def __init__(self, x, y, n=3):
        self.x = x
        self.y = y
        self.n = n
        self.kind = 'treasure'
        self.sparkle = random_num() * 10


# ---------- 粒子 ----------
class Particle:
    def __init__(self, x, y, vx, vy, life, color, size, gravity=1, fade=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        self.gravity = gravity
        self.fade = fade


class ParticleSystem:
    def __init__(self):
        self.list = []

    def add(self, p):
        self.list.append(p)

    def burst(self, x, y, n, color, speed=260, size=4, life=0.7):
        for _ in range(n):
            a = random_num() * math.pi * 2
            s = speed * (0.3 + random_num() * 0.7)
            self.add(Particle(x, y, math.cos(a) * s, math.sin(a) * s - 120, life * (0.5 + random_num() * 0.8), color, size * (0.6 + random_num() * 0.8), 0.6))

    def spark(self, x, y, n, color):
        self.burst(x, y, n, color, 300, 4, 0.5)

    def flame(self, x, y, n, color):
        for _ in range(n):
            self.add(Particle(x + (random_num() - 0.5) * 8, y - random_num() * 10,
                              (random_num() - 0.5) * 40, -(120 + random_num() * 180),
                              0.4 + random_num() * 0.3, color, 5 + random_num() * 5, -0.4))

    def smoke(self, x, y, n):
        for _ in range(n):
            self.add(Particle(x + (random_num() - 0.5) * 30, y - random_num() * 20,
                              (random_num() - 0.5) * 60, -(40 + random_num() * 60),
                              0.9 + random_num() * 0.5, (120, 120, 120, 0.7), 8 + random_num() * 8, -0.3))

    def water(self, x, y, n):
        for _ in range(n):
            self.add(Particle(x + (random_num() - 0.5) * 10, y,
                              (random_num() - 0.5) * 120, -(80 + random_num() * 200),
                              0.6 + random_num() * 0.4, '#7fd4ff', 3 + random_num() * 3, 0.9))

    def update(self, dt):
        keep = []
        for p in self.list:
            p.life -= dt
            if p.life <= 0:
                continue
            p.vy += 700 * p.gravity * dt
            p.x += p.vx * dt
            p.y += p.vy * dt
            keep.append(p)
        self.list = keep


def random_num():
    import random
    return random.random()


# ---------- 抛体解算 ----------
def solve_throw(sx, sy, tx, ty, v0):
    dx = tx - sx
    dy = ty - sy
    g = 1100
    v2 = v0 * v0
    under = v2 * v2 - g * (g * dx * dx + 2 * dy * v2)
    if under < 0:
        return None
    sq = math.sqrt(under)
    ang1 = math.atan2(v2 + sq, g * dx)
    ang2 = math.atan2(v2 - sq, g * dx)
    a = None
    if not math.isnan(ang1) and math.isfinite(ang1) and math.cos(ang1) * dx > 0:
        a = ang1
    if not math.isnan(ang2) and math.isfinite(ang2) and math.cos(ang2) * dx > 0:
        if a is None or abs(ang2) < abs(a):
            a = ang2
    if a is None:
        d = math.hypot(dx, dy) or 1
        a = math.atan2(dy, dx)
    return {'vx': v0 * math.cos(a), 'vy': v0 * math.sin(a)}
