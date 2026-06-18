"""
ui.py — 中文 HUD / 菜单 / 结束画面 / 暂停 / Boss 警告
打飞机 Space Shooter
"""
import os
import io
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, YELLOW, CYAN, ORANGE, GREEN, ASSETS_DIR

# ═══════════════════════════════════════════════════════════
#  中文字体加载
# ═══════════════════════════════════════════════════════════
_cjk_font_cache = {}

# Web 模式标记（由 main.py 设置）
_web_mode = False


def set_web_mode(enabled: bool):
    """通知 UI 当前运行在 Web/移动端模式下"""
    global _web_mode
    _web_mode = enabled


class _FreetypeFontAdapter:
    """将 pygame.freetype.Font 适配为 pygame.font.Font 的 .render() 接口"""

    def __init__(self, ft_font, ptsize: int):
        self._ft = ft_font
        self.ptsize = ptsize

    def render(self, text: str, antialias: bool, color,
               background=None) -> pygame.Surface:
        """返回 pygame.Surface（兼容 pygame.font.Font.render）"""
        kwargs = dict(fgcolor=color, size=self.ptsize)
        if background is not None:
            kwargs["bgcolor"] = background
        surf, _rect = self._ft.render(text, **kwargs)
        return surf


def _load_cjk_font(size: int):
    """加载支持中文的字体，带缓存。
    返回 pygame.font.Font 或 _FreetypeFontAdapter（均支持 .render()）"""

    if size in _cjk_font_cache:
        return _cjk_font_cache[size]

    # ═══════════════════════════════════════════════════════
    #  1. 尝试 pygame.freetype 加载捆绑字体（Web + 桌面通用）
    # ═══════════════════════════════════════════════════════
    bundled = os.path.join(ASSETS_DIR, "font.ttf")
    try:
        # 方式 A：文件路径（桌面环境有效）
        ft = pygame.freetype.Font(bundled, size=size)
        test_surf, _ = ft.render("中", fgcolor=WHITE, size=size)
        if test_surf.get_width() > 5:
            font = _FreetypeFontAdapter(ft, size)
            _cjk_font_cache[size] = font
            return font
    except Exception:
        pass

    # 方式 B：读取字节流传入（Web 环境更可靠）
    try:
        with open(bundled, "rb") as fh:
            font_data = fh.read()
        ft = pygame.freetype.Font(io.BytesIO(font_data), size=size)
        test_surf, _ = ft.render("中", fgcolor=WHITE, size=size)
        if test_surf.get_width() > 5:
            font = _FreetypeFontAdapter(ft, size)
            _cjk_font_cache[size] = font
            return font
    except Exception:
        pass

    # ═══════════════════════════════════════════════════════
    #  2. 传统 pygame.font 方式（后备）
    # ═══════════════════════════════════════════════════════
    if os.path.exists(bundled):
        try:
            font = pygame.font.Font(bundled, size)
            test = font.render("中", True, WHITE)
            if test.get_width() > 5:
                _cjk_font_cache[size] = font
                return font
        except Exception:
            pass

    # ═══════════════════════════════════════════════════════
    #  3. 系统字体名
    # ═══════════════════════════════════════════════════════
    font_names = [
        "simhei", "microsoftyahei", "notosanscjk",
        "wqy-microhei", "pingfang", "heiti sc",
    ]
    for name in font_names:
        try:
            font = pygame.font.SysFont(name, size)
            test = font.render("中", True, WHITE)
            if test.get_width() > 5:
                _cjk_font_cache[size] = font
                return font
        except Exception:
            continue

    # ═══════════════════════════════════════════════════════
    #  4. Windows 字体路径（桌面兜底）
    # ═══════════════════════════════════════════════════════
    win_font_paths = [
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\Deng.ttf",
    ]
    for path in win_font_paths:
        if os.path.exists(path):
            try:
                font = pygame.font.Font(path, size)
                _cjk_font_cache[size] = font
                return font
            except Exception:
                continue

    # ═══════════════════════════════════════════════════════
    #  5. 默认字体（ASCII only，中文会变豆腐块）
    # ═══════════════════════════════════════════════════════
    font = pygame.font.Font(None, size)
    _cjk_font_cache[size] = font
    return font


