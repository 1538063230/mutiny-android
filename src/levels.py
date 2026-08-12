# -*- coding: utf-8 -*-
"""关卡系统：15 个单人关卡 + 双人竞技场
移植自 H5 版 levels.js"""
from .physics import Platform

# 平台 [x, y, w, h]；出生点 [x, y, team]；敌人 [x, y, type]；宝藏 [x, y]

LEVELS = [
    {'name': '新手教程 · 熊孩子来袭', 'plat': [[140, 860, 760, 130], [1080, 920, 700, 80]],
     'pl': [[300, 838]], 'en': [[620, 838, 'child'], [760, 838, 'child'], [1300, 898, 'child']],
     'weapons': ['move', 'bomb'], 'gold': [[200, 830]]},
    {'name': '墨鱼怪军团', 'plat': [[80, 880, 420, 120], [620, 850, 420, 150], [1160, 900, 460, 100], [1620, 860, 340, 140], [700, 700, 240, 40]],
     'pl': [[220, 858]], 'en': [[840, 828, 'squid'], [960, 828, 'squid'], [1300, 878, 'squid'], [1450, 878, 'squid'], [1700, 838, 'squid'], [720, 660, 'squid'], [850, 660, 'squid']],
     'weapons': ['move', 'bomb', 'firebomb', 'crate', 'barrel', 'anchor'], 'gold': [[120, 848], [1680, 828]]},
    {'name': '海贼突袭', 'plat': [[100, 870, 500, 120], [760, 830, 420, 170], [1300, 880, 500, 120], [420, 700, 260, 44], [1550, 720, 260, 44]],
     'pl': [[260, 848], [340, 848]], 'en': [[900, 808, 'squid'], [980, 808, 'pirate'], [1420, 858, 'squid'], [1580, 858, 'pirate']],
     'weapons': ['move', 'bomb', 'firebomb', 'crate', 'barrel', 'anchor'], 'gold': [[150, 838], [1750, 848]]},
    {'name': '浮岛猎手', 'plat': [[60, 900, 380, 100], [560, 860, 360, 140], [1040, 900, 380, 100], [1500, 840, 460, 160], [880, 680, 300, 44], [330, 620, 220, 40]],
     'pl': [[200, 878], [300, 878]], 'en': [[650, 838, 'pirate'], [730, 838, 'pirate'], [1180, 878, 'squid'], [1600, 818, 'squid'], [960, 660, 'pirate'], [400, 600, 'child']],
     'weapons': ['move', 'bomb', 'firebomb', 'crate', 'barrel', 'anchor'], 'gold': [[110, 868], [1930, 808]]},
    {'name': '双岛血战', 'plat': [[100, 850, 640, 150], [1260, 850, 640, 150], [820, 720, 380, 40], [500, 560, 300, 44], [1400, 560, 300, 44]],
     'pl': [[260, 828], [360, 828]], 'en': [[1380, 828, 'pirate'], [1520, 828, 'pirate'], [1660, 828, 'pirate'], [1000, 700, 'elite']],
     'weapons': ['move', 'bomb', 'firebomb', 'crate', 'barrel', 'anchor'], 'gold': [[130, 818], [1700, 818]]},
    {'name': '迷宫群岛', 'plat': [[60, 880, 300, 120], [420, 830, 300, 170], [780, 900, 260, 100], [1080, 800, 300, 200], [1440, 900, 260, 100], [1700, 840, 260, 160], [950, 640, 220, 40], [1500, 620, 240, 44]],
     'pl': [[180, 858], [500, 808]], 'en': [[860, 878, 'squid'], [1200, 778, 'pirate'], [1300, 778, 'pirate'], [1550, 878, 'pirate'], [1800, 818, 'elite'], [1000, 620, 'squid']],
     'weapons': ['move', 'bomb', 'firebomb', 'crate', 'barrel', 'anchor'], 'gold': [[90, 848], [1900, 808]]},
    {'name': '高地争夺', 'plat': [[120, 920, 360, 80], [700, 800, 420, 200], [1300, 900, 300, 100], [1750, 820, 200, 180], [600, 600, 240, 40], [1350, 620, 220, 40], [900, 440, 200, 36]],
     'pl': [[240, 898], [1400, 878]], 'en': [[820, 778, 'pirate'], [900, 778, 'pirate'], [1450, 878, 'squid'], [1600, 878, 'squid'], [1850, 798, 'pirate'], [700, 580, 'elite'], [1450, 600, 'child']],
     'weapons': ['move', 'bomb', 'firebomb', 'crate', 'barrel', 'anchor'], 'gold': [[150, 888], [950, 420]]},
    {'name': '风浪之岛', 'plat': [[60, 880, 340, 120], [520, 840, 360, 160], [1000, 920, 300, 80], [1400, 850, 560, 150], [820, 660, 280, 40], [1560, 620, 240, 44], [240, 600, 240, 40]],
     'pl': [[200, 858], [300, 858]], 'en': [[640, 818, 'pirate'], [1120, 898, 'pirate'], [1520, 828, 'elite'], [1750, 828, 'pirate'], [900, 640, 'squid'], [300, 580, 'pirate'], [1660, 600, 'squid']],
     'weapons': ['move', 'bomb', 'firebomb', 'crate', 'barrel', 'anchor'], 'gold': [[90, 848], [1930, 818]]},
    {'name': '炮火连天', 'plat': [[100, 850, 560, 150], [760, 780, 480, 220], [1380, 880, 560, 120], [620, 620, 240, 40], [1200, 640, 240, 40], [940, 480, 220, 36]],
     'pl': [[260, 828], [360, 828], [1400, 858]], 'en': [[900, 758, 'pirate'], [1000, 758, 'pirate'], [1500, 858, 'pirate'], [1700, 858, 'elite'], [700, 600, 'pirate'], [1300, 620, 'pirate'], [1000, 460, 'elite']],
     'weapons': ['move', 'bomb', 'firebomb', 'crate', 'barrel', 'anchor'], 'gold': [[130, 818], [1030, 440]]},
    {'name': '暗礁奇袭', 'plat': [[40, 900, 300, 100], [420, 820, 340, 180], [860, 900, 300, 100], [1280, 840, 380, 160], [1720, 860, 240, 140], [740, 640, 260, 40], [1500, 660, 240, 44], [1050, 540, 240, 40]],
     'pl': [[180, 878], [500, 798]], 'en': [[960, 878, 'pirate'], [1400, 818, 'elite'], [1560, 818, 'pirate'], [1820, 838, 'pirate'], [820, 620, 'pirate'], [1600, 640, 'squid'], [1140, 520, 'pirate']],
     'weapons': ['move', 'bomb', 'firebomb', 'crate', 'barrel', 'anchor'], 'gold': [[70, 868], [1960, 830]]},
    {'name': '宝藏竞技场', 'plat': [[100, 860, 420, 140], [700, 800, 400, 200], [1280, 850, 420, 150], [1720, 880, 240, 120], [560, 620, 240, 40], [1180, 600, 240, 44], [900, 420, 200, 36]],
     'pl': [[250, 838], [350, 838], [1400, 828]], 'en': [[820, 778, 'elite'], [900, 778, 'pirate'], [1450, 828, 'pirate'], [1600, 828, 'pirate'], [640, 600, 'pirate'], [1280, 580, 'pirate'], [950, 400, 'elite']],
     'weapons': ['move', 'bomb', 'firebomb', 'crate', 'barrel', 'anchor'], 'gold': [[130, 828], [950, 380], [1950, 848]]},
    {'name': '幽灵船队', 'plat': [[60, 900, 320, 100], [500, 840, 360, 160], [960, 890, 320, 110], [1400, 820, 360, 180], [1800, 860, 180, 140], [740, 660, 260, 40], [1500, 640, 240, 44], [1120, 520, 220, 40]],
     'pl': [[200, 878], [620, 818]], 'en': [[1080, 868, 'pirate'], [1180, 868, 'pirate'], [1520, 798, 'pirate'], [1640, 798, 'elite'], [1850, 838, 'pirate'], [820, 640, 'pirate'], [1600, 620, 'pirate'], [1220, 500, 'pirate']],
     'weapons': ['move', 'bomb', 'firebomb', 'crate', 'barrel', 'anchor'], 'gold': [[90, 868], [1930, 830]]},
    {'name': '绝境求生', 'plat': [[80, 880, 340, 120], [540, 810, 380, 190], [1040, 870, 360, 130], [1480, 830, 480, 170], [640, 640, 240, 40], [1380, 660, 240, 44], [980, 500, 220, 40], [1560, 520, 220, 40]],
     'pl': [[220, 858], [1150, 848]], 'en': [[660, 788, 'elite'], [740, 788, 'pirate'], [1180, 848, 'pirate'], [1280, 848, 'pirate'], [1620, 808, 'pirate'], [1750, 808, 'elite'], [720, 620, 'pirate'], [1500, 640, 'pirate']],
     'weapons': ['move', 'bomb', 'firebomb', 'crate', 'barrel', 'anchor'], 'gold': [[110, 848], [1050, 470], [1950, 798]]},
    {'name': '无尽炮击', 'plat': [[60, 860, 360, 140], [560, 820, 380, 180], [1080, 880, 340, 120], [1540, 840, 420, 160], [660, 640, 240, 40], [1420, 640, 240, 44], [980, 460, 220, 40], [250, 620, 220, 40], [1720, 580, 200, 40]],
     'pl': [[200, 838], [300, 838], [1240, 858]], 'en': [[700, 798, 'pirate'], [800, 798, 'pirate'], [1200, 858, 'elite'], [1300, 858, 'pirate'], [1680, 818, 'pirate'], [1800, 818, 'pirate'], [740, 620, 'pirate'], [1520, 620, 'pirate'], [1040, 440, 'pirate']],
     'weapons': ['move', 'bomb', 'firebomb', 'crate', 'barrel', 'anchor'], 'gold': [[90, 828], [1960, 808]]},
    {'name': '决战 · 夺回宝藏', 'plat': [[80, 860, 380, 140], [560, 800, 380, 200], [1060, 860, 380, 140], [1540, 820, 400, 180], [640, 630, 240, 40], [1380, 630, 240, 44], [960, 460, 220, 40], [1300, 340, 240, 40]],
     'pl': [[220, 838], [340, 838], [1220, 838], [1320, 838]], 'en': [[700, 778, 'elite'], [800, 778, 'pirate'], [1180, 838, 'pirate'], [1280, 838, 'elite'], [1700, 798, 'pirate'], [1820, 798, 'pirate'], [720, 610, 'pirate'], [1480, 610, 'pirate'], [1000, 440, 'pirate'], [1380, 320, 'pirate']],
     'weapons': ['move', 'bomb', 'firebomb', 'crate', 'barrel', 'anchor'], 'gold': [[110, 828], [1930, 788]]},
]

