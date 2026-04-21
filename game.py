"""
Enhanced Snake Game using Pygame with Levels & Obstacles
Controls:
- Arrow Keys or WASD to move the snake
- Press SPACE to pause/resume
- Press Q to quit
- Press R to restart/next level
"""

import pygame
import random
import sys
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Directions
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

# Game Levels
class GameLevel:
    def __init__(self, level_num):
        self.level = level_num
        self.obstacles = set()
        self.num_foods = 1
        self.base_speed = 8 + level_num
        self.score_multiplier = 1 + (level_num * 0.5)
        self.setup_level()

    def setup_level(self):
        """Setup obstacles based on level"""
        if self.level == 1:
            # Level 1: No obstacles
            self.obstacles = set()
        elif self.level == 2:
            # Level 2: Border obstacles
            self.add_border_obstacles()
        elif self.level == 3:
            # Level 3: Vertical lines
            self.add_vertical_obstacles()
        elif self.level == 4:
            # Level 4: Horizontal lines + random
            self.add_horizontal_obstacles()
            self.add_random_obstacles(5)
        else:
            # Level 5+: Heavy obstacles
            self.add_complex_obstacles()

    def add_border_obstacles(self):
        """Add obstacles around the border"""
        for x in range(GRID_WIDTH):
            if x % 2 == 0:
                self.obstacles.add((x, 2))
                self.obstacles.add((x, GRID_HEIGHT - 3))

    def add_vertical_obstacles(self):
        """Add vertical line obstacles"""
        for y in range(5, GRID_HEIGHT - 5):
            if y % 3 == 0:
                self.obstacles.add((GRID_WIDTH // 3, y))
                self.obstacles.add((2 * GRID_WIDTH // 3, y))

    def add_horizontal_obstacles(self):
        """Add horizontal line obstacles"""
        for x in range(5, GRID_WIDTH - 5):
            if x % 3 == 0:
                self.obstacles.add((x, GRID_HEIGHT // 3))
                self.obstacles.add((x, 2 * GRID_HEIGHT // 3))

    def add_random_obstacles(self, count):
        """Add random obstacles"""
        for _ in range(count):
            while True:
                x = random.randint(3, GRID_WIDTH - 4)
                y = random.randint(3, GRID_HEIGHT - 4)
                if (x, y) not in self.obstacles:
                    self.obstacles.add((x, y))
                    break

    def add_complex_obstacles(self):
        """Complex obstacle pattern for higher levels"""
        # Diagonal pattern
        for i in range(0, min(GRID_WIDTH, GRID_HEIGHT), 2):
            self.obstacles.add((i, i))

        # Random scattered
        self.add_random_obstacles(8)

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game - Enhanced with Levels")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.current_level = 1
        self.total_score = 0
        self.reset_game()

    def reset_game(self):
        """Initialize/reset the game state for current level"""
        self.level_data = GameLevel(self.current_level)
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.foods = []
        for _ in range(self.level_data.num_foods):
            self.foods.append(self.spawn_food())
        self.level_score = 0
        self.game_over = False
        self.level_complete = False
        self.paused = False
        self.speed = self.level_data.base_speed

    def spawn_food(self):
        """Randomly place food on the grid avoiding obstacles and snake"""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if ((x, y) not in self.snake and
                (x, y) not in self.level_data.obstacles and
                (x, y) not in self.foods):
                return (x, y)

    def handle_events(self):
        """Handle user input and window events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False

                # Pause/Resume
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused

                # Movement controls
                if event.key in (pygame.K_UP, pygame.K_w):
                    if self.direction != Direction.DOWN:
                        self.next_direction = Direction.UP
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if self.direction != Direction.UP:
                        self.next_direction = Direction.DOWN
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if self.direction != Direction.RIGHT:
                        self.next_direction = Direction.LEFT
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if self.direction != Direction.LEFT:
                        self.next_direction = Direction.RIGHT

                # Restart/Next level
                if event.key == pygame.K_r:
                    if self.game_over:
                        self.current_level = 1
                        self.total_score = 0
                        self.reset_game()
                    elif self.level_complete:
                        self.current_level += 1
                        self.reset_game()

        return True

    def update(self):
        """Update game logic"""
        if self.paused or self.game_over or self.level_complete:
            return

        self.direction = self.next_direction

        # Calculate new head position
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)

        # Check wall collision
        if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
            self.game_over = True
            return

        # Check obstacle collision
        if new_head in self.level_data.obstacles:
            self.game_over = True
            return

        # Check self collision
        if new_head in self.snake:
            self.game_over = True
            return

        # Add new head
        self.snake.insert(0, new_head)

        # Check food collision
        food_eaten = False
        for food in self.foods:
            if new_head == food:
                food_eaten = True
                self.foods.remove(food)
                points = int(10 * self.level_data.score_multiplier)
                self.level_score += points
                self.total_score += points
                self.foods.append(self.spawn_food())
                break

        if not food_eaten:
            # Remove tail if no food eaten
            self.snake.pop()

        # Check level completion (score threshold)
        if self.level_score >= 100 * self.current_level:
            self.level_complete = True

    def draw(self):
        """Draw the game on screen"""
        self.screen.fill(BLACK)

        # Draw grid
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WINDOW_WIDTH, y), 1)

        # Draw obstacles
        for ox, oy in self.level_data.obstacles:
            pygame.draw.rect(self.screen, PURPLE,
                           (ox * GRID_SIZE + 1, oy * GRID_SIZE + 1,
                            GRID_SIZE - 2, GRID_SIZE - 2))

        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            color = GREEN if i == 0 else DARK_GREEN
            pygame.draw.rect(self.screen, color,
                           (x * GRID_SIZE + 1, y * GRID_SIZE + 1,
                            GRID_SIZE - 2, GRID_SIZE - 2))

        # Draw food
        for i, (fx, fy) in enumerate(self.foods):
            color = RED if i == 0 else ORANGE
            pygame.draw.circle(self.screen, color,
                             (fx * GRID_SIZE + GRID_SIZE // 2,
                              fy * GRID_SIZE + GRID_SIZE // 2),
                             GRID_SIZE // 2 - 2)

        # Draw HUD
        self.draw_hud()

        # Draw paused message
        if self.paused:
            paused_text = self.font.render("PAUSED (Press SPACE to resume)", True, YELLOW)
            text_rect = paused_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(paused_text, text_rect)

        # Draw game over message
        if self.game_over:
            game_over_text = self.font.render("GAME OVER!", True, RED)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
            self.screen.blit(game_over_text, text_rect)

            score_text = self.small_font.render(f"Level Score: {self.level_score} | Total Score: {self.total_score}", True, WHITE)
            score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(score_text, score_rect)

            restart_text = self.small_font.render("Press R to restart or Q to quit", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
            self.screen.blit(restart_text, restart_rect)

        # Draw level complete message
        if self.level_complete:
            complete_text = self.font.render("LEVEL COMPLETE!", True, CYAN)
            text_rect = complete_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
            self.screen.blit(complete_text, text_rect)

            score_text = self.small_font.render(f"Score: {self.level_score} | Total: {self.total_score}", True, WHITE)
            score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(score_text, score_rect)

            next_text = self.small_font.render(f"Press R for Level {self.current_level + 1}", True, WHITE)
            next_rect = next_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
            self.screen.blit(next_text, next_rect)

        pygame.display.flip()

    def draw_hud(self):
        """Draw heads-up display with score and level info"""
        # Level
        level_text = self.font.render(f"Level: {self.current_level}", True, CYAN)
        self.screen.blit(level_text, (10, 10))

        # Level score
        level_score_text = self.small_font.render(f"Level Score: {self.level_score}", True, GREEN)
        self.screen.blit(level_score_text, (10, 50))

        # Total score
        total_score_text = self.small_font.render(f"Total Score: {self.total_score}", True, YELLOW)
        self.screen.blit(total_score_text, (10, 75))

        # Speed
        speed_text = self.small_font.render(f"Speed: {self.speed}", True, WHITE)
        self.screen.blit(speed_text, (10, 100))

        # Level progress
        progress_text = self.small_font.render(f"Goal: {100 * self.current_level} pts", True, GRAY)
        self.screen.blit(progress_text, (10, 125))

        # Snake length
        length_text = self.small_font.render(f"Length: {len(self.snake)}", True, WHITE)
        self.screen.blit(length_text, (WINDOW_WIDTH - 150, 10))

    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.speed)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()