# ═══════════════════════════════════════════════════════════
#  UI 贴图预加载
# ═══════════════════════════════════════════════════════════

def _load_ui_img(filename: str):
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

_UI_GAMEOVER = _load_ui_img("gameover.png")            # 300x41
_UI_PAUSE_NOR = _load_ui_img("pause_nor.png")          # 60x45
_UI_PAUSE_PRESSED = _load_ui_img("pause_pressed.png")  # 60x45
_UI_RESUME_NOR = _load_ui_img("resume_nor.png")        # 60x45
_UI_RESUME_PRESSED = _load_ui_img("resume_pressed.png") # 60x45
_UI_AGAIN = _load_ui_img("again.png")                  # 300x41
_UI_LIFE = _load_ui_img("life.png")                    # 46x57
_UI_BOMB = _load_ui_img("bomb.png")                    # 63x57


# ═══════════════════════════════════════════════════════════
#  Button 类
# ═══════════════════════════════════════════════════════════

class Button:
    """可点击按钮 — 支持 hover 切换贴图"""

    def __init__(self, x: float, y: float, normal_img, hover_img=None,
                 center: bool = True):
        img = normal_img or pygame.Surface((1, 1))
        self.rect = img.get_rect()
        if center:
            self.rect.center = (int(x), int(y))
        else:
            self.rect.topleft = (int(x), int(y))
        self.normal_img = normal_img
        self.hover_img = hover_img or normal_img
        self._hovered = False
        self._was_clicked = False

    def update(self, mouse_pos: tuple, mouse_down: bool):
        """每帧调用：检测 hover + click"""
        self._hovered = self.rect.collidepoint(mouse_pos)
        self._was_clicked = self._hovered and mouse_down
        return self._was_clicked

    @property
    def clicked(self) -> bool:
        return self._was_clicked

    @property
    def hovered(self) -> bool:
        return self._hovered

    def draw(self, surface: pygame.Surface):
        img = self.hover_img if self._hovered and self.hover_img else self.normal_img
        if img is not None:
            surface.blit(img, self.rect)


# ═══════════════════════════════════════════════════════════
#  爱心绘制
# ════════════════════════════════════════════════════
# ═══════

def _draw_heart(surface: pygame.Surface, x: float, y: float, size: int = 7):
    """用基本图形绘制一颗爱心（兜底）"""
    r = size / 2
    pygame.draw.circle(surface, RED, (int(x - r * 0.7), int(y - r * 0.4)), int(r * 0.6))
    pygame.draw.circle(surface, RED, (int(x + r * 0.7), int(y - r * 0.4)), int(r * 0.6))
    pts = [
        (x - size * 0.8, y - r * 0.2),
        (x + size * 0.8, y - r * 0.2),
        (x, y + size * 0.7),
    ]
    pygame.draw.polygon(surface, RED, pts)
    pygame.draw.circle(surface, (255, 200, 200), (int(x - r * 0.3), int(y - r * 0.8)), int(r * 0.25))


def _draw_life_icon(surface: pygame.Surface, x: float, y: float, size: int = 18):
    """绘制生命图标 — 优先使用贴图"""
    if _UI_LIFE is not None:
        w, h = _UI_LIFE.get_size()
        scale = size / max(w, h)
        img = pygame.transform.scale(_UI_LIFE, (int(w * scale), int(h * scale)))
        rect = img.get_rect(center=(int(x), int(y)))
        surface.blit(img, rect)
    else:
        _draw_heart(surface, x, y, size=7)


# ═══════════════════════════════════════════════════════════
#  增益小图标绘制
# ═══════════════════════════════════════════════════════════

def _draw_shield_icon(surface: pygame.Surface, x: float, y: float):
    """护盾图标 — 蓝色圆环"""
    r = 6
    pygame.draw.circle(surface, (60, 160, 255), (int(x), int(y)), r, 2)
    pygame.draw.circle(surface, (120, 200, 255), (int(x - 1), int(y - 1)), r - 3)

