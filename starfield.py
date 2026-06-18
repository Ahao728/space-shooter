"""
starfield.py — 多层视差滚动星空背景
打飞机 Space Shooter
"""
import random
import pygame
from settings import (STAR_LAYERS, STAR_COUNT_PER_LAYER, STAR_SPEED,
                      STAR_COLORS, STAR_SIZES, SCREEN_WIDTH, SCREEN_HEIGHT)


class Star:
    """单颗星星"""
    def __init__(self, layer: int):
        self.layer = layer
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = random.uniform(0, SCREEN_HEIGHT)
        self.speed = STAR_SPEED[layer]
        self.color = STAR_COLORS[layer]
        self.size = STAR_SIZES[layer]
        # 随机亮度变化
        self.brightness = random.uniform(0.4, 1.0)

    def update(self):
        """向下滚动，到底后回到顶部"""
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.uniform(0, SCREEN_WIDTH)

    def draw(self, surface: pygame.Surface):
        c = self.color
        color = (int(c[0] * self.brightness),
                 int(c[1] * self.brightness),
                 int(c[2] * self.brightness))
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)


class Starfield:
    """多层星空管理器"""
    def __init__(self):
        self.stars = []
        for layer in range(STAR_LAYERS):
            for _ in range(STAR_COUNT_PER_LAYER[layer]):
                self.stars.append(Star(layer))

    def update(self):
        for star in self.stars:
            star.update()

    def draw(self, surface: pygame.Surface):
        for star in self.stars:
            star.draw(surface)
