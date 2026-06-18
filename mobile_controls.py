"""
mobile_controls.py — 移动端触摸虚拟控件
打飞机 Space Shooter · Web/Mobile
"""
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class MobileControls:
    """移动端虚拟摇杆 + 按钮 — 半透明叠加层"""

    def __init__(self):
        # ── 虚拟摇杆（左下角）──
        self.joystick_base_center = (90, SCREEN_HEIGHT - 130)
        self.joystick_radius = 52
        self.joystick_knob_center = list(self.joystick_base_center)
        self.joystick_knob_radius = 24
        self.joystick_active = False
        self.joystick_touch_id = None

        # ── 炸弹按钮（右下角）──
        self.bomb_center = (SCREEN_WIDTH - 80, SCREEN_HEIGHT - 130)
        self.bomb_radius = 38
        self.bomb_pressed = False
        self.bomb_touch_id = None

        # ── 暂停按钮（右上角）──
        self.pause_rect = pygame.Rect(SCREEN_WIDTH - 55, 42, 46, 40)
        self.pause_pressed = False
        self.pause_touch_id = None

        # ── 输出状态 ──
        self.move_left = False
        self.move_right = False
        self.move_up = False
        self.move_down = False
        self.bomb_triggered = False   # 单帧脉冲
        self.pause_triggered = False  # 单帧脉冲

        # 死区（避免轻微触碰就移动）
        self.dead_zone = 12

    # ═══════════════════════════════════════════════════
    def handle_finger_event(self, event: pygame.event.Event):
        """处理 FINGERDOWN / FINGERUP / FINGERMOTION 事件"""
        # pygbag 中 finger 坐标是归一化的 (0~1)，转为屏幕坐标
        fx = event.x * SCREEN_WIDTH
        fy = event.y * SCREEN_HEIGHT

        if event.type == pygame.FINGERDOWN:
            self._on_touch_down(fx, fy, event.finger_id)

        elif event.type == pygame.FINGERUP:
            self._on_touch_up(event.finger_id)

        elif event.type == pygame.FINGERMOTION:
            self._on_touch_move(fx, fy, event.finger_id)

    # ═══════════════════════════════════════════════════
    def _on_touch_down(self, x: float, y: float, finger_id: int):
        # 摇杆区域
        bx, by = self.joystick_base_center
        if ((x - bx) ** 2 + (y - by) ** 2) < (self.joystick_radius + 20) ** 2:
            if self.joystick_touch_id is None:
                self.joystick_touch_id = finger_id
                self.joystick_active = True
                self.joystick_knob_center = [x, y]
                self._update_joystick_output(x, y)
                return

        # 炸弹按钮
        bx2, by2 = self.bomb_center
        if ((x - bx2) ** 2 + (y - by2) ** 2) < (self.bomb_radius + 10) ** 2:
            if self.bomb_touch_id is None:
                self.bomb_touch_id = finger_id
                self.bomb_pressed = True
                self.bomb_triggered = True
                return

        # 暂停按钮
        if self.pause_rect.collidepoint(x, y):
            if self.pause_touch_id is None:
                self.pause_touch_id = finger_id
                self.pause_pressed = True
                self.pause_triggered = True
                return

    # ═══════════════════════════════════════════════════
    def _on_touch_up(self, finger_id: int):
        if finger_id == self.joystick_touch_id:
            self.joystick_touch_id = None
            self.joystick_active = False
            self.joystick_knob_center = list(self.joystick_base_center)
            self.move_left = self.move_right = self.move_up = self.move_down = False

        if finger_id == self.bomb_touch_id:
            self.bomb_touch_id = None
            self.bomb_pressed = False

        if finger_id == self.pause_touch_id:
            self.pause_touch_id = None
            self.pause_pressed = False

    # ═══════════════════════════════════════════════════
    def _on_touch_move(self, x: float, y: float, finger_id: int):
        if finger_id == self.joystick_touch_id:
            bx, by = self.joystick_base_center
            dx = x - bx
            dy = y - by
            dist = (dx ** 2 + dy ** 2) ** 0.5
            max_dist = self.joystick_radius - self.joystick_knob_radius

            if dist > max_dist:
                dx = dx / dist * max_dist
                dy = dy / dist * max_dist

            self.joystick_knob_center = [bx + dx, by + dy]
            self._update_joystick_output(x, y)

    # ═══════════════════════════════════════════════════
    def _update_joystick_output(self, x: float, y: float):
        """根据摇杆位置更新方向输出"""
        bx, by = self.joystick_base_center
        dx = x - bx
        dy = y - by

        self.move_left = dx < -self.dead_zone
        self.move_right = dx > self.dead_zone
        self.move_up = dy < -self.dead_zone
        self.move_down = dy > self.dead_zone

    # ═══════════════════════════════════════════════════
    def reset_triggers(self):
        """每帧末调用，复位单帧脉冲信号"""
        self.bomb_triggered = False
        self.pause_triggered = False

    # ═══════════════════════════════════════════════════
    def draw(self, surface: pygame.Surface):
        """绘制虚拟控件（半透明）"""
        # ── 摇杆底座 ──
        base_alpha = 80
        base_surf = pygame.Surface((self.joystick_radius * 2, self.joystick_radius * 2),
                                    pygame.SRCALPHA)
        pygame.draw.circle(base_surf, (180, 190, 210, base_alpha),
                           (self.joystick_radius, self.joystick_radius),
                           self.joystick_radius)
        pygame.draw.circle(base_surf, (140, 150, 180, base_alpha),
                           (self.joystick_radius, self.joystick_radius),
                           self.joystick_radius, 2)
        bx, by = self.joystick_base_center
        surface.blit(base_surf,
                     (bx - self.joystick_radius, by - self.joystick_radius))

        # ── 摇杆旋钮 ──
        knob_alpha = 140
        knob_surf = pygame.Surface((self.joystick_knob_radius * 2,
                                     self.joystick_knob_radius * 2),
                                    pygame.SRCALPHA)
        pygame.draw.circle(knob_surf, (200, 220, 255, knob_alpha),
                           (self.joystick_knob_radius, self.joystick_knob_radius),
                           self.joystick_knob_radius)
        kx, ky = self.joystick_knob_center
        surface.blit(knob_surf,
                     (kx - self.joystick_knob_radius,
                      ky - self.joystick_knob_radius))

        # ── 炸弹按钮 ──
        b_alpha = 180 if self.bomb_pressed else 100
        b_color = (255, 120, 40, b_alpha)
        b_surf = pygame.Surface((self.bomb_radius * 2, self.bomb_radius * 2),
                                 pygame.SRCALPHA)
        pygame.draw.circle(b_surf, b_color,
                           (self.bomb_radius, self.bomb_radius),
                           self.bomb_radius)
        pygame.draw.circle(b_surf, (255, 200, 100, b_alpha),
                           (self.bomb_radius, self.bomb_radius),
                           self.bomb_radius, 2)
        # 炸弹图标：B 字母简写
        font = pygame.font.Font(None, 32)
        label = font.render("B", True, (255, 255, 255, 200))
        b_surf.blit(label, label.get_rect(center=(self.bomb_radius, self.bomb_radius - 2)))
        bx2, by2 = self.bomb_center
        surface.blit(b_surf,
                     (bx2 - self.bomb_radius, by2 - self.bomb_radius))

        # ── 暂停按钮 ──
        p_alpha = 140 if self.pause_pressed else 80
        p_surf = pygame.Surface((self.pause_rect.width, self.pause_rect.height),
                                 pygame.SRCALPHA)
        p_color = (180, 190, 210, p_alpha)
        p_surf.fill(p_color)
        pygame.draw.rect(p_surf, (140, 150, 180, p_alpha),
                         (0, 0, self.pause_rect.width, self.pause_rect.height), 2)
        # 双竖线（暂停图标）
        bar_w = 5
        bar_h = 18
        bar_gap = 8
        bar_y = (self.pause_rect.height - bar_h) // 2
        for bx_off in [-bar_gap // 2, bar_gap // 2]:
            bx_bar = self.pause_rect.width // 2 + bx_off - bar_w // 2
            pygame.draw.rect(p_surf, (220, 230, 255, 160),
                             (bx_bar, bar_y, bar_w, bar_h))
        surface.blit(p_surf, (self.pause_rect.x, self.pause_rect.y))
