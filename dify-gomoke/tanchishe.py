# -*- coding: utf-8 -*-
import pygame
import random
import sys
import json
import os
from pygame.locals import *

# 初始化pygame
pygame.init()
pygame.mixer.init()

# 常量定义
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
FPS = 60

# 颜色定义
COLOR_BG = (51, 51, 51)        # 背景色
COLOR_SNAKE = (76, 175, 80)    # 蛇身颜色
COLOR_FOOD = (244, 67, 54)     # 食物颜色
COLOR_TEXT = (255, 255, 255)   # 文字颜色
COLOR_BUTTON = (33, 150, 243)  # 按钮颜色
COLOR_GRID = (70, 70, 70)      # 网格线颜色

# 方向定义
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock()
        # 尝试使用支持中文的字体
        try:
            self.font_small = pygame.font.SysFont('PingFang SC', 14)
            self.font_medium = pygame.font.SysFont('PingFang SC', 18)
            self.font_large = pygame.font.SysFont('PingFang SC', 24, bold=True)
        except:
            # 如果PingFang SC不可用，使用系统默认字体
            self.font_small = pygame.font.SysFont(None, 14)
            self.font_medium = pygame.font.SysFont(None, 18)
            self.font_large = pygame.font.SysFont(None, 24)
        
        # 游戏状态
        self.game_state = "MENU"  # MENU, PLAYING, PAUSED, GAME_OVER
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.food = self.generate_food()
        self.score = 0
        self.high_score = self.load_high_score()
        self.speed_level = 1
        self.speed = 10  # 初始速度
        self.frame_count = 0
        
        # 游戏设置
        self.settings = {
            "wall_mode": True,
            "grid_display": False,
            "sound_effects": True,
            "music": True,
            "game_speed": 5
        }
        self.load_settings()
        
        # 加载音效
        self.load_sounds()
        
        # 初始化背景音乐
        if self.settings["music"]:
            try:
                pygame.mixer.music.load("background.mp3")  # 需要提供音乐文件
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)  # 循环播放
            except:
                # 如果没有音乐文件，就跳过音乐播放
                pass
    
    def load_sounds(self):
        # 这里应该加载音效文件，示例中使用空音效
        self.eat_sound = pygame.mixer.Sound("eat.wav") if os.path.exists("eat.wav") else None
        self.crash_sound = pygame.mixer.Sound("crash.wav") if os.path.exists("crash.wav") else None
        self.button_sound = pygame.mixer.Sound("button.wav") if os.path.exists("button.wav") else None
    
    def play_sound(self, sound):
        if self.settings["sound_effects"] and sound:
            sound.play()
    
    def load_high_score(self):
        try:
            with open('highscore.json', 'r') as f:
                data = json.load(f)
                return data.get('high_score', 0)
        except (FileNotFoundError, json.JSONDecodeError):
            return 0
    
    def save_high_score(self):
        with open('highscore.json', 'w') as f:
            json.dump({'high_score': self.high_score}, f)
    
    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                loaded_settings = json.load(f)
                for key in self.settings:
                    if key in loaded_settings:
                        self.settings[key] = loaded_settings[key]
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    
    def save_settings(self):
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f)
    
    def generate_food(self):
        while True:
            food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if food not in self.snake:
                return food
    
    def reset_game(self):
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.food = self.generate_food()
        self.score = 0
        self.speed_level = 1
        self.speed = 10
        self.frame_count = 0
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    mouse_pos = pygame.mouse.get_pos()
                    self.handle_mouse_click(mouse_pos)
            
            elif event.type == KEYDOWN:
                if self.game_state == "PLAYING":
                    if event.key == K_UP and self.direction != DOWN:
                        self.next_direction = UP
                    elif event.key == K_DOWN and self.direction != UP:
                        self.next_direction = DOWN
                    elif event.key == K_LEFT and self.direction != RIGHT:
                        self.next_direction = LEFT
                    elif event.key == K_RIGHT and self.direction != LEFT:
                        self.next_direction = RIGHT
                    elif event.key == K_SPACE:
                        self.game_state = "PAUSED"
                        self.play_sound(self.button_sound)
                    elif event.key == K_ESCAPE:
                        self.game_state = "MENU"
                        self.play_sound(self.button_sound)
                
                elif self.game_state == "PAUSED":
                    if event.key == K_SPACE:
                        self.game_state = "PLAYING"
                        self.play_sound(self.button_sound)
                    elif event.key == K_ESCAPE:
                        self.game_state = "MENU"
                        self.play_sound(self.button_sound)
                
                elif self.game_state == "MENU":
                    if event.key == K_RETURN:
                        self.game_state = "PLAYING"
                        self.reset_game()
                        self.play_sound(self.button_sound)
                
                elif self.game_state == "GAME_OVER":
                    if event.key == K_RETURN:
                        self.game_state = "PLAYING"
                        self.reset_game()
                        self.play_sound(self.button_sound)
                    elif event.key == K_ESCAPE:
                        self.game_state = "MENU"
                        self.play_sound(self.button_sound)
    
    def handle_mouse_click(self, mouse_pos):
        """处理鼠标点击事件"""
        x, y = mouse_pos
        
        if self.game_state == "MENU":
            # 检查菜单按钮点击
            button_y_positions = [150, 200, 250, 300]  # Play Game, Settings, Help, Exit
            button_texts = ["Play Game", "Settings", "Help", "Exit"]
            
            for i, (pos_y, text) in enumerate(zip(button_y_positions, button_texts)):
                text_surface = self.font_medium.render(text, True, COLOR_BUTTON)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, pos_y))
                
                if text_rect.collidepoint(x, y):
                    if i == 0:  # Play Game
                        self.game_state = "PLAYING"
                        self.reset_game()
                        self.play_sound(self.button_sound)
                    elif i == 3:  # Exit
                        pygame.quit()
                        sys.exit()
                    break
        
        elif self.game_state == "PAUSED":
            # 检查暂停菜单按钮点击
            button_y_positions = [180, 230, 280]  # Resume, Restart, Main Menu
            button_texts = ["Resume", "Restart", "Main Menu"]
            
            for i, (pos_y, text) in enumerate(zip(button_y_positions, button_texts)):
                text_surface = self.font_medium.render(text, True, COLOR_BUTTON)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, pos_y))
                
                if text_rect.collidepoint(x, y):
                    if i == 0:  # Resume
                        self.game_state = "PLAYING"
                        self.play_sound(self.button_sound)
                    elif i == 1:  # Restart
                        self.game_state = "PLAYING"
                        self.reset_game()
                        self.play_sound(self.button_sound)
                    elif i == 2:  # Main Menu
                        self.game_state = "MENU"
                        self.play_sound(self.button_sound)
                    break
        
        elif self.game_state == "GAME_OVER":
            # 检查游戏结束菜单按钮点击
            button_y_positions = [220, 270]  # Play Again, Main Menu
            button_texts = ["Play Again", "Main Menu"]
            
            for i, (pos_y, text) in enumerate(zip(button_y_positions, button_texts)):
                text_surface = self.font_medium.render(text, True, COLOR_BUTTON)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, pos_y))
                
                if text_rect.collidepoint(x, y):
                    if i == 0:  # Play Again
                        self.game_state = "PLAYING"
                        self.reset_game()
                        self.play_sound(self.button_sound)
                    elif i == 1:  # Main Menu
                        self.game_state = "MENU"
                        self.play_sound(self.button_sound)
                    break
    
    def update(self):
        if self.game_state != "PLAYING":
            return
        
        self.frame_count += 1
        if self.frame_count < self.speed:
            return
        
        self.frame_count = 0
        self.direction = self.next_direction
        
        # 移动蛇
        head_x, head_y = self.snake[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)
        
        # 检查碰撞
        if self.settings["wall_mode"]:
            if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or 
                new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
                self.game_over()
                return
        else:
            # 穿墙模式
            new_head = (new_head[0] % GRID_WIDTH, new_head[1] % GRID_HEIGHT)
        
        if new_head in self.snake:
            self.game_over()
            return
        
        # 检查是否吃到食物
        if new_head == self.food:
            self.snake.insert(0, new_head)
            self.food = self.generate_food()
            self.score += 10
            self.play_sound(self.eat_sound)
            
            # 更新最高分
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            
            # 每10分提高速度
            if self.score % 100 == 0 and self.speed_level < 10:
                self.speed_level += 1
                self.speed = max(1, 10 - self.speed_level)
        else:
            self.snake.insert(0, new_head)
            self.snake.pop()
    
    def game_over(self):
        self.game_state = "GAME_OVER"
        self.play_sound(self.crash_sound)
    
    def draw(self):
        self.screen.fill(COLOR_BG)
        
        if self.settings["grid_display"]:
            for x in range(0, SCREEN_WIDTH, GRID_SIZE):
                pygame.draw.line(self.screen, COLOR_GRID, (x, 0), (x, SCREEN_HEIGHT))
            for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
                pygame.draw.line(self.screen, COLOR_GRID, (0, y), (SCREEN_WIDTH, y))
        
        # 绘制食物
        food_rect = pygame.Rect(
            self.food[0] * GRID_SIZE, 
            self.food[1] * GRID_SIZE, 
            GRID_SIZE, GRID_SIZE
        )
        pygame.draw.ellipse(self.screen, COLOR_FOOD, food_rect)
        
        # 绘制蛇
        for segment in self.snake:
            segment_rect = pygame.Rect(
                segment[0] * GRID_SIZE, 
                segment[1] * GRID_SIZE, 
                GRID_SIZE, GRID_SIZE
            )
            pygame.draw.rect(self.screen, COLOR_SNAKE, segment_rect)
            pygame.draw.rect(self.screen, COLOR_BG, segment_rect, 1)  # 边框
        
        # 绘制游戏信息
        score_text = self.font_small.render(f"Score: {self.score}", True, COLOR_TEXT)
        high_score_text = self.font_small.render(f"High Score: {self.high_score}", True, COLOR_TEXT)
        speed_text = self.font_small.render(f"Speed: {self.speed_level}", True, COLOR_TEXT)
        pause_text = self.font_medium.render("Pause (SPACE)", True, COLOR_BUTTON)
        
        self.screen.blit(high_score_text, (10, 10))
        self.screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, 10))
        self.screen.blit(speed_text, (10, SCREEN_HEIGHT - 30))
        self.screen.blit(pause_text, (SCREEN_WIDTH - pause_text.get_width() - 10, SCREEN_HEIGHT - 30))
        
        # 绘制菜单界面
        if self.game_state == "MENU":
            self.draw_menu()
        elif self.game_state == "PAUSED":
            self.draw_pause_menu()
        elif self.game_state == "GAME_OVER":
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_menu(self):
        # 半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # 标题
        title = self.font_large.render("SNAKE GAME", True, COLOR_TEXT)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        # 菜单选项
        options = ["Play Game", "Settings", "Help", "Exit"]
        for i, option in enumerate(options):
            text = self.font_medium.render(option, True, COLOR_BUTTON)
            self.screen.blit(text, (
                SCREEN_WIDTH // 2 - text.get_width() // 2,
                150 + i * 50
            ))
    
    def draw_pause_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        title = self.font_large.render("PAUSED", True, COLOR_TEXT)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        options = ["Resume", "Restart", "Main Menu"]
        for i, option in enumerate(options):
            text = self.font_medium.render(option, True, COLOR_BUTTON)
            self.screen.blit(text, (
                SCREEN_WIDTH // 2 - text.get_width() // 2,
                180 + i * 50
            ))
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        title = self.font_large.render("GAME OVER", True, COLOR_TEXT)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        score_text = self.font_medium.render(f"Your Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (
            SCREEN_WIDTH // 2 - score_text.get_width() // 2,
            160
        ))
        
        options = ["Play Again", "Main Menu"]
        for i, option in enumerate(options):
            text = self.font_medium.render(option, True, COLOR_BUTTON)
            self.screen.blit(text, (
                SCREEN_WIDTH // 2 - text.get_width() // 2,
                220 + i * 50
            ))
    
    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = SnakeGame()
    game.run()