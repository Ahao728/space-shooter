"""
settings.py — 游戏全局常量
打飞机 Space Shooter
"""
import os
import sys

# ── 素材路径（兼容 PyInstaller 打包）──
if getattr(sys, 'frozen', False):
    _BASE = sys._MEIPASS
else:
    _BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(_BASE, "assets")

# ── 屏幕 ──
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "打飞机"

# ── 颜色 (RGB) ──
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (80, 80, 80)
LIGHT_GRAY = (160, 160, 160)
RED = (255, 60, 60)
GREEN = (60, 255, 120)
BLUE = (60, 140, 255)
CYAN = (0, 220, 255)
YELLOW = (255, 220, 40)
ORANGE = (255, 150, 30)
PURPLE = (180, 60, 255)

# ── 玩家 ──
PLAYER_SPEED = 6
PLAYER_SIZE = 24          # 飞船三角形边长
PLAYER_COLOR = CYAN
PLAYER_GLOW = (0, 150, 200)

# ── 子弹 ──
BULLET_SPEED = -10         # 负值 = 向上
BULLET_SIZE = (3, 14)      # 宽 x 高
BULLET_COLOR = CYAN
BULLET_GLOW = (0, 180, 255)
SHOOT_COOLDOWN = 220       # 毫秒，射击间隔

# ── 敌机 ──
ENEMY_SPAWN_INITIAL = 1800   # 初始生成间隔（毫秒）
ENEMY_SPAWN_MIN = 400        # 最快生成间隔
ENEMY_SPEED_MIN = 2
ENEMY_SPEED_MAX = 5
ENEMY_SIZE_SMALL = 18
ENEMY_SIZE_LARGE = 28
ENEMY_COLOR_SMALL = (255, 80, 80)     # 红色小飞机
ENEMY_COLOR_LARGE = (255, 160, 40)    # 橙色大飞机

# ── 道具 ──
POWERUP_DROP_CHANCE = 0.28     # 击毁敌机掉落概率
POWERUP_SPEED = 3
POWERUP_SIZE = 28
POWERUP_DURATION = 5000        # 限时道具持续毫秒（5秒）
# 道具配色
POWERUP_COLORS = {
    "triple":  (60, 255, 120),     # 绿 — 三连射
    "rapid":   (255, 220, 40),     # 黄 — 快速射击
    "shield":  (60, 140, 255),     # 蓝 — 护盾
    "life":    (255, 80, 200),     # 粉 — 加命
}

# ── BOSS ──
BOSS_SPAWN_SCORE = 8000       # 每超过此分数倍数刷BOSS
BOSS_HP_BASE = 50             # Boss 基础血量（随出场次数递增）
BOSS_HP_INCREMENT = 15        # 每次 Boss 血量增加
BOSS_SIZE = 46
BOSS_SPEED = 1.8
BOSS_SCORE = 1000

# ── 星空 ──
STAR_LAYERS = 3            # 视差层数
STAR_COUNT_PER_LAYER = [40, 25, 15]
STAR_SPEED = [1, 2, 4]    # 像素/帧，越远越慢
STAR_COLORS = [GRAY, LIGHT_GRAY, WHITE]
STAR_SIZES = [1, 1.5, 2]

# ── 精灵缩放 ──
PLAYER_SPRITE_SCALE = 0.55       # 玩家 102x126 → ~56x69
ENEMY1_SCALE = 1.0               # 小敌机 57x43 原尺寸
ENEMY2_SCALE = 0.7               # 波形敌机 69x99 → ~48x69
BOSS_SPRITE_SCALE = 0.65         # Boss 169x258 → ~110x168

# ── 新道具 ──
PIERCING_DURATION = 5000         # 穿透弹持续毫秒
BOMB_FLASH_MS = 180              # 炸弹闪白时间
BOMB_MAX = 3                     # 炸弹最多持有数

# 道具掉落权重（百分比）
POWERUP_WEIGHTS = [
    ("triple",    22),
    ("rapid",     22),
    ("shield",    18),
    ("life",      12),
    ("bomb",      12),
    ("piercing",  14),
]
