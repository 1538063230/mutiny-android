# -*- coding: utf-8 -*-
"""游戏主逻辑：战斗循环、触摸交互、AI、HUD
移植自 H5 版 game.js"""
import math
from .entities import (WORLD_W, WORLD_H, Pirate, Bomb, FireBomb, Fire, Barrel, Crate,
                       Anchor, Treasure, ParticleSystem, solve_throw, PIRATE_TYPES)
from .physics import World, WATER_Y
from .levels import build_level, build_arena, save_progress

THROW_MIN = 300.0
THROW_K = 0.95
TAP_THRESHOLD = 15.0

WEAPON_NAMES = {'move': '移动', 'bomb': '炸弹', 'firebomb': '燃烧', 'crate': '板条箱', 'barrel': '火药桶', 'anchor': '船锚'}
WEAPON_ICONS = {'move': '步行', 'bomb': '炸弹', 'firebomb': '燃烧', 'crate': '木箱', 'barrel': '油桶', 'anchor': '船锚'}


class Game:
    def __init__(self, renderer, sound):
        self.renderer = renderer
        self.sound = sound
        self.world = World()
        self.particles = ParticleSystem()
        self.effects = []  # [(x, y, radius, t, dur, color)]
        self.time = 0.0
        self.paused = False
        self.running = False
        self.shake = 0.0

        self.players = []
        self.enemies = []
        self.blue_team = []
        self.projectiles = []
        self.fires = []
        self.barrels = []
        self.crates = []
        self.treasures = []
        self.mode = 'level'
        self.level_number = 1
        self.level_name = ''

        self.selected = None
        self.aims = {}  # tid -> aim dict
        self.hud_buttons = []
        self.result_shown = False

        self.on_result = None   # callback(kind, custom_title)
        self.on_pause = None
        self._aim_next_tid = 1

    # ---------- 世界构建 ----------
    def start_level(self, n):
        self.mode = 'level'
        self.level_number = n
        self._build(build_level(n))

    def start_arena(self):
        self.mode = 'arena'
        self._build(build_arena())

    def _build(self, L):
        self.world = World()
        self.players = []
        self.enemies = []
        self.blue_team = []
        self.projectiles = []
        self.fires = []
        self.barrels = []
        self.crates = []
        self.treasures = []
        self.effects = []
        self.particles.list = []
        self.aims = {}
        self.selected = None
        self.hud_buttons = []
        self.shake = 0.0
        self.time = 0.0
        self.result_shown = False
        self.paused = False
        self.level_name = L.get('name', '')

        for p in L['platforms']:
            self.world.add_platform(p)

        def spawn_pirate(sp, team, type_):
            pir = Pirate(sp['x'], sp['y'], {'team': team, 'type': type_})
            if team == 'blue':
                pir.band_color = '#1d5fe0'
            self.world.add_body(pir.body)
            return pir

        if self.mode == 'arena':
            for sp in L['players']:
                self.players.append(spawn_pirate(sp, 'red', 'player'))
            for sp in L['blue']:
                self.blue_team.append(spawn_pirate(sp, 'blue', 'player'))
            self.weapons = L['weapons']
        else:
            for sp in L['players']:
                self.players.append(spawn_pirate(sp, 'player', 'player'))
            for e in L['enemies']:
                pir = spawn_pirate(e, 'enemy', e['type'])
                cfg = PIRATE_TYPES[e['type']]
                pir.ai_t = 1.5 + random_num() * 2
                pir.ai_cd = list(cfg['ai_cd'])
                self.enemies.append(pir)
            self.weapons = L['weapons']
        for g in L['gold']:
            self.treasures.append(Treasure(g['x'], g['y']))

    # ---------- 触摸 ----------
    def on_touch_down(self, sx, sy):
        if self.paused or self.result_shown:
            return False
        # HUD 按钮
        for b in self.hud_buttons:
            if b['x'] <= sx <= b['x'] + b['w'] and b['y'] <= sy <= b['y'] + b['h']:
                self._on_hud(b['id'])
                return True

        wx, wy = self.renderer.screen_to_world(sx, sy)
        hit = self._pirate_at(wx, wy)

        # 船锚模式
        if self.selected and self.selected.weapon == 'anchor' and self.selected.alive and not self.selected.dead:
            on_self = hit and hit is self.selected
            if not on_self:
                self.spawn_anchor(wx)
                self.sound.play('throw')
                self.selected.throw_cd = max(self.selected.throw_cd, 0.8)
                return True

        if hit:
            if self._is_controllable(hit):
                if self.selected is not hit:
                    self.selected = hit
                    self.sound.play('select')
                self.aims[self._aim_next_tid] = {'p': hit, 'sx': sx, 'sy': sy, 'cx': sx, 'cy': sy, 'dragging': False}
                self._aim_next_tid += 1
                return True
            else:
                self.selected = None
                return True

        self.selected = None
        return False

    def on_touch_move(self, tid, sx, sy):
        aim = self.aims.get(tid)
        if not aim:
            return
        aim['cx'] = sx
        aim['cy'] = sy
        dx = aim['cx'] - aim['sx']
        dy = aim['cy'] - aim['sy']
        if not aim['dragging'] and math.hypot(dx, dy) > TAP_THRESHOLD:
            aim['dragging'] = True

    def on_touch_up(self, tid, sx, sy):
        aim = self.aims.pop(tid, None)
        if not aim:
            return
        p = aim['p']
        if p.dead or not p.alive:
            return
        if aim['dragging']:
            w_start = self.renderer.screen_to_world(aim['sx'], aim['sy'])
            w_cur = self.renderer.screen_to_world(aim['cx'], aim['cy'])
            if p.weapon == 'move':
                p.move_to(w_cur[0], w_cur[1])
                self.sound.play('click')
                return
            if p.throw_cd > 0:
                self.sound.play('click')
                return
            vx = (w_start[0] - w_cur[0]) * THROW_K
            vy = (w_start[1] - w_cur[1]) * THROW_K
            sp = math.hypot(vx, vy)
            max_sp = p.throw_speed
            if sp > max_sp:
                k = max_sp / sp
                self._throw_weapon(p, vx * k, vy * k)
            elif sp >= THROW_MIN:
                self._throw_weapon(p, vx, vy)

    def _is_controllable(self, p):
        if self.mode == 'arena':
            return True
        return p.team == 'player'

    def _pirate_at(self, wx, wy):
        all_p = self.players + self.enemies + self.blue_team
        best = None
        best_d = 1e9
        for p in all_p:
            if p.dead:
                continue
            d = math.hypot(p.x - wx, p.y - wy)
            if d < p.body.r + 12 and d < best_d:
                best = p
                best_d = d
        return best

    def _on_hud(self, hid):
        if hid == 'pause':
            self.sound.play('click')
            if self.on_pause:
                self.on_pause()
        elif hid.startswith('weapon_'):
            w = hid[7:]
            if self.selected and w in self.weapons:
                self.selected.weapon = w
                self.sound.play('click')

    # ---------- 投掷 ----------
    def _throw_weapon(self, p, vx, vy):
        p.face = 1 if vx >= 0 else -1
        p.throw_cd = 1.2
        p.squash = 0.25
        sx = p.x + (p.body.r + 4 if vx >= 0 else -p.body.r - 4)
        sy = p.y - 6
        if p.weapon == 'bomb':
            b = Bomb(sx, sy, vx, vy, {'owner': p})
            self.world.add_body(b.body)
            self.projectiles.append(b)
        elif p.weapon == 'firebomb':
            b = FireBomb(sx, sy, vx, vy, {'owner': p})
            self.world.add_body(b.body)
            self.projectiles.append(b)
        elif p.weapon == 'crate':
            c = Crate(sx, sy)
            c.body.set_velocity(vx, vy)
            self.world.add_body(c.body)
            self.crates.append(c)
        elif p.weapon == 'barrel':
            b = Barrel(sx, sy)
            b.body.set_velocity(vx, vy)
            self.world.add_body(b.body)
            self.barrels.append(b)
        self.sound.play('throw')

    def spawn_anchor(self, x):
        a = Anchor(x, -40)
        self.world.add_body(a.body)
        self.projectiles.append(a)

    # ---------- 世界反馈 ----------
    def damage_area(self, x, y, radius, damage, impulse):
        def on_hit(b, fall, d):
            ent = b.entity
            if not ent:
                return
            if ent.kind == 'pirate':
                ent.hurt(damage * fall, x, y)
            elif ent.kind == 'barrel':
                ent.ignite(self)
            elif ent.kind == 'crate':
                ent.hurt(damage * fall)
        self.world.explode(x, y, radius, damage, impulse, on_hit)

    def explode_at(self, x, y, radius, damage, impulse, source):
        self.damage_area(x, y, radius, damage, impulse)
        big = radius > 200
        self.effects.append({'x': x, 'y': y, 'radius': radius, 't': 0, 'dur': 0.5,
                             'color': '#ffd54a' if big else '#ff8a4a'})
        self.effects.append({'x': x, 'y': y, 'radius': radius * 0.5, 't': 0, 'dur': 0.35, 'color': '#ffffff'})
        self.particles.burst(x, y, 42 if big else 26, '#ffb347' if big else '#ff7b1f',
                             420 if big else 320, 5, 0.8)
        self.particles.burst(x, y, 26 if big else 14, '#ffffff', 360 if big else 260, 4, 0.5)
        self.particles.smoke(x, y, 12 if big else 6)
        self.shake = max(self.shake, 14 if big else 8)
        self.sound.play('bigExplode' if big else 'explosion')

    def spawn_fire(self, x, y):
        self.fires.append(Fire(x, y))
        self.particles.flame(x, y, 8, '#ff8a1f')

    def on_drown(self, pir):
        if pir.dead:
            return
        pir.kill('water')
        self.particles.water(pir.x, pir.y + pir.body.r, 16)
        self.sound.play('splash')

    # ---------- 更新 ----------
    def update(self, dt):
        self.time += dt
        self.shake *= math.pow(0.001, dt)

        for p in self.players:
            p.update(dt, self.world, self)
        for p in self.enemies:
            p.update(dt, self.world, self)
        for p in self.blue_team:
            p.update(dt, self.world, self)

        # 投掷物
        for i in range(len(self.projectiles) - 1, -1, -1):
            pr = self.projectiles[i]
            pr.update(dt, self.world, self)
            if pr.kind == 'anchor':
                remove = pr.dead
            elif pr.kind == 'bomb':
                remove = pr.exploded
            elif pr.kind == 'firebomb':
                remove = pr.ignited
            else:
                remove = False
            if remove:
                self.world.remove_body(pr.body)
                del self.projectiles[i]

        # 火焰
        for i in range(len(self.fires) - 1, -1, -1):
            f = self.fires[i]
            f.update(dt, self.world, self)
            if f.life <= 0:
                del self.fires[i]

        # 火药桶
        for i in range(len(self.barrels) - 1, -1, -1):
            b = self.barrels[i]
            b.update(dt, self.world, self)
            if b.dead:
                self.world.remove_body(b.body)
                del self.barrels[i]

        # 板条箱
        for i in range(len(self.crates) - 1, -1, -1):
            c = self.crates[i]
            c.update(dt, self.world, self)
            if c.dead:
                self.particles.burst(c.x, c.y, 10, '#a9713b', 200, 4, 0.6)
                self.world.remove_body(c.body)
                del self.crates[i]

        self.world.step(dt)

        if self.mode == 'level':
            self._update_ai(dt)

        self._cleanup_dead(self.players)
        self._cleanup_dead(self.enemies)
        self._cleanup_dead(self.blue_team)

        self.particles.update(dt)
        for i in range(len(self.effects) - 1, -1, -1):
            e = self.effects[i]
            e['t'] += dt
            if e['t'] >= e['dur']:
                del self.effects[i]

        self._update_camera(dt)
        self._check_result()

    def _cleanup_dead(self, lst):
        for i in range(len(lst) - 1, -1, -1):
            p = lst[i]
            if p.dead and p.death_t > 2.5:
                if p.cause == 'water':
                    self.particles.water(p.x, p.y, 10)
                self.world.remove_body(p.body)
                del lst[i]

    def _update_camera(self, dt):
        cx = WORLD_W / 2
        cy = WORLD_H / 2
        pts = [p for p in self.players + self.enemies + self.blue_team if not p.dead]
        if pts:
            sx = sum(p.x for p in pts) / len(pts)
            sy = sum(p.y for p in pts) / len(pts)
            cx, cy = sx, sy
        self.renderer._update_cam(cx, cy)
        if self.shake > 0.5:
            self.renderer.cam['x'] += (random_num() - 0.5) * self.shake
            self.renderer.cam['y'] += (random_num() - 0.5) * self.shake

    # ---------- AI ----------
    def _update_ai(self, dt):
        for e in self.enemies:
            if e.dead:
                continue
            e.ai_t -= dt
            if e.ai_t > 0:
                continue
            cfg = PIRATE_TYPES[e.type]
            e.ai_t = cfg['ai_cd'][0] + random_num() * (cfg['ai_cd'][1] - cfg['ai_cd'][0])

            target = None
            best = 1e9
            for p in self.players:
                if p.dead:
                    continue
                d = math.hypot(p.x - e.x, p.y - e.y)
                if d < best:
                    best = d
                    target = p
            if not target:
                continue

            if best > 420 and e.body.grounded and random_num() < 0.3:
                direction = 1 if target.x > e.x else -1
                e.move_to(e.x + direction * (120 + random_num() * 200), e.y)
            elif best < 200 and e.body.grounded and random_num() < 0.3:
                direction = 1 if target.x > e.x else -1
                e.move_to(e.x - direction * (160 + random_num() * 120), e.y)

            v0 = cfg['throw_spd'] * (0.92 + random_num() * 0.16)
            sol = solve_throw(e.x, e.y - 8, target.x, target.y - 4, v0)
            if sol:
                sol['vx'] += (random_num() - 0.5) * 90
                sol['vy'] += (random_num() - 0.5) * 60
                b = Bomb(e.x + math.copysign(12, sol['vx'] or 1), e.y - 6,
                         sol['vx'], sol['vy'], {'owner': e})
                self.world.add_body(b.body)
                self.projectiles.append(b)
                e.throw_cd = 0.6
                self.sound.play('throw')

    # ---------- 胜负判定 ----------
    def _check_result(self):
        if self.result_shown:
            return
        if self.mode == 'arena':
            red_alive = any(not p.dead for p in self.players)
            blue_alive = any(not p.dead for p in self.blue_team)
            if blue_alive and not red_alive:
                self._finish('lose', '红方战败')
            elif red_alive and not blue_alive:
                self._finish('win', '红方获胜！')
        else:
            enemy_alive = any(not p.dead for p in self.enemies)
            player_alive = any(not p.dead for p in self.players)
            if not enemy_alive:
                save_progress(self.level_number + 1)
                self._finish('win', None)
            elif not player_alive:
                self._finish('lose', None)

    def _finish(self, kind, custom_title):
        self.result_shown = True
        self.sound.play('win' if kind == 'win' else 'lose')
        if self.on_result:
            self.on_result(kind, custom_title)


def random_num():
    import random
    return random.random()
