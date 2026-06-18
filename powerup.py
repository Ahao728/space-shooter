"""
powerup.py — 道具精灵
打飞机 Space Shooter
"""
import os
import random
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    POWERUP_SPEED, POWERUP_SIZE, POWERUP_COLORS, POWERUP_DURATION,
    PIERCING_DURATION, POWERUP_WEIGHTS, ASSETS_DIR,
)


def _load_pu_img(filename: str):
    """加载道具贴图"""
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


# 预加载道具贴图
_PU_IMAGES = {
    "life":    _load_pu_img("life.png"),           # 46x57
    "bomb":    _load_pu_img("bomb_supply.png"),     # 60x107
    "piercing": _load_pu_img("bullet_supply.png"),  # 58x88
}
# 图片缩放到的统一尺寸
_PU_IMG_SIZE = 42


def _random_pu_type() -> str:
    """加权随机选取道具类型"""
    types, weights = zip(*POWERUP_WEIGHTS)
    return random.choices(types, weights=weights)[0]


class PowerUp(pygame.sprite.Sprite):
    """道具 — 被拾取后给玩家加成"""

    def __init__(self, x: float, y: float, pu_type: str = None):
        super().__init__()
        self.pu_type = pu_type or _random_pu_type()

        # 持续时间：一次性道具 = 0
        if self.pu_type in ("life", "bomb"):
            self.duration = 0
        elif self.pu_type == "piercing":
            self.duration = PIERCING_DURATION
        else:
            self.duration = POWERUP_DURATION

        self.color = POWERUP_COLORS.get(self.pu_type, (255, 255, 255))

        # ── 尝试使用贴图 ──
        img = _PU_IMAGES.get(self.pu_type)
        if img is not None:
            w, h = img.get_size()
            scale = _PU_IMG_SIZE / max(w, h)
            self.image = pygame.transform.scale(
                img, (int(w * scale), int(h * scale)))
        else:
            self.image = self._draw_icon()

        self.rect = self.image.get_rect(center=(x, y))
        self._spawn_time = pygame.time.get_ticks()

    def _draw_icon(self) -> pygame.Surface:
        """程序绘制道具图标（兜底）"""
        size = POWERUP_SIZE
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx = cy = size / 2
        r = size * 0.45

        if self.pu_type == "triple":
            for dx, dy in [(-3, 0), (3, -4), (3, 4)]:
                pygame.draw.circle(surf, self.color, (int(cx + dx), int(cy + dy)), 3)
            pygame.draw.circle(surf, (255, 255, 255), (int(cx), int(cy)), 2)

        elif self.pu_type == "rapid":
            pts = [(cx, cy - r), (cx, cy - 2), (cx - 4, cy + 2),
                   (cx, cy + 1), (cx + 2, cy + r)]
            pygame.draw.lines(surf, self.color, False, pts, 2)

        elif self.pu_type == "shield":
            pygame.draw.circle(surf, self.color, (int(cx), int(cy)), int(r), 3)
            pygame.draw.circle(surf, (255, 255, 255), (int(cx), int(cy)), int(r * 0.3))

        elif self.pu_type == "life":
            off = r * 0.3
            pygame.draw.rect(surf, self.color,
                             (cx - off, cy - r * 0.7, off * 2, r * 1.4))
            pygame.draw.rect(surf, self.color,
                             (cx - r * 0.7, cy - off, r * 1.4, off * 2))

        elif self.pu_type == "bomb":
            # 炸弹图标：圆 + 引信
            pygame.draw.circle(surf, (255, 160, 30), (int(cx), int(cy)), int(r * 0.7))
            pygame.draw.circle(surf, (255, 220, 80), (int(cx - 1), int(cy - 1)), int(r * 0.4))
            pygame.draw.line(surf, (255, 100, 30), (int(cx + r * 0.5), int(cy - r * 0.5)),
                             (int(cx + r * 0.8), int(cy - r * 0.9)), 2)
            # 火花
            pygame.draw.circle(surf, (255, 255, 100), (int(cx + r * 0.8), int(cy - r * 0.9)), 2)

        elif self.pu_type == "piercing":
            # 穿透图标：箭头穿过方块
            pygame.draw.rect(surf, (100, 200, 255),
                             (cx - r * 0.3, cy - r * 0.5, r * 0.6, r), 1)
            color = (255, 200, 40)
            pygame.draw.polygon(surf, color,
                                [(cx - r * 0.7, cy - r * 0.1),
                                 (cx + r * 0.6, cy - r * 0.5),
                                 (cx + r * 0.6, cy + r * 0.3)])

        # 光晕外框
        pygame.draw.circle(surf, (255, 255, 255, 60), (int(cx), int(cy)), int(r + 2), 1)
        return surf

    def update(self):
        """向下掉落，超出屏幕删除"""
        self.rect.y += POWERUP_SPEED
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    @staticmethod
    def maybe_spawn(x: float, y: float, powerups_group: pygame.sprite.Group,
                    drop_chance: float = 0.28):
        """工厂方法：按概率生成道具"""
        if random.random() < drop_chance:
            powerups_group.add(PowerUp(x, y))