def _draw_triple_icon(surface: pygame.Surface, x: float, y: float):
    """三连射图标 — 三个绿点扇形"""
    c = (60, 255, 120)
    for dx, dy in [(-3, -1), (3, -3), (3, 3)]:
        pygame.draw.circle(surface, c, (int(x + dx), int(y + dy)), 2)

def _draw_rapid_icon(surface: pygame.Surface, x: float, y: float):
    """速射图标 — 黄色双竖线"""
    c = (255, 220, 40)
    for dx in [-2, 2]:
        pygame.draw.line(surface, c, (x + dx, y - 5), (x + dx, y + 5), 2)

def _draw_piercing_icon(surface: pygame.Surface, x: float, y: float):
    """穿透弹图标 — 金色箭头穿过方块"""
    r = 5
    pygame.draw.rect(surface, (100, 200, 255),
                     (int(x - r * 0.4), int(y - r * 0.6), int(r * 0.8), int(r * 1.2)), 1)
    pts = [(x - r, y - 2), (x + r - 1, y - 4), (x + r - 1, y), (x - r, y + 2)]
    pygame.draw.polygon(surface, (255, 200, 40), pts)

def _draw_bomb_icon(surface: pygame.Surface, x: float, y: float):
    """炸弹图标 — 优先使用 bomb.png 贴图"""
    if _UI_BOMB is not None:
        w, h = _UI_BOMB.get_size()
        scale = 14 / max(w, h)
        img = pygame.transform.scale(_UI_BOMB, (int(w * scale), int(h * scale)))
        rect = img.get_rect(center=(int(x), int(y)))
        surface.blit(img, rect)
    else:
        r = 5
        pygame.draw.circle(surface, (255, 160, 30), (int(x), int(y)), r)
        pygame.draw.circle(surface, (255, 220, 100), (int(x - 1), int(y - 1)), r - 2)
        pygame.draw.circle(surface, (255, 255, 150), (int(x + r - 1), int(y - r + 1)), 2)

_BUFF_ICONS = {
    "shield":   _draw_shield_icon,
    "triple":   _draw_triple_icon,
    "rapid":    _draw_rapid_icon,
    "piercing": _draw_piercing_icon,
    "bomb":     _draw_bomb_icon,
}


# ═══════════════════════════════════════════════════════════
#  HUD
# ═══════════════════════════════════════════════════════════

def draw_hud(surface: pygame.Surface, score: int, lives: int,
             weapon_type: str = "normal", weapon_timer: int = 0, shield: bool = False,
             has_triple: bool = False, triple_timer: int = 0,
             has_rapid: bool = False, rapid_timer: int = 0,
             has_piercing: bool = False, piercing_timer: int = 0,
             bombs: int = 0):
    """顶栏：分数（左）+ 爱心生命（右）+ 武器状态 + 炸弹数"""
    font = _load_cjk_font(24)
    small_font = _load_cjk_font(18)

    # 分数
    score_text = font.render(f"分数 {score}", True, WHITE)
    surface.blit(score_text, (14, 8))

    # 生命（使用贴图图标）
    for i in range(lives):
        _draw_life_icon(surface, SCREEN_WIDTH - 22 - i * 24, 18, size=16)

    # 武器状态 — 每种增益独立一行，前面画对应图标
    lines = []  # (icon_key, text)

    if shield:
        lines.append(("shield", "护盾"))
    if has_triple:
        secs = max(0, triple_timer) // 1000 + 1
        lines.append(("triple", "三连射 {}秒".format(secs)))
    if has_rapid:
        secs = max(0, rapid_timer) // 1000 + 1
        lines.append(("rapid", "速射 {}秒".format(secs)))
    if has_piercing:
        secs = max(0, piercing_timer) // 1000 + 1
        lines.append(("piercing", "穿透弹 {}秒".format(secs)))
    # 兼容旧调用
    if not has_triple and not has_rapid and not has_piercing and weapon_type != "normal":
        secs = max(0, weapon_timer) // 1000 + 1
        label = {"triple": "三连射", "rapid": "速射", "combo": "三连+速射",
                 "piercing": "穿透弹"}.get(weapon_type, weapon_type)
        lines.append((weapon_type.split("+")[0] if "+" in weapon_type else weapon_type,
                      "{} {}秒".format(label, secs)))

    # 炸弹数
    if bombs > 0:
        lines.append(("bomb", "炸弹 x{}".format(bombs)))

    for i, (icon_key, text) in enumerate(lines):
        y = 44 + i * 22
        # 画图标
        draw_fn = _BUFF_ICONS.get(icon_key)
        if draw_fn:
            draw_fn(surface, 22, y)
        # 画文字（图标右侧）
        txt = small_font.render(text, True, YELLOW)
        surface.blit(txt, (32, y - 6))


