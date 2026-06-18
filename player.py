"""
player.py — 玩家飞船
打飞机 Space Shooter
"""
import os
import pygame
from settings import (SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SPEED, PLAYER_SIZE,
                      SHOOT_COOLDOWN, BULLET_SPEED, POWERUP_DURATION,
                      PIERCING_DURATION, BOMB_MAX, ASSETS_DIR, PLAYER_SPRITE_SCALE)
from bullet import Bullet


def _load_img(filename: str, scale: float = 1.0):
    """加载素材图片并按比例缩放"""
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


class Player:
    """玩家飞船 — 精灵图渲染 + 武器/道具系统"""

    def __init__(self):
        # ── 精灵贴图 ──
        self._sprite1 = _load_img("me1.png", PLAYER_SPRITE_SCALE)
        self._sprite2 = _load_img("me2.png", PLAYER_SPRITE_SCALE)
        self._destroy_frames = [
            _load_img(f"me_destroy_{i}.png", PLAYER_SPRITE_SCALE)
            for i in range(1, 5)
        ]
        self._current_sprite = self._sprite1 or pygame.Surface((30, 36))
        self._anim_timer = 0

        if self._sprite1:
            sw, sh = self._sprite1.get_size()
        else:
            sw, sh = 30, 36

        # 初始位置：屏幕底部中央
        self.x = SCREEN_WIDTH / 2
        self.y = SCREEN_HEIGHT - 100
        self.speed = PLAYER_SPEED
        self.radius = sw * 0.35  # 碰撞圆半径

        # 控制标记
        self.move_left = False
        self.move_right = False
        self.move_up = False
        self.move_down = False

        # 射击冷却
        self._last_shot_time = 0  # pygame ticks

        # ── 武器 / 道具状态（独立共存，互不覆盖）──
        self.has_triple = False
        self.triple_timer = 0
        self.has_rapid = False
        self.rapid_timer = 0
        self.has_piercing = False      # 穿透弹
        self.piercing_timer = 0
        self.bombs = 0                 # 清屏炸弹数量
        self.shield_active = False

        # 死亡动画状态
        self._dying = False
        self._death_frame = 0
        self._death_timer = 0
        self._use_bomb = False         # 本帧使用炸弹的信号

    # ── 向后兼容属性 ──
    @property
    def weapon_type(self) -> str:
        parts = []
        if self.has_triple:   parts.append("triple")
        if self.has_rapid:    parts.append("rapid")
        if self.has_piercing: parts.append("piercing")
        return "+".join(parts) if parts else "normal"

    @property
    def weapon_timer(self) -> int:
        return max(self.triple_timer, self.rapid_timer, self.piercing_timer)

    # ═══════════════════════════════════════════
    def handle_event(self, event: pygame.event.Event):
        """处理键盘输入"""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.move_left = True
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.move_right = True
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.move_up = True
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.move_down = True
            elif event.key == pygame.K_b:
                if self.bombs > 0:
                    self._use_bomb = True

        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.move_left = False
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.move_right = False
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.move_up = False
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.move_down = False

    # ═══════════════════════════════════════════
    def shoot(self) -> list:
        """返回子弹列表（空列表 = 冷却中）
        三连射 & 速射可叠加：快速三连射 = 半冷却 + 3 发子弹
        穿透弹：子弹不因碰撞而销毁"""
        if self._dying:
            return []

        now = pygame.time.get_ticks()
        cooldown = SHOOT_COOLDOWN // 2 if self.has_rapid else SHOOT_COOLDOWN
        if now - self._last_shot_time < cooldown:
            return []

        self._last_shot_time = now
        bullets = []
        nose_y = self.y - self._current_sprite.get_height() / 2

        if self.has_triple:
            bullets.append(Bullet(self.x, nose_y, BULLET_SPEED, self.has_piercing))
            bullets.append(Bullet(self.x - 8, nose_y + 4, BULLET_SPEED, self.has_piercing))
            bullets.append(Bullet(self.x + 8, nose_y + 4, BULLET_SPEED, self.has_piercing))
        else:
            bullets.append(Bullet(self.x, nose_y, BULLET_SPEED, self.has_piercing))

        return bullets

    # ═══════════════════════════════════════════
    def apply_powerup(self, pu_type: str):
        """应用道具效果 — 不同增益独立共存，互不覆盖"""
        if pu_type == "triple":
            self.has_triple = True
            self.triple_timer = POWERUP_DURATION
        elif pu_type == "rapid":
            self.has_rapid = True
            self.rapid_timer = POWERUP_DURATION
        elif pu_type == "piercing":
            self.has_piercing = True
            self.piercing_timer = PIERCING_DURATION
        elif pu_type == "bomb":
            self.bombs = min(self.bombs + 1, BOMB_MAX)
        elif pu_type == "shield":
            self.shield_active = True
        elif pu_type == "life":
            return  # main.py 处理加命

    # ═══════════════════════════════════════════
    def consume_bomb(self) -> bool:
        """消耗一枚炸弹，返回 True 表示成功使用"""
        if self.bombs > 0:
            self.bombs -= 1
            return True
        return False

    @property
    def bomb_requested(self) -> bool:
        """本帧是否按下了炸弹键（由 main 读取后复位）"""
        return self._use_bomb

    def clear_bomb_request(self):
        self._use_bomb = False

    # ═══════════════════════════════════════════
    def start_death(self):
        """开始死亡动画"""
        if not self._dying:
            self._dying = True
            self._death_frame = 0
            self._death_timer = 0

    @property
    def death_finished(self) -> bool:
        """死亡动画是否播放完毕"""
        return self._dying and self._death_frame >= len(self._destroy_frames)

    # ═══════════════════════════════════════════
    def update(self, dt_ms: int = 0):
        """更新位置 + 动画 + 计时器"""
        # ── 死亡动画 ──
        if self._dying:
            self._death_timer += dt_ms
            if self._death_timer >= 100:  # 每 100ms 一帧
                self._death_timer = 0
                self._death_frame += 1
            return

        # ── 引擎动画（me1 / me2 交替闪烁）──
        if self._sprite1 and self._sprite2:
            self._anim_timer += dt_ms
            if self._anim_timer >= 300:
                self._anim_timer = 0
                self._current_sprite = (self._sprite2 if self._current_sprite is self._sprite1
                                        else self._sprite1)

        # ── 武器计时器（独立倒计时）──
        if self.triple_timer > 0:
            self.triple_timer -= dt_ms
            if self.triple_timer <= 0:
                self.has_triple = False
                self.triple_timer = 0
        if self.rapid_timer > 0:
            self.rapid_timer -= dt_ms
            if self.rapid_timer <= 0:
                self.has_rapid = False
                self.rapid_timer = 0
        if self.piercing_timer > 0:
            self.piercing_timer -= dt_ms
            if self.piercing_timer <= 0:
                self.has_piercing = False
                self.piercing_timer = 0

        # ── 移动 ──
        dx = dy = 0
        if self.move_left:
            dx = -self.speed
        if self.move_right:
            dx = self.speed
        if self.move_up:
            dy = -self.speed
        if self.move_down:
            dy = self.speed

        # 对角线归一化，防止斜移过快
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        self.x += dx
        self.y += dy

        # 边界限制
        margin = self.radius
        self.x = max(margin, min(SCREEN_WIDTH - margin, self.x))
        self.y = max(margin, min(SCREEN_HEIGHT - margin, self.y))

    # ═══════════════════════════════════════════
    def draw(self, surface: pygame.Surface):
        """绘制飞船 —— 精灵图 + 护盾光环 + 死亡动画"""
        if self._dying:
            frames = [f for f in self._destroy_frames if f is not None]
            if self._death_frame < len(frames):
                frame = frames[self._death_frame]
                rect = frame.get_rect(center=(int(self.x), int(self.y)))
                surface.blit(frame, rect)
            return

        # 飞船精灵
        if self._current_sprite:
            rect = self._current_sprite.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(self._current_sprite, rect)

        # ── 护盾光环 ──
        if self.shield_active:
            r = self.radius + 10
            tick = pygame.time.get_ticks()
            alpha = 60 + int(40 * abs((tick % 600) / 300 - 1))  # 脉冲
            pygame.draw.circle(surface, (60, 180, 255, alpha),
                               (int(self.x), int(self.y)), int(r), 2)
            pygame.draw.circle(surface, (100, 220, 255, alpha // 2),
                               (int(self.x), int(self.y)), int(r + 4), 1)

    # ═══════════════════════════════════════════
    @property
    def rect(self) -> pygame.Rect:
        """碰撞检测用的矩形"""
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2,
        )
