import pygame
import random
import sys

pygame.init()

CELL_SIZE = 120
GRID_SIZE = 4
WIDTH = CELL_SIZE * GRID_SIZE
HEIGHT = CELL_SIZE * GRID_SIZE + 80

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (80, 180, 80)
RED = (220, 70, 70)
BLUE = (80, 120, 220)
GOLD = (240, 190, 40)
PURPLE = (160, 80, 180)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Intelligent Wumpus World")

font = pygame.font.SysFont("arial", 24)
small_font = pygame.font.SysFont("arial", 18)


class Cell:
    def __init__(self):
        self.has_wumpus = False
        self.has_pit = False
        self.has_gold = False
        self.visited = False
        self.percepts = []


class World:
    def __init__(self):
        self.grid = [[Cell() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.generate_world()
        self.generate_percepts()

    def generate_world(self):
        positions = []

        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if not (row == 0 and col == 0):
                    positions.append((row, col))

        wumpus_pos = random.choice(positions)
        self.grid[wumpus_pos[0]][wumpus_pos[1]].has_wumpus = True
        positions.remove(wumpus_pos)

        gold_pos = random.choice(positions)
        self.grid[gold_pos[0]][gold_pos[1]].has_gold = True
        positions.remove(gold_pos)

        for _ in range(3):
            pit_pos = random.choice(positions)
            self.grid[pit_pos[0]][pit_pos[1]].has_pit = True
            positions.remove(pit_pos)

    def get_neighbors(self, row, col):
        neighbors = []

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc

            if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
                neighbors.append((new_row, new_col))

        return neighbors

    def generate_percepts(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                cell = self.grid[row][col]

                if cell.has_gold:
                    cell.percepts.append("Glitter")

                for nr, nc in self.get_neighbors(row, col):
                    neighbor = self.grid[nr][nc]

                    if neighbor.has_pit and "Breeze" not in cell.percepts:
                        cell.percepts.append("Breeze")

                    if neighbor.has_wumpus and "Stench" not in cell.percepts:
                        cell.percepts.append("Stench")


class Agent:
    def __init__(self):
        self.row = 0
        self.col = 0
        self.score = 100
        self.alive = True
        self.has_gold = False
        self.knowledge = set()
        self.safe_cells = {(0, 0)}

    def move(self, direction, world):
        if not self.alive or self.has_gold:
            return

        new_row = self.row
        new_col = self.col

        if direction == "UP":
            new_row -= 1
        elif direction == "DOWN":
            new_row += 1
        elif direction == "LEFT":
            new_col -= 1
        elif direction == "RIGHT":
            new_col += 1

        if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
            self.row = new_row
            self.col = new_col
            self.score -= 1
            self.update_knowledge(world)
            self.check_current_cell(world)

    def update_knowledge(self, world):
        current_cell = world.grid[self.row][self.col]
        current_cell.visited = True

        self.knowledge.add((self.row, self.col))

        if len(current_cell.percepts) == 0:
            for neighbor in world.get_neighbors(self.row, self.col):
                self.safe_cells.add(neighbor)

    def decide_action(self, world):
        current_cell = world.grid[self.row][self.col]

        if "Glitter" in current_cell.percepts:
            return "Grab Gold"

        if "Breeze" in current_cell.percepts or "Stench" in current_cell.percepts:
            return "Danger Nearby"

        return "Cell Seems Safe"

    def check_current_cell(self, world):
        current_cell = world.grid[self.row][self.col]

        if current_cell.has_pit:
            self.alive = False
            self.score -= 50

        elif current_cell.has_wumpus:
            self.alive = False
            self.score -= 50

        elif current_cell.has_gold:
            self.has_gold = True
            self.score += 100


class Game:
    def __init__(self):
        self.world = World()
        self.agent = Agent()
        self.agent.update_knowledge(self.world)
        self.running = True

    def draw_grid(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                cell = self.world.grid[row][col]

                if cell.visited:
                    pygame.draw.rect(screen, WHITE, rect)
                else:
                    pygame.draw.rect(screen, GRAY, rect)

                pygame.draw.rect(screen, BLACK, rect, 2)

                if cell.visited:
                    center_x = col * CELL_SIZE + CELL_SIZE // 2
                    center_y = row * CELL_SIZE + CELL_SIZE // 2

                    if cell.has_pit:
                        pygame.draw.circle(screen, BLACK, (center_x, center_y), 22)
                        text = small_font.render("Pit", True, WHITE)
                        screen.blit(text, (center_x - 12, center_y - 10))

                    if cell.has_wumpus:
                        pygame.draw.circle(screen, RED, (center_x, center_y), 28)
                        text = small_font.render("W", True, WHITE)
                        screen.blit(text, (center_x - 8, center_y - 10))

                    if cell.has_gold:
                        pygame.draw.circle(screen, GOLD, (center_x, center_y), 22)
                        text = small_font.render("Gold", True, BLACK)
                        screen.blit(text, (center_x - 18, center_y - 10))

                    percept_text = ", ".join(cell.percepts)
                    if percept_text:
                        text = small_font.render(percept_text, True, PURPLE)
                        screen.blit(text, (col * CELL_SIZE + 5, row * CELL_SIZE + 5))

    def draw_agent(self):
        x = self.agent.col * CELL_SIZE + CELL_SIZE // 2
        y = self.agent.row * CELL_SIZE + CELL_SIZE // 2

        pygame.draw.circle(screen, BLUE, (x, y), 25)
        text = small_font.render("A", True, WHITE)
        screen.blit(text, (x - 6, y - 10))

    def draw_status(self):
        pygame.draw.rect(screen, WHITE, (0, WIDTH, WIDTH, 80))

        current_cell = self.world.grid[self.agent.row][self.agent.col]
        percepts = ", ".join(current_cell.percepts)

        if percepts == "":
            percepts = "None"

        action = self.agent.decide_action(self.world)

        status = f"Score: {self.agent.score} | Percepts: {percepts} | AI: {action}"
        text = small_font.render(status, True, BLACK)
        screen.blit(text, (10, WIDTH + 10))

        controls = "Use Arrow Keys to Move | R to Restart | ESC to Quit"
        controls_text = small_font.render(controls, True, BLACK)
        screen.blit(controls_text, (10, WIDTH + 40))

        if not self.agent.alive:
            game_over = font.render("Game Over! Agent died.", True, RED)
            screen.blit(game_over, (110, 210))

        if self.agent.has_gold:
            win_text = font.render("You Win! Gold Found.", True, GREEN)
            screen.blit(win_text, (120, 210))

    def restart_game(self):
        self.world = World()
        self.agent = Agent()
        self.agent.update_knowledge(self.world)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif event.key == pygame.K_r:
                    self.restart_game()

                elif event.key == pygame.K_UP:
                    self.agent.move("UP", self.world)

                elif event.key == pygame.K_DOWN:
                    self.agent.move("DOWN", self.world)

                elif event.key == pygame.K_LEFT:
                    self.agent.move("LEFT", self.world)

                elif event.key == pygame.K_RIGHT:
                    self.agent.move("RIGHT", self.world)

    def draw(self):
        screen.fill(WHITE)
        self.draw_grid()
        self.draw_agent()
        self.draw_status()
        pygame.display.update()

    def run(self):
        clock = pygame.time.Clock()

        while self.running:
            self.handle_events()
            self.draw()
            clock.tick(60)

        pygame.quit()
        sys.exit()


game = Game()
game.run()