# 双人对战竞技场
ARENA = {
    'plat': [[80, 880, 380, 120], [620, 830, 380, 170], [1200, 830, 380, 170], [1740, 880, 180, 120], [810, 660, 220, 40], [1390, 660, 220, 40]],
    'red': [[200, 858], [300, 858], [1760, 858]],
    'blue': [[1380, 808], [1480, 808], [1580, 808]],
    'weapons': ['move', 'bomb', 'firebomb', 'crate', 'barrel', 'anchor'],
}

TOTAL_LEVELS = len(LEVELS)

# 通关进度存储（Android 用系统偏好；桌面 fallback 到文件）
SAVE_KEY = 'mutiny_progress'


def _load_progress():
    try:
        from kivy.app import App
        app = App.get_running_app()
        if app and hasattr(app, 'get_progress'):
            return app.get_progress()
    except Exception:
        pass
    import os
    try:
        p = os.path.join(os.path.expanduser('~'), '.mutiny_progress')
        if os.path.exists(p):
            return int(open(p).read().strip())
    except Exception:
        pass
    return 1


def _save_progress(n):
    try:
        from kivy.app import App
        app = App.get_running_app()
        if app and hasattr(app, 'save_progress'):
            app.save_progress(n)
            return
    except Exception:
        pass
    import os
    try:
        p = os.path.join(os.path.expanduser('~'), '.mutiny_progress')
        open(p, 'w').write(str(n))
    except Exception:
        pass


