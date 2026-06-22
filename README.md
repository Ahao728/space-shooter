# 🚀 打飞机 · Space Shooter

经典纵版太空射击游戏，基于 Pygame 开发。**现已支持手机浏览器触屏游玩！**

## 🎮 在线试玩

**👉 [点击这里开始游戏](https://ahao728.github.io/space-shooter/) 👈**

> 支持 PC 键盘操作 & 手机触屏操控，打开浏览器就能玩！

## 🕹️ 操作方式

### PC 端（键盘）
| 按键 | 功能 |
|------|------|
| 方向键 / WASD | 移动飞船 |
| 自动连射 | 无需按键 |
| P | 暂停 |
| B | 清屏炸弹 |
| R | 游戏结束后重新开始 |
| ESC | 退出 |

### 📱 手机端（触屏）
| 控件 | 位置 | 功能 |
|------|------|------|
| 🕹️ 滑动屏幕 | 屏幕 | 移动飞船 |
| 💣 B 按钮 | 右下角 | 清屏炸弹 |
| ⏸ 暂停按钮 | 右上角 | 暂停/继续 |

## ✨ 游戏特色

- 🎯 **自动射击** — 专注走位，火力全自动
- 💥 **多种敌机** — 小飞机、大飞机、Boss 陆续登场
- ⚡ **丰富道具** —
  - 🔫 三连射 — 扇形三发
  - ⏩ 速射 — 双倍射速
  - 🛡️ 护盾 — 抵挡一次伤害
  - 💘 生命 — 恢复 1 命
  - 🧨 炸弹 — 清屏灭敌
  - 💉 穿透弹 — 子弹穿透敌机
- 🌟 **粒子爆炸** — 击毁敌机华丽特效
- 📊 **HUD 状态栏** — 实时显示武器增益 & 倒计时
- 🌌 **视差星空** — 三层纵深背景

## 🖥️ 本地运行

```bash
# 安装依赖
pip install pygame

# 运行游戏
python main.py
```

### 构建 Web 版本

```bash
pip install pygbag
pygbag .
# 然后在浏览器打开 http://localhost:8000
```

## 🛠️ 技术栈

- **Python 3** + **Pygame** 游戏引擎
- **pygbag** — 编译为 WebAssembly 在浏览器运行
- **GitHub Pages** — 自动部署托管

## 📁 项目结构

```
space_shooter/
├── main.py             # 游戏入口 & 主循环
├── player.py           # 玩家飞船
├── enemy.py            # 敌机 & Boss
├── bullet.py           # 子弹系统
├── powerup.py          # 道具掉落
├── explosion.py        # 爆炸特效
├── starfield.py        # 视差星空
├── settings.py         # 全局常量
├── ui.py               # HUD / 菜单 / 按钮
├── mobile_controls.py  # 手机触屏虚拟控件
├── assets/             # 图片素材
├── index.html          # Web 入口
└── .github/workflows/  # 自动部署 CI
```

## 📄 License

MIT
