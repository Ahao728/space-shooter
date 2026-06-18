"""
bullet.py — 子弹精灵
打飞机 Space Shooter
"""
import os
import pygame
from settings import SCREEN_HEIGHT, BULLET_SIZE, BULLET_COLOR, BULLET_GLOW, ASSETS_DIR


def _load_bullet_img(filename: str):
    """加载子弹贴图"""
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

# 预加载子弹贴图
_BULLET1_IMG = _load_bullet_img("bullet1.png")   # 5x11 普通弹
_BULLET2_IMG = _load_bullet_img("bullet2.png")   # 5x11 穿透弹


class Bullet(pygame.sprite.Sprite):
    """玩家子弹 — 支持穿透属性"""

    def __init__(self, x: float, y: float, speed: float, piercing: bool = False):
        super().__init__()
        self.speed = speed
        self.piercing = piercing

        img = (_BULLET2_IMG if piercing else _BULLET1_IMG)
        if img is not None:
            self.image = img.copy()
            if piercing:
                # 穿透弹加金色光晕
                overlay = pygame.Surface(img.get_size(), pygame.SRCALPHA)
                overlay.fill((255, 200, 40, 100))
                self.image.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        else:
            # 兜底：程序绘制
            w, h = BULLET_SIZE
            self.image = pygame.Surface((w, h), pygame.SRCALPHA)
            cx, cy = w / 2, h / 2
            color = (255, 200, 40) if piercing else BULLET_COLOR
            pygame.draw.ellipse(self.image, (0, 80, 200, 60),
                                (cx - w * 0.6, cy - h * 0.7, w * 1.2, h * 1.4))
            pygame.draw.ellipse(self.image, color,
                                (cx - w * 0.3, cy - h * 0.3, w * 0.6, h * 0.6))

        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        """向上移动，超出屏幕则标记删除"""
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()
