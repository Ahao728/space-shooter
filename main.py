"""
main.py — 打飞机 Space Shooter · 游戏入口
"""
import os
import sys
import asyncio
import pygame

# ── 平台检测 ──
IS_WEB = sys.platform == "emscripten"

# ⚠️ 必须在导入子模块之前初始化 pygame，否则各模块的图片预加载会失败
pygame.init()

from settings import (SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, BLACK,
                      POWERUP_DROP_CHANCE, BOMB_FLASH_MS, ASSETS_DIR)
from starfield import Starfield
from player import Player
from enemy import EnemySpawner, BossEnemy
from ui import (draw_hud, draw_game_over, draw_menu, draw_boss_warning,
                draw_pause_overlay, Button, make_pause_button,
                make_resume_button, make_restart_button, make_end_button,
                set_web_mode)
from explosion import spawn_explosion, spawn_sprite_death
from powerup import PowerUp
from mobile_controls import MobileControls


def _load_bg():
    """加载背景图"""
    path = os.path.join(ASSETS_DIR, "background.png")
    try:
        bg = pygame.image.load(path).convert()
        # 480x700 → 拉伸到 480x720
        return pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except Exception:
        return None


class Game:
    """游戏主控制器 — 状态机：menu / playing / game_over"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "menu"
        self._bg = _load_bg()  # 背景图（可选）

        # ── 按钮 ──
        self.btn_pause = make_pause_button()
        self.btn_resume = make_resume_button()
        self.btn_restart = make_restart_button()
        self.btn_end = make_end_button()

        # ── 移动端触摸控件 ──
        self.mobile_ctrl = MobileControls() if IS_WEB else None

        # 告诉 UI 模块当前是 Web 模式（用于菜单提示）
        if IS_WEB:
            set_web_mode(True)

        # ── 鼠标状态 ──
        self._mouse_pos = (0, 0)
        self._mouse_down = False

        self._init_game()

    def _init_game(self):
        self.starfield = Starfield()
        self.player = Player()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.enemy_spawner = EnemySpawner()
        self.score = 0
        self.lives = 3
        self._invincible_until = 0
        self.explosions = []
        self.sprite_explosions = []   # 精灵帧死亡动画
        self._boss_warning_timer = 0
        self._bomb_flash = 0          # 炸弹闪白倒计时
        self._player_dying = False    # 玩家死亡动画中
        self.paused = False

    def _start_game(self):
        self._init_game()
        self.state = "playing"

    # ═══════════════════════════════════════════════════
    def handle_events(self):
        # ── 鼠标状态 ──
        self._mouse_pos = pygame.mouse.get_pos()
        self._mouse_down = False  # 每帧重置，由 MOUSEBUTTONDOWN 设置

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键
                    self._mouse_down = True

            # ── 移动端触摸事件 ──
            if self.mobile_ctrl:
                if event.type in (pygame.FINGERDOWN, pygame.FINGERUP, pygame.FINGERMOTION):
                    self.mobile_ctrl.handle_finger_event(event)
                # 菜单状态下，轻触屏幕任意位置开始游戏
                if self.state == "menu" and event.type == pygame.FINGERDOWN:
                    self._start_game()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                # ── 菜单：空格 / 点击开始按钮 ──
                if self.state == "menu":
                    if event.key == pygame.K_SPACE:
                        self._start_game()

                # ── 结束：R 键重来 ──
                elif self.state == "game_over":
                    if event.key == pygame.K_r:
                        self._init_game()
                        self.state = "playing"

                # ── 游戏中 ──
                elif self.state == "playing" and not self._player_dying:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    # 暂停状态下 R 键重新开始
                    if self.paused and event.key == pygame.K_r:
                        self._init_game()
                        self.state = "playing"

            # ── 玩家键盘输入（仅游戏中 & 未死亡 & 未暂停）──
            if self.state == "playing" and not self._player_dying and not self.paused:
                self.player.handle_event(event)

        # ════════════════════════════════════════
        #  按钮交互（每帧检测）
        # ════════════════════════════════════════
        if self.state == "menu":
            # 菜单：鼠标点击 / 触摸任意位置 → 开始游戏
            if self._mouse_down:
                self._start_game()

        elif self.state == "game_over":
            # 按钮定位到结束页面位置
            cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
            self.btn_restart.rect.center = (cx, cy + 10)
            if self.btn_restart.update(self._mouse_pos, self._mouse_down):
                self._init_game()
                self.state = "playing"
            # 返回主页面按钮
            self.btn_end.rect.center = (cx, cy + 60)
            if self.btn_end.update(self._mouse_pos, self._mouse_down):
                self._init_game()
                self.state = "menu"

        elif self.state == "playing" and not self._player_dying:
            if self.paused:
                # 暂停状态下：继续 + 重新开始按钮
                if self.btn_resume.update(self._mouse_pos, self._mouse_down):
                    self.paused = False
                if self.btn_restart.update(self._mouse_pos, self._mouse_down):
                    self._init_game()
                    self.state = "playing"
            else:
                # 游戏中：右上角暂停按钮
                if self.btn_pause.update(self._mouse_pos, self._mouse_down):
                    self.paused = True

    # ═══════════════════════════════════════════════════
    def _damage_enemy(self, enemy):
        """对敌机造成伤害，处理击杀/得分/爆炸/掉落"""
        enemy.hp -= 1
        # 受击闪烁
        enemy.flash_hit()
        if enemy.hp <= 0:
            self.score += enemy.score
            if isinstance(enemy, BossEnemy):
                etype = "boss"
            elif enemy.score >= 200:
                etype = "large"
            else:
                etype = "small"
            spawn_explosion(self.explosions, enemy.rect.centerx, enemy.rect.centery, etype)
            spawn_sprite_death(self.sprite_explosions, enemy.rect.centerx,
                               enemy.rect.centery, etype)
            PowerUp.maybe_spawn(enemy.rect.centerx, enemy.rect.centery,
                                self.powerups, POWERUP_DROP_CHANCE)
            if isinstance(enemy, BossEnemy):
                self.enemy_spawner.on_boss_killed()
            enemy.kill()

    # ═══════════════════════════════════════════════════
    def update(self):
        if self.state != "playing":
            return

        dt_ms = min(self.clock.get_time(), 50)

        # ── 炸弹闪白倒计时 ──
        if self._bomb_flash > 0:
            self._bomb_flash -= dt_ms

        # ── 暂停 ──
        if self.paused:
            self.starfield.update()
            if self.mobile_ctrl:
                self.mobile_ctrl.reset_triggers()
            return

        # ── 移动端：滑屏跟手控制 ──
        if self.mobile_ctrl:
            mc = self.mobile_ctrl
            # 炸弹
            if mc.bomb_triggered and self.player.bombs > 0:
                self.player._use_bomb = True
            # 滑屏：飞机直接跟随手指位置（手指在哪，飞机就在哪）
            if mc.swipe_active and not self._player_dying:
                self.player.move_to(mc.swipe_current[0], mc.swipe_current[1])

        # ── 玩家死亡动画 ──
        if self._player_dying:
            self.player.update(dt_ms)
            self.starfield.update()
            for exp in self.explosions:
                exp.update()
            self.explosions = [e for e in self.explosions if e.alive]
            for se in self.sprite_explosions:
                se.update(dt_ms)
            self.sprite_explosions = [s for s in self.sprite_explosions if s.alive]
            if self.player.death_finished:
                self.state = "game_over"
            return

        self.starfield.update()
        self.player.update(dt_ms)

        # ════════════════════════════════════════
        #  射击（自动连发，无需按键）
        # ════════════════════════════════════════
        for bullet in self.player.shoot():
            self.bullets.add(bullet)

        # ════════════════════════════════════════
        #  炸弹（B 键 / 清屏）
        # ════════════════════════════════════════
        if self.player.bomb_requested:
            if self.player.consume_bomb():
                self._bomb_flash = BOMB_FLASH_MS
                # 摧毁所有敌机 + 敌弹（计入分数）
                for enemy in list(self.enemies):
                    self.score += enemy.score
                    etype = "boss" if isinstance(enemy, BossEnemy) else \
                            "large" if enemy.score >= 200 else "small"
                    spawn_explosion(self.explosions, enemy.rect.centerx,
                                    enemy.rect.centery, etype)
                    spawn_sprite_death(self.sprite_explosions, enemy.rect.centerx,
                                       enemy.rect.centery, etype)
                    if isinstance(enemy, BossEnemy):
                        self.enemy_spawner.on_boss_killed()
                    enemy.kill()
                for eb in list(self.enemy_bullets):
                    eb.kill()
            self.player.clear_bomb_request()

        # ════════════════════════════════════════
        #  敌机生成
        # ════════════════════════════════════════
        for enemy in self.enemy_spawner.update(dt_ms, self.score):
            self.enemies.add(enemy)
            if isinstance(enemy, BossEnemy):
                self._boss_warning_timer = 1200

        if self._boss_warning_timer > 0:
            self._boss_warning_timer -= dt_ms

        self.bullets.update()
        self.enemies.update()
        self.powerups.update()
        self.enemy_bullets.update()

        # ── 收集 Boss 子弹 ──
        for enemy in self.enemies:
            if isinstance(enemy, BossEnemy):
                for eb in enemy.pending_bullets:
                    self.enemy_bullets.add(eb)

        # ════════════════════════════════════════
        #  碰撞检测
        # ════════════════════════════════════════

        # 1) 子弹 vs 敌机（穿透弹不销毁）
        normal_bullets = [b for b in self.bullets if not b.piercing]
        piercing_bullets = [b for b in self.bullets if b.piercing]

        # 普通子弹：碰撞即销毁
        if normal_bullets:
            ng = pygame.sprite.Group()
            ng.add(normal_bullets)
            hits = pygame.sprite.groupcollide(ng, self.enemies, True, False)
            for bullet, enemies_hit in hits.items():
                for enemy in enemies_hit:
                    self._damage_enemy(enemy)

        # 穿透弹：穿过敌机不销毁
        for bullet in piercing_bullets:
            hit_list = pygame.sprite.spritecollide(bullet, self.enemies, False)
            for enemy in hit_list:
                self._damage_enemy(enemy)

        now = pygame.time.get_ticks()

        # 2) 玩家 vs 道具
        picked = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for pu in picked:
            if pu.pu_type == "life":
                self.lives = min(5, self.lives + 1)
            elif pu.pu_type == "bomb":
                self.player.apply_powerup("bomb")
            elif pu.pu_type == "shield":
                self.player.shield_active = True
            else:
                self.player.apply_powerup(pu.pu_type)

        # 3) 敌机 vs 玩家（仅非无敌期间）
        if now >= self._invincible_until:
            collided = pygame.sprite.spritecollide(self.player, self.enemies, False)
            if collided:
                if self.player.shield_active:
                    self.player.shield_active = False
                    for e in collided:
                        spawn_explosion(self.explosions, e.rect.centerx, e.rect.centery)
                        if isinstance(e, BossEnemy):
                            self.enemy_spawner.on_boss_killed()
                        e.kill()
                else:
                    self.lives -= 1
                    self._invincible_until = now + 2000
                    spawn_explosion(self.explosions, self.player.x, self.player.y,
                                    color_palette=[(100, 180, 255), (180, 220, 255), (255, 255, 255)])
                    if self.lives <= 0:
                        self._player_dying = True
                        self.player.start_death()
                        return

        # 4) 敌弹 vs 玩家（仅非无敌期间）
        if now >= self._invincible_until:
            hit_by_bullet = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
            if hit_by_bullet:
                if self.player.shield_active:
                    self.player.shield_active = False
                else:
                    self.lives -= 1
                    self._invincible_until = now + 2000
                    if self.lives <= 0:
                        self._player_dying = True
                        self.player.start_death()
                        return

        # ── 爆炸更新 ──
        for exp in self.explosions:
            exp.update()
        self.explosions = [e for e in self.explosions if e.alive]
        for se in self.sprite_explosions:
            se.update(dt_ms)
        self.sprite_explosions = [s for s in self.sprite_explosions if s.alive]

        # ── 重置触摸单帧信号 ──
        if self.mobile_ctrl:
            self.mobile_ctrl.reset_triggers()

    # ═══════════════════════════════════════════════════
    def draw(self):
        # ── 背景 ──
        if self._bg:
            self.screen.blit(self._bg, (0, 0))
        else:
            self.screen.fill(BLACK)

        if self.state == "menu":
            self.starfield.update()
            self.starfield.draw(self.screen)
            draw_menu(self.screen)

        elif self.state == "playing":
            self.starfield.draw(self.screen)
            self.bullets.draw(self.screen)
            self.enemy_bullets.draw(self.screen)
            self.enemies.draw(self.screen)
            self.powerups.draw(self.screen)
            for exp in self.explosions:
                exp.draw(self.screen)
            for se in self.sprite_explosions:
                se.draw(self.screen)

            now = pygame.time.get_ticks()
            visible = not (now < self._invincible_until and (now // 100) % 2 == 0)
            if visible:
                self.player.draw(self.screen)

            draw_hud(
                self.screen, self.score, self.lives,
                self.player.weapon_type, self.player.weapon_timer,
                self.player.shield_active,
                self.player.has_triple, self.player.triple_timer,
                self.player.has_rapid, self.player.rapid_timer,
                self.player.has_piercing, self.player.piercing_timer,
                self.player.bombs,
            )
            draw_boss_warning(self.screen, self._boss_warning_timer)

            # 暂停按钮（右上角，游戏中常驻）
            if not self.paused and not self._player_dying:
                self.btn_pause.draw(self.screen)

            if self.paused:
                draw_pause_overlay(self.screen, self.btn_resume, self.btn_restart)
                if self.mobile_ctrl:
                    self.mobile_ctrl.draw(self.screen)

            # ── 炸弹闪白效果 ──
            if self._bomb_flash > 0:
                alpha = int(120 * (self._bomb_flash / BOMB_FLASH_MS))
                flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                flash.fill((255, 255, 255, alpha))
                self.screen.blit(flash, (0, 0))

            # ── 移动端控件（最上层）──
            if self.mobile_ctrl:
                self.mobile_ctrl.draw(self.screen)

        elif self.state == "game_over":
            self.starfield.update()
            self.starfield.draw(self.screen)
            self.bullets.draw(self.screen)
            self.enemies.draw(self.screen)
            self.enemy_bullets.draw(self.screen)
            for exp in self.explosions:
                exp.draw(self.screen)
            for se in self.sprite_explosions:
                se.draw(self.screen)
            self.player.draw(self.screen)
            draw_game_over(self.screen, self.score, self.btn_restart, self.btn_end)

        pygame.display.flip()

    def run(self):
        """桌面同步主循环"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        if not IS_WEB:
            sys.exit()

    async def run_web(self):
        """Web 异步主循环 — 每帧 yield 给浏览器"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            await asyncio.sleep(0)
        pygame.quit()


async def _web_main():
    """pygbag 入口：创建 Game 并运行异步循环"""
    game = Game()
    await game.run_web()


if __name__ == "__main__":
    if IS_WEB:
        asyncio.run(_web_main())
    else:
        game = Game()
        game.run()
