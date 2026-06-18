"""
enemy.py — 敌机精灵 + 生成器
打飞机 Space Shooter
"""
import os
import random
import math
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    ENEMY_SPAWN_INITIAL, ENEMY_SPAWN_MIN,
    ENEMY_SPEED_MIN, ENEMY_SPEED_MAX,
    ENEMY_SIZE_SMALL, ENEMY_SIZE_LARGE,
    BOSS_SPAWN_SCORE, BOSS_HP_BASE, BOSS_HP_INCREMENT, BOSS_SIZE, BOSS_SPEED, BOSS_SCORE,
    ENEMY1_SCALE, ENEMY2_SCALE, BOSS_SPRITE_SCALE, ASSETS_DIR,
)
from explosion import get_hit_image


def _load_enemy_img(filename: str, scale: float = 1.0):
    """加载敌机贴图"""
    path = os.path.join(ASSETS_DIR, filename)
    try:
        img = pygame.image.load(path)
        try:
            img = img.convert_alpha()
        except pygame.error:
            pass
        if scale != 1.0:
            w, h = img.get_size()
            img = pygame.transform.scale(img, (int(w * scale), int(h * scale)))
        return img
    except Exception:
        return None


# 预加载敌机贴图
_ENEMY1_IMG = _load_enemy_img("enemy1.png", ENEMY1_SCALE)        # 57x43 小敌机
_ENEMY2_IMG = _load_enemy_img("enemy2.png", ENEMY2_SCALE)        # 69x99 波形敌机
_BOSS_IMG1 = _load_enemy_img("enemy3_n1.png", BOSS_SPRITE_SCALE) # 169x258 Boss
_BOSS_IMG2 = _load_enemy_img("enemy3_n2.png", BOSS_SPRITE_SCALE) # Boss 2


class Enemy(pygame.sprite.Sprite):
    """敌机基类 — 定义通用接口 + 受击闪烁"""

    HIT_FLASH_MS = 80  # 受击闪烁持续时间

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.speed_y = ENEMY_SPEED_MIN
        self.hp = 1
        self.score = 100
        self._normal_image = None   # 原始贴图
        self._hit_image = None      # 受击贴图
        self._hit_timer = 0         # 闪烁倒计时

    def flash_hit(self):
        """触发受击闪烁"""
        if self._normal_image and self._hit_image:
            self._hit_timer = Enemy.HIT_FLASH_MS
            self.image = self._hit_image

    def _restore_image(self):
        """恢复原始贴图"""
        if self._normal_image:
            self.image = self._normal_image

    def update(self):
        """子类覆盖具体移动逻辑"""
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
        # 受击闪烁恢复
        if self._hit_timer > 0:
            self._hit_timer -= 16  # 近似每帧 16ms
            if self._hit_timer <= 0:
                self._restore_image()


