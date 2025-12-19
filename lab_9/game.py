import random
import sys
import pygame
from pygame.locals import *
from config_manager import GameConfig


class AssetLoader:
    def __init__(self, config):
        self.config = config
        self.images = {}
        self.load_images()
    
    def load_images(self):
        # Загрузка с fallback
        def load(path, fallback_color):
            try:
                return pygame.image.load(path).convert_alpha()
            except:
                surf = pygame.Surface((50, 50))
                surf.fill(fallback_color)
                return surf
        
        # Основные изображения
        self.images['bird'] = load(
            self.config.get_image_path('bird'),
            self.config.get_color('fallback_bird', (255, 255, 0))
        )
        
        self.images['background'] = load(
            self.config.get_image_path('background'),
            self.config.get_color('fallback_bg', (135, 206, 235))
        )
        
        self.images['ground'] = load(
            self.config.get_image_path('ground'),
            self.config.get_color('fallback_ground', (222, 184, 135))
        )
        
        pipe_img = load(
            self.config.get_image_path('pipe'),
            self.config.get_color('fallback_pipe', (0, 180, 0))
        )
        self.images['pipe'] = (pygame.transform.rotate(pipe_img, 180), pipe_img)


class Game:
    def __init__(self, config_layer=None):
        pygame.init()
        
        self.config = GameConfig(config_layer)
        self.assets = AssetLoader(self.config)
        
        self.window = pygame.display.set_mode(
            (self.config.window_width, self.config.window_height)
        )
        pygame.display.set_caption(self.config.title)
        
        self.clock = pygame.time.Clock()
        self.reset()
    
    def reset(self):
        self.score = 0
        self.bird_x = self.config.window_width // 5
        self.bird_y = self.config.window_height // 2
        self.bird_vel_y = 0
        self.pipes = []
        self.game_over = False
        self.add_pipe()
        self.add_pipe()
    
    def add_pipe(self):
        offset = self.config.window_height // 3
        pipe_height = self.assets.images['pipe'][0].get_height()
        
        y2 = offset + random.randrange(
            0, int(self.config.window_height - self.assets.images['ground'].get_height() - 1.2 * offset)
        )
        
        pipe_x = self.config.window_width + 10
        y1 = pipe_height - y2 + offset
        
        self.pipes.append({'x': pipe_x, 'y': -y1, 'type': 'top'})
        self.pipes.append({'x': pipe_x, 'y': y2, 'type': 'bottom', 'scored': False})
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            
            if event.type == KEYDOWN:
                if event.key in self.config.get_control_keys('quit'):
                    return False
                
                if not self.game_over and event.key in self.config.get_control_keys('jump'):
                    self.bird_vel_y = self.config.bird_jump
                
                if self.game_over and event.key in self.config.get_control_keys('restart'):
                    self.reset()
        
        return True
    
    def update(self):
        if self.game_over:
            return
        
        # Физика птицы
        self.bird_vel_y += self.config.bird_gravity
        self.bird_vel_y = min(self.config.bird_max_speed, self.bird_vel_y)
        self.bird_vel_y = max(self.config.bird_min_speed, self.bird_vel_y)
        self.bird_y += self.bird_vel_y
        
        # Движение труб
        for pipe in self.pipes:
            pipe['x'] += self.config.pipe_speed
        
        # Удаление старых труб
        if self.pipes and self.pipes[0]['x'] < -self.assets.images['pipe'][0].get_width():
            self.pipes = self.pipes[2:]
        
        # Добавление новых труб
        if not self.pipes or self.pipes[-1]['x'] < self.config.window_width - self.config.pipe_spacing:
            self.add_pipe()
        
        # Столкновения
        self.game_over = self.check_collision()
        
        # Счет
        self.update_score()
    
    def check_collision(self):
        if self.bird_y < 0 or self.bird_y > self.config.elevation - 25:
            return True
        
        bird_rect = pygame.Rect(
            self.bird_x, self.bird_y,
            self.assets.images['bird'].get_width(),
            self.assets.images['bird'].get_height()
        )
        
        for pipe in self.pipes:
            pipe_img = self.assets.images['pipe'][0 if pipe['type'] == 'top' else 1]
            pipe_rect = pygame.Rect(
                pipe['x'], pipe['y'],
                pipe_img.get_width(),
                pipe_img.get_height()
            )
            
            if bird_rect.colliderect(pipe_rect):
                return True
        
        return False
    
    def update_score(self):
        bird_center_x = self.bird_x + self.assets.images['bird'].get_width() / 2
        
        for i in range(0, len(self.pipes), 2):
            pipe = self.pipes[i]
            if 'scored' in pipe and not pipe['scored']:
                pipe_img = self.assets.images['pipe'][0]
                pipe_center_x = pipe['x'] + pipe_img.get_width() / 2
                
                if pipe_center_x <= bird_center_x < pipe_center_x + 5:
                    self.score += 1
                    pipe['scored'] = True
                    break
    
    def render(self):
        self.window.blit(self.assets.images['background'], (0, 0))
        
        for pipe in self.pipes:
            img_idx = 0 if pipe['type'] == 'top' else 1
            self.window.blit(self.assets.images['pipe'][img_idx], (pipe['x'], pipe['y']))
        
        self.window.blit(self.assets.images['ground'], (0, self.config.elevation))
        self.window.blit(self.assets.images['bird'], (self.bird_x, self.bird_y))
        
        self.render_score()
        
        if self.game_over:
            self.render_game_over()
        
        pygame.display.update()
    
    def render_score(self):
        font = pygame.font.SysFont(None, 48)
        text = font.render(str(self.score), True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.config.window_width//2, 50))
        self.window.blit(text, text_rect)
    
    def render_game_over(self):
        font = pygame.font.SysFont(None, 48)
        text = font.render("GAME OVER", True, (255, 50, 50))
        text_rect = text.get_rect(center=(self.config.window_width//2, self.config.window_height//3))
        self.window.blit(text, text_rect)
    
    def run(self):
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.config.fps)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    # Можно запустить с разными конфигами:
    # game = Game()                     # Базовый конфиг
    # game = Game("graphics.yaml")      # С улучшенной графикой
    # game = Game("physics.yaml")       # С другой физикой
    # game = Game("controls.yaml")      # С другими управлениями
    
    game = Game()
    game.run()
