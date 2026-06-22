"""
mobile_controls.py — 移动端触摸滑动控件
打飞机 Space Shooter · Web/Mobile
"""
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class MobileControls:
    """移动端滑屏控制 + 炸弹按钮 — 半透明叠加层

    滑屏：手指在屏幕上任意位置按下并滑动，飞机跟随手指移动。
    松手后飞机停在原位，不会自动回中。
    """

    def __init__(self):
        # ── 滑屏移动控制 ──
        self.swipe_start = None          # 触摸起始点 (x, y)
        self.swipe_current = None        # 当前触摸位置 (x, y)
        self.swipe_touch_id = None
        self.swipe_active = False

        # ── 炸弹按钮（右下角）──
        self.bomb_center = (SCREEN_WIDTH - 80, SCREEN_HEIGHT - 130)
        self.bomb_radius = 38
        self.bomb_pressed = False
        self.bomb_touch_id = None

        # ── 输出状态 ──
        self.bomb_triggered = False   # 单帧脉冲

    # ═══════════════════════════════════════════════════
    @property
    def swipe_dx(self) -> float:
        """当前触摸点相对于起始点的 X 偏移量"""
        if self.swipe_active and self.swipe_start is not None and self.swipe_current is not None:
            return self.swipe_current[0] - self.swipe_start[0]
        return 0.0

    @property
    def swipe_dy(self) -> float:
        """当前触摸点相对于起始点的 Y 偏移量"""
        if self.swipe_active and self.swipe_start is not None and self.swipe_current is not None:
            return self.swipe_current[1] - self.swipe_start[1]
        return 0.0

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
        # 炸弹按钮优先
        bx, by = self.bomb_center
        if ((x - bx) ** 2 + (y - by) ** 2) < (self.bomb_radius + 10) ** 2:
            if self.bomb_touch_id is None:
                self.bomb_touch_id = finger_id
                self.bomb_pressed = True
                self.bomb_triggered = True
                return

        # 滑屏移动（屏幕任意位置，且未被占用）
        if self.swipe_touch_id is None:
            self.swipe_touch_id = finger_id
            self.swipe_active = True
            self.swipe_start = (x, y)
            self.swipe_current = (x, y)

    # ═══════════════════════════════════════════════════
    def _on_touch_up(self, finger_id: int):
        if finger_id == self.bomb_touch_id:
            self.bomb_touch_id = None
            self.bomb_pressed = False

        if finger_id == self.swipe_touch_id:
            self.swipe_touch_id = None
            self.swipe_active = False
            self.swipe_start = None
            self.swipe_current = None

    # ═══════════════════════════════════════════════════
    def _on_touch_move(self, x: float, y: float, finger_id: int):
        if finger_id == self.swipe_touch_id and self.swipe_active:
            self.swipe_current = (x, y)

    # ═══════════════════════════════════════════════════
    def reset_triggers(self):
        """每帧末调用，复位单帧脉冲信号"""
        self.bomb_triggered = False

    # ═══════════════════════════════════════════════════
    def draw(self, surface: pygame.Surface):
        """绘制虚拟控件（半透明）"""
        # ── 滑动方向指示 ──
        if self.swipe_active and self.swipe_start and self.swipe_current:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            sx, sy = self.swipe_start
            cx, cy = self.swipe_current
            # 起点空心圆
            pygame.draw.circle(overlay, (200, 220, 255, 100),
                               (int(sx), int(sy)), 10, 2)
            # 方向线
            pygame.draw.line(overlay, (200, 220, 255, 120),
                             (int(sx), int(sy)), (int(cx), int(cy)), 3)
            # 当前位置实心圆
            pygame.draw.circle(overlay, (200, 220, 255, 150),
                               (int(cx), int(cy)), 8)
            surface.blit(overlay, (0, 0))

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
