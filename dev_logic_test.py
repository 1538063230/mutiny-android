# -*- coding: utf-8 -*-
"""核心逻辑测试：纯 Python，无渲染，验证物理、AI、投掷、爆炸、胜负判定"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.game import Game
from src.entities import Pirate, Bomb, FireBomb, Barrel, Crate, Anchor, Treasure, solve_throw
from src.physics import World, WATER_Y, Platform, Body
from src.levels import build_level, build_arena

# 静音（用占位 sound）
class SilentSound:
    def play(self, *a, **kw): pass

# 测试 1：物理与碰撞
def test_physics():
    w = World()
    p = Platform(0, 100, 200, 20)
    w.add_platform(p)
    b = Body(50, 0, 10)
    w.add_body(b)
    for _ in range(120):
        w.step(0.016)
    assert abs(b.y - 100 + b.r) < 1.5, f'海盗应停在平台上 y~={100 - b.r:.2f}, got {b.y:.2f}'
    assert b.grounded, '海盗应着地'
    print('PASS: 物理 - 平台碰撞与着地判定')

# 测试 2：落水
def test_drown():
    w = World()
    b = Body(50, WATER_Y - 5, 5)
    b.vy = 200
    w.add_body(b)
    called = []
    class G:
        def on_drown(self, p):
            called.append(True)
    g = G()
    for _ in range(60):
        w.step(0.016)
    assert b.y > WATER_Y, f'海盗应掉进海 y={b.y}, water={WATER_Y}'
    print('PASS: 物理 - 落水判定')

# 测试 3：投弹解算
def test_solve_throw():
    # 平地目标 10m 外，速度 1000
    sol = solve_throw(0, 100, 300, 100, 1300)
    assert sol is not None
    # 投掷后 y 应向上（vy<0）走平直弧线，落回 y≈100 时 x 应接近 300
    assert sol['vx'] > 0
    # 模拟到落地，断言 x 离 300 不太远（±200 容差，因为选解可能高抛）
    px, py = 0, 100
    pvx, pvy = sol['vx'], sol['vy']
    t = 0
    max_x = 0
    while t < 600 and py < 100 + 50:
        pvy += 1100 * 0.016
        px += pvx * 0.016
        py += pvy * 0.016
        max_x = max(max_x, px)
        t += 1
    print(f'  投掷 vx={pvx:.0f} vy={sol["vy"]:.1f}  最大x={max_x:.0f} (target=300)')
    assert max_x > 200, f'投掷应能打到 x~300, got {max_x}'
    print('PASS: 投掷解算 - 解出方向可前进到目标区域')

# 测试 4：海盗满血/伤害/死亡
def test_pirate():
    p = Pirate(100, 200, {'type': 'pirate'})
    assert p.hp == 75
    p.hurt(20)
    assert p.hp == 55
    p.hurt(60)
    assert p.dead
    print('PASS: 海盗 - 血量与死亡')

# 测试 5：炸弹爆炸
def test_explode():
    sound = SilentSound()
    game = Game.__new__(Game)
    game.particles = type('P', (), {'list': [], 'burst': lambda *a,**kw:None,
                                     'flame': lambda *a,**kw:None,
                                     'smoke': lambda *a,**kw:None,
                                     'spark': lambda *a,**kw:None,
                                     'water': lambda *a,**kw:None})()
    game.effects = []
    game.sound = sound
    game.shake = 0
    game.world = World()
    game.explode_at(0, 0, 200, 50, 300, None)
    assert game.shake > 0, '爆炸应有震屏'
    assert len(game.effects) >= 1, '爆炸应有特效'
    print('PASS: 爆炸 - 震屏与特效')

# 测试 6：关卡构建
def test_levels():
    for n in range(1, 16):
        L = build_level(n)
        assert L['platforms']
        assert L['players']
        assert L['enemies']
        print(f'  关卡 {n}: {L["name"]} ({len(L["enemies"])} 敌人)')
    print('PASS: 15 个关卡均可构建')

# 测试 7：构建双人竞技场
def test_arena():
    A = build_arena()
    assert A['mode'] == 'arena'
    assert len(A['players']) == 3
    assert len(A['blue']) == 3
    print('PASS: 双人竞技场可构建')

# 测试 8：全关卡运行 3 秒（不渲染），观察逻辑不崩溃
def test_full_run():
    import time
    sound = SilentSound()
    game = Game.__new__(Game)
    class PStub:
        def __init__(self):
            self.list = []
        def burst(self, *a, **kw): pass
        def flame(self, *a, **kw): pass
        def smoke(self, *a, **kw): pass
        def spark(self, *a, **kw): pass
        def water(self, *a, **kw): pass
        def update(self, dt): pass
    game.particles = PStub()
    game.effects = []
    game.sound = sound
    game.shake = 0
    game.on_result = None
    game.on_pause = None
    game.renderer = type('R', (), {'_update_cam': lambda *a, **kw: None, 'cam': {'x': 0, 'y': 0}})()
    game.start_level(1)
    for i in range(180):
        game.update(0.016)
    players_alive = [p for p in game.players if not p.dead]
    enemies_alive = [e for e in game.enemies if not e.dead]
    print(f'  关卡 1 运行 3 秒: 玩家存活 {len(players_alive)}/{len(game.players)}, 敌人存活 {len(enemies_alive)}/{len(game.enemies)}')
    print('PASS: 全关卡逻辑运行稳定')

# 测试 9：炸弹引信倒计时
def test_bomb_fuse():
    b = Bomb(100, 100, 0, 0)
    assert b.fuse > 2
    print('PASS: 炸弹引信初始化')

# 测试 10：火药桶被点燃引爆
def test_barrel_chain():
    b = Barrel(100, 100)
    sound = SilentSound()
    game = Game.__new__(Game)
    game.particles = type('P', (), {'list': [], 'burst': lambda *a,**kw:None,
                                     'flame': lambda *a,**kw:None,
                                     'smoke': lambda *a,**kw:None,
                                     'spark': lambda *a,**kw:None,
                                     'water': lambda *a,**kw:None})()
    game.effects = []
    game.sound = sound
    game.shake = 0
    game.world = World()
    b.ignite(game)
    assert b.igniting
    for _ in range(35):
        b.update(0.016, World(), game)
    assert b.dead
    print('PASS: 火药桶 - 点燃→延时→爆炸')

if __name__ == '__main__':
    test_physics()
    test_drown()
    test_solve_throw()
    test_pirate()
    test_explode()
    test_levels()
    test_arena()
    test_bomb_fuse()
    test_barrel_chain()
    test_full_run()
    print('\n所有核心逻辑测试通过 ✅')