# ═══════════════════════════════════════════════════════════
#  开始菜单
# ═══════════════════════════════════════════════════════════

def draw_menu(surface: pygame.Surface):
    """开始菜单画面"""
    cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

    title_font = _load_cjk_font(64)
    title = title_font.render("太空射击", True, CYAN)
    title_rect = title.get_rect(center=(cx, cy - 140))
    surface.blit(title, title_rect)

    sub_font = _load_cjk_font(28)
    sub = sub_font.render("SPACE  SHOOTER", True, (150, 170, 220))
    sub_rect = sub.get_rect(center=(cx, cy - 85))
    surface.blit(sub, sub_rect)

    # 闪烁提示（黑色文字）
    tick = pygame.time.get_ticks()
    if (tick // 700) % 2 == 0:
        hint_font = _load_cjk_font(28)
        if _web_mode:
            hint_text = "点击屏幕开始游戏"
        else:
            hint_text = "按 空格键 开始游戏"
        hint = hint_font.render(hint_text, True, (20, 20, 30))
        hint_rect = hint.get_rect(center=(cx, cy + 20))
        surface.blit(hint, hint_rect)

    # 操作说明
    ctrl_font = _load_cjk_font(18)
    if _web_mode:
        controls = [
            "← 虚拟摇杆  —  移动飞船",
            "（自动连射，无需按键）",
            "⏸ 右上角   —  暂停游戏",
            "B 按钮       —  清屏炸弹",
        ]
    else:
        controls = [
            "方向键 / WASD   —  移动飞船",
            "（自动连射，无需按键）",
            "P 键              —  暂停游戏",
            "B 键              —  使用清屏炸弹",
            "ESC 键           —  退出游戏",
        ]
    for i, line in enumerate(controls):
        txt = ctrl_font.render(line, True, (140, 150, 180))
        surface.blit(txt, txt.get_rect(center=(cx, cy + 70 + i * 26)))

    # 敌机装饰（使用精灵图）
    _enemy1_dec = _load_ui_img("enemy1.png")
    _enemy2_dec = _load_ui_img("enemy2.png")
    tick = pygame.time.get_ticks()
    for i in range(3):
        ex = cx + (i - 1) * 70
        ey = cy - 190
        if _enemy2_dec:
            img = pygame.transform.scale(_enemy2_dec, (40, 57))
            surface.blit(img, img.get_rect(center=(ex, ey)))
        elif _enemy1_dec:
            img = pygame.transform.scale(_enemy1_dec, (35, 26))
            surface.blit(img, img.get_rect(center=(ex, ey - 5)))

    # 版本号
    ver = ctrl_font.render("v2.0", True, (80, 80, 100))
    surface.blit(ver, (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 30))


# ═══════════════════════════════════════════════════════════
#  游戏结束
# ═══════════════════════════════════════════════════════════

def draw_game_over(surface: pygame.Surface, score: int,
                   btn_restart: Button = None, btn_end: Button = None):
    """游戏结束覆盖层"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

    # 标题文字
    title_font = _load_cjk_font(64)
    title = title_font.render("游 戏 结 束", True, RED)
    surface.blit(title, title.get_rect(center=(cx, cy - 120)))

    # 分数
    score_font = _load_cjk_font(40)
    score_text = score_font.render(f"最终分数：{score}", True, YELLOW)
    surface.blit(score_text, score_text.get_rect(center=(cx, cy - 55)))

    # 按钮（位置由 main 在 handle_events 中设定）
    if btn_restart:
        btn_restart.draw(surface)
    if btn_end:
        btn_end.draw(surface)

    # 键盘提示
    hint_font = _load_cjk_font(18)
    hint = hint_font.render("R 键 重新开始    ESC 键 退出游戏", True,
                            (160, 180, 200))
    surface.blit(hint, hint.get_rect(center=(cx, cy + 105)))

    tick = pygame.time.get_ticks()
    if (tick // 600) % 2 == 0:
        arrow = hint_font.render("▼", True, ORANGE)
        surface.blit(arrow, arrow.get_rect(center=(cx, cy + 125)))


# ═══════════════════════════════════════════════════════════
#  Boss 警告
# ═══════════════════════════════════════════════════════════

def draw_boss_warning(surface: pygame.Surface, timer: int):
    """Boss 出现警告 — 红色闪烁边框 + 居中大字"""
    if timer <= 0:
        return
    tick = pygame.time.get_ticks()

    # 屏幕边缘红色闪烁
    alpha = 40 + int(30 * abs((tick % 400) / 200 - 1))
    border = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    border_width = 4
    pygame.draw.rect(border, (255, 40, 40, alpha),
                     (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), border_width)
    pygame.draw.rect(border, (255, 80, 40, alpha // 2),
                     (4, 4, SCREEN_WIDTH - 8, SCREEN_HEIGHT - 8), 2)
    surface.blit(border, (0, 0))

    # 闪烁警告文字
    if (tick // 160) % 2 == 0:
        cx = SCREEN_WIDTH // 2
        font_large = _load_cjk_font(44)
        # 光晕
        glow = font_large.render("！！ BOSS 来袭 ！！", True, (255, 200, 40))
        text = font_large.render("！！ BOSS 来袭 ！！", True, RED)
        for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, 0)]:
            s = glow if (ox, oy) != (0, 0) else text
            r = s.get_rect(center=(cx + ox, 100 + oy))
            surface.blit(s, r)


# ═══════════════════════════════════════════════════════════
#  暂停
# ═══════════════════════════════════════════════════════════

def draw_pause_overlay(surface: pygame.Surface,
                       btn_resume: Button = None,
                       btn_restart: Button = None):
    """暂停覆盖层 — 含继续 + 重新开始按钮"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surface.blit(overlay, (0, 0))

    cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

    font = _load_cjk_font(48)
    text = font.render("游 戏 暂 停", True, WHITE)
    text_rect = text.get_rect(center=(cx, cy - 120))
    surface.blit(text, text_rect)

    # 按钮（纵向排列，避免重叠）
    if btn_resume:
        btn_resume.draw(surface)
    if btn_restart:
        btn_restart.draw(surface)

    # 键盘提示
    hint_font = _load_cjk_font(18)
    hint = hint_font.render("P 键继续    R 键重新开始", True, (160, 180, 200))
    hint_rect = hint.get_rect(center=(cx, cy + 140))
    surface.blit(hint, hint_rect)


# ═══════════════════════════════════════════════════════════
#  创建按钮实例（供 main 使用）
# ═══════════════════════════════════════════════════════════

def make_pause_button() -> Button:
    """游戏中的暂停按钮（右上角，生命值下方）"""
    return Button(SCREEN_WIDTH - 40, 50, _UI_PAUSE_NOR, _UI_PAUSE_PRESSED)

def make_resume_button() -> Button:
    """暂停界面 — 继续按钮（居中偏上）"""
    cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    return Button(cx, cy - 10, _UI_RESUME_NOR, _UI_RESUME_PRESSED)

def make_restart_button() -> Button:
    """暂停/结束界面 — 重新开始按钮"""
    cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    return Button(cx, cy + 55, _UI_AGAIN, _UI_AGAIN)

def make_end_button() -> Button:
    """结束界面 — 结束游戏按钮（使用 gameover.png，点击回主页面）"""
    return Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60, _UI_GAMEOVER, _UI_GAMEOVER)