def get_progress():
    return max(1, _load_progress())


def save_progress(n):
    cur = get_progress()
    if n > cur:
        _save_progress(n)


def reset_progress():
    try:
        _save_progress(1)
    except Exception:
        pass


def build_level(n):
    d = LEVELS[min(n - 1, len(LEVELS) - 1)]
    platforms = [Platform(p[0], p[1], p[2], p[3]) for p in d['plat']]
    return {
        'number': n,
        'name': d['name'],
        'platforms': platforms,
        'players': [{'x': p[0], 'y': p[1], 'team': 'player'} for p in d['pl']],
        'enemies': [{'x': e[0], 'y': e[1], 'type': e[2]} for e in d['en']],
        'weapons': list(d['weapons']),
        'gold': [{'x': g[0], 'y': g[1]} for g in d['gold']],
    }


def build_arena():
    return {
        'mode': 'arena',
        'name': '双人对战',
        'platforms': [Platform(p[0], p[1], p[2], p[3]) for p in ARENA['plat']],
        'players': [{'x': p[0], 'y': p[1], 'team': 'red'} for p in ARENA['red']],
        'blue': [{'x': p[0], 'y': p[1], 'team': 'blue'} for p in ARENA['blue']],
        'weapons': list(ARENA['weapons']),
        'gold': [],
    }
