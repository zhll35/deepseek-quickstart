import pygame
import sys
import random
import numpy as np
from pygame.locals import *

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Game constants
BOARD_SIZE = 15
GRID_SIZE = 40
PIECE_RADIUS = 18
MARGIN = 40
WINDOW_SIZE = BOARD_SIZE * GRID_SIZE + 2 * MARGIN
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BOARD_COLOR = (220, 179, 92)
LINE_COLOR = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
HIGHLIGHT = (255, 215, 0)

# Create game window
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption('Gomoku')
clock = pygame.time.Clock()

# Sound effects (placeholder)
def play_sound(sound_type):
    pass

# Game state
class GameState:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        self.current_player = 1  # 1 for black, 2 for white
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.moves = []
    
    def make_move(self, row, col):
        if self.game_over or self.board[row][col] != 0:
            return False
        
        self.board[row][col] = self.current_player
        self.last_move = (row, col)
        self.moves.append((row, col))
        
        if self.check_win(row, col):
            self.game_over = True
            self.winner = self.current_player
        elif len(self.moves) == BOARD_SIZE * BOARD_SIZE:
            self.game_over = True  # Draw
        
        self.current_player = 3 - self.current_player  # Switch player
        return True
    
    def undo_move(self):
        if not self.moves:
            return False
        
        row, col = self.moves.pop()
        self.board[row][col] = 0
        self.current_player = 3 - self.current_player
        self.game_over = False
        self.winner = None
        
        if self.moves:
            self.last_move = self.moves[-1]
        else:
            self.last_move = None
        return True
    
    def check_win(self, row, col):
        player = self.board[row][col]
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # Horizontal, vertical, diagonal
        
        for dr, dc in directions:
            count = 1
            # Forward check
            r, c = row + dr, col + dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == player:
                count += 1
                r += dr
                c += dc
            # Backward check
            r, c = row - dr, col - dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == player:
                count += 1
                r -= dr
                c -= dc
            
            if count >= 5:
                return True
        return False

# Simple AI
class SimpleAI:
    def __init__(self, difficulty=1):
        self.difficulty = difficulty  # 1-easy, 2-medium, 3-hard
    
    def make_move(self, game_state):
        if game_state.game_over:
            return None
        
        if self.difficulty == 1:
            return self.random_move(game_state)
        elif self.difficulty == 2:
            return self.defensive_move(game_state)
        else:
            return self.offensive_move(game_state)
    
    def random_move(self, game_state):
        empty_positions = [(i, j) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE) 
                          if game_state.board[i][j] == 0]
        return random.choice(empty_positions) if empty_positions else None
    
    def defensive_move(self, game_state):
        # Basic defense: block opponent's 4-in-a-row
        opponent = 3 - game_state.current_player
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if game_state.board[i][j] == 0:
                    # Simulate opponent's move
                    game_state.board[i][j] = opponent
                    if game_state.check_win(i, j):
                        game_state.board[i][j] = 0  # Revert
                        return (i, j)
                    game_state.board[i][j] = 0  # Revert
        
        # No urgent defense needed, random move
        return self.random_move(game_state)
    
    def offensive_move(self, game_state):
        # Basic offense: try to make 4-in-a-row
        player = game_state.current_player
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if game_state.board[i][j] == 0:
                    # Simulate own move
                    game_state.board[i][j] = player
                    if game_state.check_win(i, j):
                        game_state.board[i][j] = 0  # Revert
                        return (i, j)
                    game_state.board[i][j] = 0  # Revert
        
        # Try defense
        move = self.defensive_move(game_state)
        if move:
            return move
        
        # Otherwise random move
        return self.random_move(game_state)

