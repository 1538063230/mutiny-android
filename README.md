# 海盗军团抢宝藏（手机版 - 安卓 APP）

复刻 Nitrome 经典 Flash 小游戏《Mutiny · 海盗军团抢宝藏》的 Kivy 安卓应用。
所有 15 关单人闯关 + 双人对战、触屏拖拽瞄准投掷、5 种道具、AI、爆炸/火焰/船锚特效全部移植实现。

## 电脑开发/调试

```bash
cd android_app
python dev_test.py        # 自动化截图测试
python dev_logic_test.py  # 核心逻辑测试
python dev_run.py         # 实际运行（可玩）
```

## 打包安卓 APK

> ⚠️ Buildozer 仅在 Linux/macOS 上运行。如果当前是 Windows，请使用 WSL2、Docker，或在 Linux 服务器上打包。

### Linux/macOS：
```bash
cd android_app
pip install buildozer
buildozer android debug   # 生成 APK（首次耗时较长，会下载 NDK/SDK）
```

APK 输出路径：`bin/mutiny-1.0.0-debug.apk`，用 `adb install` 或直接传到手机安装。

### Windows (WSL2)：
```bash
wsl
cd /mnt/c/Users/.../android_app
pip install buildozer
buildozer android debug
```

### 云端打包（最快）：
- 上传代码到 GitHub，用 **GitHub Actions** 跑 buildozer（示例 workflow 见 `.github/workflows/`）
- 或上传到 **Replit / Google Cloud Shell** 远程执行打包

## 文件结构

```
android_app/
├── main.py               # App 入口 + 导航 + 进度存储
├── buildozer.spec        # 打包配置
├── assets/               # 静态资源（中文字体等）
│   └── simhei.ttf
├── dev_test.py           # 截图测试
├── dev_logic_test.py     # 逻辑单元测试
├── dev_run.py            # 开发模式启动
└── src/
    ├── __init__.py
    ├── gamecanvas.py     # 战斗画布 Widget（触摸、循环）
    ├── game.py           # 主逻辑（AI、胜负、爆炸）
    ├── scene.py          # 场景渲染（海盗/道具/HUD）
    ├── render.py         # Kivy 像素绘制 + 离屏纹理
    ├── entities.py       # 实体系统（海盗/炸弹/火焰等）
    ├── physics.py        # 2D 物理引擎
    ├── levels.py         # 15 关关卡数据
    ├── audio.py          # 程序化音效
    └── ui.py             # 菜单/选关/结算/暂停 UI
```

## 玩法说明

- 目标：消灭所有敌人
- 操作：点击选中海盗 → 选道具 → 按住拖拽瞄准 → 松手投掷
- 道具：炸弹(范围爆炸)、燃烧弹(地面火焰)、火药桶(大爆炸)、板条箱(掩体)、船锚(天降)

## 已实现功能

✓ 触屏拖拽瞄准投掷（带抛物线虚线）
✓ 5 种道具与对应物理/爆炸/火焰/燃烧效果
✓ 火药桶被点燃延时爆炸链式触发
✓ 落水判定与淘汰机制
✓ 敌方 AI（自动瞄准、随机走位、随机误差）
✓ 15 关单人 + 双人竞技场
✓ 解锁进度保存（SharedPreferences）
✓ 程序化合成音效（无音频文件）
✓ 横屏锁定 + 多分辨率自适应
✓ 中文 UI（自带 SimHei 中文字体）

## 截图

桌面测试截图保存在 `screenshots/`：
- `menu.png` - 主菜单
- `about.png` - 游戏说明
- `levels.png` - 选关
- `game_initial.png` - 战斗初始
- `game_throw.png` - 投弹中