class StraightEnemy(Enemy):
    """直线敌机 — 使用 enemy1.png 精灵"""

    def __init__(self):
        super().__init__()
        size = ENEMY_SIZE_SMALL
        self.speed_y = random.uniform(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
        self.score = 100
        self.hp = 1

        if _ENEMY1_IMG is not None:
            self.image = _ENEMY1_IMG.copy()
            self._sprite = _ENEMY1_IMG
        else:
            # 兜底：程序绘制倒三角
            self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            cx, cy = size, size
            tip = (cx, cy + size * 0.8)
            left = (cx - size * 0.6, cy - size * 0.5)
            right = (cx + size * 0.6, cy - size * 0.5)
            pygame.draw.polygon(self.image, (255, 80, 80), [tip, left, right])
            pygame.draw.polygon(self.image, (220, 40, 40), [tip, left, right], 2)
            pygame.draw.circle(self.image, (255, 200, 200), (cx, cy - size * 0.1), 3)

        self.rect = self.image.get_rect(
            center=(random.randint(size + 10, SCREEN_WIDTH - size - 10), -size)
        )


class SineEnemy(Enemy):
    """波形敌机 — 使用 enemy2.png 精灵，正弦波移动"""

    def __init__(self):
        super().__init__()
        size = ENEMY_SIZE_LARGE
        self.speed_y = random.uniform(ENEMY_SPEED_MIN * 0.7, ENEMY_SPEED_MAX * 0.8)
        self.score = 200
        self.hp = 2

        self.start_x = random.uniform(size + 20, SCREEN_WIDTH - size - 20)
        self.amplitude = random.uniform(30, 80)
        self.frequency = random.uniform(0.02, 0.05)
        self.phase = random.uniform(0, 2 * math.pi)

        if _ENEMY2_IMG is not None:
            self.image = _ENEMY2_IMG.copy()
            self._normal_image = self.image
            self._hit_image = get_hit_image("large")
            self._sprite = _ENEMY2_IMG
        else:
            # 兜底：六边形
            self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            points = []
            for i in range(6):
                angle = math.pi / 3 * i - math.pi / 2
                px = size + size * 0.7 * math.cos(angle)
                py = size + size * 0.7 * math.sin(angle)
                points.append((px, py))
            pygame.draw.polygon(self.image, (255, 160, 40), points)
            pygame.draw.polygon(self.image, (200, 100, 20), points, 2)
            pygame.draw.circle(self.image, (255, 255, 200), (size, size), 5, 1)
            pygame.draw.circle(self.image, (255, 255, 200), (size, size), 2)

        self.rect = self.image.get_rect(
            center=(self.start_x, -size)
        )

    def update(self):
        """正弦波水平移动 + 下落"""
        super().update()
        self.rect.x = int(self.start_x + self.amplitude * math.sin(
            self.rect.y * self.frequency + self.phase))


class EnemyBullet(pygame.sprite.Sprite):
    """Boss 发射的子弹 — 使用 bullet2.png，向下移动"""

    def __init__(self, x: float, y: float, speed_x: float = 0, speed_y: float = 5):
        super().__init__()
        # 使用 bullet2.png 素材
        img = _load_enemy_img("bullet2.png")
        if img is not None:
            self.image = img
        else:
            self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
            r = 4
            pygame.draw.circle(self.image, (255, 80, 180), (r, r), r)
            pygame.draw.circle(self.image, (255, 200, 240), (r, r), r - 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_x = speed_x
        self.speed_y = speed_y

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT or self.rect.bottom < 0:
            self.kill()


class BossEnemy(Enemy):
    """Boss 敌机 — 使用 enemy3_n1/n2.png 精灵"""

    def __init__(self, boss_count: int = 1):
        super().__init__()
        size = BOSS_SIZE
        self.speed_y = 0.5
        self.speed_x = BOSS_SPEED
        self.hp = BOSS_HP_BASE + (boss_count - 1) * BOSS_HP_INCREMENT
        self.score = BOSS_SCORE + (boss_count - 1) * 500
        self._boss_count = boss_count
        self._shoot_timer = 0
        self._direction = 1
        self._entered = False
        self.pending_bullets = []
        self._anim_timer = 0
        self._use_sprite1 = True

        if _BOSS_IMG1 is not None:
            self._boss_sprite1 = _BOSS_IMG1.copy()
            self._boss_sprite2 = (_BOSS_IMG2.copy() if _BOSS_IMG2 is not None
                                  else _BOSS_IMG1.copy())
            self.image = self._boss_sprite1
            self._normal_image = self._boss_sprite1
            self._hit_image = get_hit_image("boss")
            self._sprite = self._boss_sprite1
        else:
            # 兜底：八角形
            self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            cx = cy = size
            points = []
            for i in range(8):
                ang = math.pi / 4 * i
                r_val = size * 0.8
                px = cx + r_val * math.cos(ang)
                py = cy + r_val * math.sin(ang)
                points.append((px, py))
            shade = max(40, 200 - boss_count * 30)
            boss_color = (shade + 50, 50, shade + 10)
            pygame.draw.polygon(self.image, boss_color, points)
            pygame.draw.polygon(self.image, (255, 60, 180), points, 3)
            pygame.draw.circle(self.image, (255, 200, 50), (cx, cy), size * 0.3)
            pygame.draw.circle(self.image, (255, 255, 200), (cx, cy), size * 0.15)
            for ang in [0, math.pi / 2, math.pi, 3 * math.pi / 2]:
                wx = cx + size * 0.55 * math.cos(ang)
                wy = cy + size * 0.55 * math.sin(ang)
                pygame.draw.circle(self.image, (255, 100, 100), (int(wx), int(wy)), 4)

        # 修正精灵图视觉偏移（素材内飞船偏右 40px，X 轴补正）
        vis_ox = int(40 * BOSS_SPRITE_SCALE)
        self.rect = self.image.get_rect(
            center=(SCREEN_WIDTH / 2 - vis_ox, -size)
        )

    def update(self):
        self.pending_bullets = []

        if not self._entered:
            self.rect.y += 3  # 快速入场（约 1 秒）
            if self.rect.top >= 40:
                self._entered = True
            return

        # Boss 精灵动画（交替两张图）
        if _BOSS_IMG1 is not None and _BOSS_IMG2 is not None:
            self._anim_timer += 1
            if self._anim_timer >= 20:
                self._anim_timer = 0
                self._use_sprite1 = not self._use_sprite1
                self._normal_image = (self._boss_sprite1 if self._use_sprite1
                                      else self._boss_sprite2)
                if self._hit_timer <= 0:
                    old_center = self.rect.center
                    self.image = self._normal_image
                    self.rect = self.image.get_rect(center=old_center)

        # 巡逻
        self.rect.x += self.speed_x * self._direction
        if self.rect.left <= 10:
            self._direction = 1
        elif self.rect.right >= SCREEN_WIDTH - 10:
            self._direction = -1

        # 射击（每 0.7 秒一轮三连发）
        self._shoot_timer += 1
        if self._shoot_timer >= 180:  # 60 帧 = 1 秒
            self._shoot_timer = 0
            self.pending_bullets = self._shoot()

    def _shoot(self) -> list[EnemyBullet]:
        """三发直线弹 — 并排垂直下落"""
        cx = self.rect.centerx
        cy = self.rect.bottom
        bullets = [
            EnemyBullet(cx, cy, speed_x=0, speed_y=5),       # 正中
            EnemyBullet(cx - 12, cy, speed_x=0, speed_y=5),   # 左
            EnemyBullet(cx + 12, cy, speed_x=0, speed_y=5),   # 右
        ]
        return bullets


class EnemySpawner:
    """敌机生成器 — 按时间间隔生成，难度随存活时间递增"""

    def __init__(self):
        self._reset()

    def _reset(self):
        self.spawn_interval = ENEMY_SPAWN_INITIAL
        self._last_spawn = pygame.time.get_ticks()
        self.elapsed_time = 0
        self._last_boss_score = 0
        self._boss_alive = False
        self._boss_count = 0

    def on_boss_killed(self):
        """Boss 被击杀时调用"""
        self._boss_alive = False

    def update(self, dt_ms: int, score: int) -> list[Enemy]:
        """返回本帧新生成的敌机（含 Boss）"""
        self.elapsed_time += dt_ms
        now = pygame.time.get_ticks()

        self.spawn_interval = max(
            ENEMY_SPAWN_MIN,
            ENEMY_SPAWN_INITIAL - (self.elapsed_time // 8000) * 150
        )

        new_enemies = []

        # ── Boss ──
        if not self._boss_alive and score > 0:
            next_boss_at = self._last_boss_score + BOSS_SPAWN_SCORE
            if score >= next_boss_at:
                self._boss_count += 1
                boss = BossEnemy(self._boss_count)
                new_enemies.append(boss)
                self._last_boss_score = next_boss_at
                self._boss_alive = True

        # ── 普通敌机 ──
        if now - self._last_spawn >= self.spawn_interval:
            self._last_spawn = now
            sine_chance = min(0.3, 0.1 + self.elapsed_time / 200000)
            if random.random() < sine_chance:
                new_enemies.append(SineEnemy())
            else:
                count = random.choices([1, 2, 3], weights=[0.55, 0.3, 0.15])[0]
                if self.elapsed_time > 60000:
                    count = random.choices([1, 2, 3], weights=[0.3, 0.4, 0.3])[0]
                for _ in range(count):
                    new_enemies.append(StraightEnemy())

        return new_enemies