# Main game class
class GomokuGame:
    def __init__(self):
        self.state = GameState()
        self.ai = SimpleAI(difficulty=2)
        self.game_mode = "human_vs_human"  # "human_vs_human", "human_vs_ai"
        self.running = True
        self.animating = False
        self.animation_pos = None
        self.animation_progress = 0
        self.font = pygame.font.SysFont('Arial', 24)
    
    def reset_game(self):
        self.state.reset()
        self.animating = False
    
    def handle_click(self, pos):
        if self.animating or self.state.game_over:
            return
        
        x, y = pos
        if MARGIN <= x <= WINDOW_SIZE - MARGIN and MARGIN <= y <= WINDOW_SIZE - MARGIN:
            col = round((x - MARGIN) / GRID_SIZE)
            row = round((y - MARGIN) / GRID_SIZE)
            
            if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                if self.state.make_move(row, col):
                    play_sound("place")
                    self.animating = True
                    self.animation_pos = (row, col)
                    self.animation_progress = 0
                    
                    # AI turn
                    if self.game_mode == "human_vs_ai" and not self.state.game_over and self.state.current_player == 2:
                        ai_move = self.ai.make_move(self.state)
                        if ai_move:
                            pygame.time.set_timer(AI_MOVE_EVENT, 500)  # 0.5s delay
    
    def undo_move(self):
        if self.state.undo_move():
            play_sound("undo")
    
    def draw_board(self):
        # Draw board background
        screen.fill(BOARD_COLOR)
        
        # Draw grid lines
        for i in range(BOARD_SIZE):
            # Horizontal lines
            pygame.draw.line(screen, LINE_COLOR, 
                            (MARGIN, MARGIN + i * GRID_SIZE), 
                            (WINDOW_SIZE - MARGIN, MARGIN + i * GRID_SIZE), 2)
            # Vertical lines
            pygame.draw.line(screen, LINE_COLOR, 
                            (MARGIN + i * GRID_SIZE, MARGIN), 
                            (MARGIN + i * GRID_SIZE, WINDOW_SIZE - MARGIN), 2)
        
        # Draw star points
        star_points = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
        for row, col in star_points:
            center = (MARGIN + col * GRID_SIZE, MARGIN + row * GRID_SIZE)
            pygame.draw.circle(screen, BLACK, center, 5)
        
        # Draw pieces
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                center = (MARGIN + col * GRID_SIZE, MARGIN + row * GRID_SIZE)
                if self.state.board[row][col] == 1:  # Black
                    pygame.draw.circle(screen, BLACK, center, PIECE_RADIUS)
                elif self.state.board[row][col] == 2:  # White
                    pygame.draw.circle(screen, WHITE, center, PIECE_RADIUS)
                    pygame.draw.circle(screen, BLACK, center, PIECE_RADIUS, 1)
        
        # Draw last move marker
        if self.state.last_move:
            row, col = self.state.last_move
            center = (MARGIN + col * GRID_SIZE, MARGIN + row * GRID_SIZE)
            pygame.draw.circle(screen, RED, center, 5)
        
        # Draw animated piece
        if self.animating and self.animation_pos:
            row, col = self.animation_pos
            center = (MARGIN + col * GRID_SIZE, MARGIN + row * GRID_SIZE)
            progress = min(self.animation_progress / 10, 1.0)
            
            # Bounce animation
            bounce_offset = -20 * (1 - (2 * progress - 1)**2)
            animated_center = (center[0], center[1] + bounce_offset)
            
            # Fade-in effect
            alpha = int(255 * progress)
            
            player = self.state.board[row][col]
            if player == 1:  # Black
                s = pygame.Surface((PIECE_RADIUS*2, PIECE_RADIUS*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*BLACK, alpha), (PIECE_RADIUS, PIECE_RADIUS), PIECE_RADIUS)
                screen.blit(s, (animated_center[0] - PIECE_RADIUS, animated_center[1] - PIECE_RADIUS))
            elif player == 2:  # White
                s = pygame.Surface((PIECE_RADIUS*2, PIECE_RADIUS*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*WHITE, alpha), (PIECE_RADIUS, PIECE_RADIUS), PIECE_RADIUS)
                pygame.draw.circle(s, (*BLACK, alpha), (PIECE_RADIUS, PIECE_RADIUS), PIECE_RADIUS, 1)
                screen.blit(s, (animated_center[0] - PIECE_RADIUS, animated_center[1] - PIECE_RADIUS))
            
            self.animation_progress += 1
            if progress >= 1.0:
                self.animating = False
        
        # Draw game status
        status_text = ""
        if self.state.game_over:
            if self.state.winner == 1:
                status_text = "Black wins!"
            elif self.state.winner == 2:
                status_text = "White wins!"
            else:
                status_text = "Draw!"
        else:
            status_text = "Current turn: " + ("Black" if self.state.current_player == 1 else "White")
        
        text_surface = self.font.render(status_text, True, BLACK)
        screen.blit(text_surface, (20, 10))
        
        # Draw buttons
        pygame.draw.rect(screen, GRAY, (WINDOW_SIZE - 120, 10, 110, 30))
        reset_text = self.font.render("Restart", True, BLACK)
        screen.blit(reset_text, (WINDOW_SIZE - 110, 15))
        
        if len(self.state.moves) > 0:
            pygame.draw.rect(screen, GRAY, (WINDOW_SIZE - 120, 50, 110, 30))
            undo_text = self.font.render("Undo", True, BLACK)
            screen.blit(undo_text, (WINDOW_SIZE - 110, 55))
    
    def handle_ai_move(self):
        ai_move = self.ai.make_move(self.state)
        if ai_move:
            row, col = ai_move
            if self.state.make_move(row, col):
                play_sound("place")
                self.animating = True
                self.animation_pos = (row, col)
                self.animation_progress = 0
    
    def run(self):
        global AI_MOVE_EVENT
        AI_MOVE_EVENT = pygame.USEREVENT + 1
        
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        # Check restart button
                        if WINDOW_SIZE - 120 <= event.pos[0] <= WINDOW_SIZE - 10 and 10 <= event.pos[1] <= 40:
                            self.reset_game()
                        # Check undo button
                        elif len(self.state.moves) > 0 and WINDOW_SIZE - 120 <= event.pos[0] <= WINDOW_SIZE - 10 and 50 <= event.pos[1] <= 80:
                            self.undo_move()
                        else:
                            self.handle_click(event.pos)
                elif event.type == AI_MOVE_EVENT:
                    pygame.time.set_timer(AI_MOVE_EVENT, 0)  # Stop timer
                    self.handle_ai_move()
                elif event.type == KEYDOWN:
                    if event.key == K_r:  # R to restart
                        self.reset_game()
                    elif event.key == K_u and len(self.state.moves) > 0:  # U to undo
                        self.undo_move()
                    elif event.key == K_1:  # Switch game mode
                        self.game_mode = "human_vs_human"
                        self.reset_game()
                    elif event.key == K_2:
                        self.game_mode = "human_vs_ai"
                        self.reset_game()
            
            self.draw_board()
            pygame.display.flip()
            clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# Start game
if __name__ == "__main__":
    game = GomokuGame()
    game.run()