"""
explosion.py — 粒子爆炸特效 + 精灵帧死亡动画
打飞机 Space Shooter
"""
import os
import random
import math
import pygame
from settings import ASSETS_DIR


# ═══════════════════════════════════════════════════════════
#  精灵帧预加载
# ═══════════════════════════════════════════════════════════

def _load_frame(filename: str):
    path = os.path.join(ASSETS_DIR, filename)
    try:
        img = pygame.image.load(path)
        try:
            img = img.convert_alpha()
        except pygame.error:
            pass
        return img
    except Exception:
        return None


# 小敌机死亡帧 (enemy1_down1~4)
_ENEMY1_DOWN = [_load_frame(f"enemy1_down{i}.png") for i in range(1, 5)]
_ENEMY1_DOWN = [f for f in _ENEMY1_DOWN if f is not None]

# 中敌机死亡帧 (enemy2_down1~4)
_ENEMY2_DOWN = [_load_frame(f"enemy2_down{i}.png") for i in range(1, 5)]
_ENEMY2_DOWN = [f for f in _ENEMY2_DOWN if f is not None]

# Boss 死亡帧 (enemy3_down1~6)
_ENEMY3_DOWN = [_load_frame(f"enemy3_down{i}.png") for i in range(1, 7)]
_ENEMY3_DOWN = [f for f in _ENEMY3_DOWN if f is not None]

# 敌机受击贴图
_ENEMY2_HIT = _load_frame("enemy2_hit.png")
_ENEMY3_HIT = _load_frame("enemy3_hit.png")

# 玩家死亡帧 (me_destroy1~4)
_ME_DESTROY = [_load_frame(f"me_destroy_{i}.png") for i in range(1, 5)]
_ME_DESTROY = [f for f in _ME_DESTROY if f is not None]


def get_death_frames(enemy_type: str) -> list:
    """根据敌机类型返回死亡动画帧列表"""
    if enemy_type == "small":
        return _ENEMY1_DOWN
    elif enemy_type == "large":
        return _ENEMY2_DOWN
    elif enemy_type == "boss":
        return _ENEMY3_DOWN
    elif enemy_type == "player":
        return _ME_DESTROY
    return []


def get_hit_image(enemy_type: str):
    """返回敌机受击贴图"""
    if enemy_type == "large":
        return _ENEMY2_HIT
    elif enemy_type == "boss":
        return _ENEMY3_HIT
    return None


# ═══════════════════════════════════════════════════════════
#  粒子爆炸（保留作为补充特效）
# ═══════════════════════════════════════════════════════════

PARTICLE_COUNT = 18
PARTICLE_SPEED = (2, 7)
PARTICLE_LIFE = (15, 35)
PARTICLE_SIZE = (1.5, 4)

FIRE_COLORS = [
    (255, 80, 20), (255, 160, 30), (255, 220, 40), (255, 255, 180),
]
HIT_COLORS = [
    (100, 180, 255), (180, 220, 255), (255, 255, 255),
]


class Explosion:
    """粒子爆炸"""

    def __init__(self, x: float, y: float, color_palette: list = None):
        if color_palette is None:
            color_palette = FIRE_COLORS

        self.particles = []
        for _ in range(PARTICLE_COUNT):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(*PARTICLE_SPEED)
            self.particles.append({
                'x': x + random.uniform(-5, 5),
                'y': y + random.uniform(-5, 5),
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - random.uniform(0, 2),
                'life': random.randint(*PARTICLE_LIFE),
                'max_life': 0,
                'size': random.uniform(*PARTICLE_SIZE),
                'color': random.choice(color_palette),
            })
            self.particles[-1]['max_life'] = self.particles[-1]['life']
        self.alive = True

    def update(self):
        self.alive = False
        for p in self.particles:
            if p['life'] <= 0:
                continue
            self.alive = True
            p['life'] -= 1
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.1
            p['vx'] *= 0.98

    def draw(self, surface: pygame.Surface):
        for p in self.particles:
            if p['life'] <= 0:
                continue
            t = p['life'] / p['max_life']
            size = max(0.5, p['size'] * t)
            c = p['color']
            color = (int(c[0] * t), int(c[1] * t * 0.8), int(c[2] * t * 0.6))
            pygame.draw.circle(surface, (color[0] // 2, color[1] // 2, color[2] // 2),
                               (int(p['x']), int(p['y'])), size * 1.8, 1)
            pygame.draw.circle(surface, color, (int(p['x']), int(p['y'])), size)


# ═══════════════════════════════════════════════════════════
#  精灵帧死亡动画
# ═══════════════════════════════════════════════════════════

class SpriteExplosion:
    """精灵帧序列动画 — 用于敌机 / Boss / 玩家死亡"""

    def __init__(self, x: float, y: float, frames: list, frame_ms: int = 80):
        self.x = x
        self.y = y
        self.frames = frames
        self.frame_ms = frame_ms
        self._timer = 0
        self._index = 0
        self.alive = bool(frames)

    def update(self, dt_ms: int = 16):
        if not self.alive:
            return
        self._timer += dt_ms
        if self._timer >= self.frame_ms:
            self._timer = 0
            self._index += 1
            if self._index >= len(self.frames):
                self.alive = False

    def draw(self, surface: pygame.Surface):
        if self.alive and self._index < len(self.frames):
            frame = self.frames[self._index]
            if frame is not None:
                rect = frame.get_rect(center=(int(self.x), int(self.y)))
                surface.blit(frame, rect)


# ═══════════════════════════════════════════════════════════
#  快捷工厂
# ═══════════════════════════════════════════════════════════

def spawn_explosion(explosions: list, x: float, y: float,
                    enemy_type: str = "small", color_palette: list = None):
    """生成粒子爆炸（保留作为辅助特效）"""
    if color_palette is not None:
        e = Explosion(x, y, color_palette)
    elif enemy_type == "large":
        e = Explosion(x, y, random.choice([FIRE_COLORS, HIT_COLORS]))
        extra = len(e.particles)
        e.particles.extend([dict(p) for p in e.particles[:extra // 2]])
    else:
        e = Explosion(x, y, FIRE_COLORS)
    explosions.append(e)


def spawn_sprite_death(sprite_explosions: list, x: float, y: float,
                       enemy_type: str = "small"):
    """生成精灵帧死亡动画"""
    frames = get_death_frames(enemy_type)
    if frames:
        ms = 100 if enemy_type == "boss" else 80
        sprite_explosions.append(SpriteExplosion(x, y, frames, ms))
