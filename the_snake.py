import random
import pygame
from typing import Tuple

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
FPS = 20

UP = (0, -GRID_SIZE)
DOWN = (0, GRID_SIZE)
LEFT = (-GRID_SIZE, 0)
RIGHT = (GRID_SIZE, 0)

screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(
        self,
        position: Tuple[int, int] = (0, 0),
        body_color: Tuple[int, int, int] = (255, 255, 255)
    ) -> None:
        """Инициализирует объект позицией и цветом."""
        self.position = position
        self.body_color = body_color

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает объект на поверхности."""
        pass


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self) -> None:
        """Создаёт яблоко и ставит его в случайную позицию."""
        super().__init__((0, 0), (255, 0, 0))
        self.randomize_position()

    def randomize_position(self) -> None:
        """Ставит яблоко в случайную клетку сетки."""
        x = random.randint(0, GRID_WIDTH - 1) * GRID_SIZE
        y = random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (x, y)

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает яблоко с рамкой."""
        rect = pygame.Rect(
            self.position[0],
            self.position[1],
            GRID_SIZE,
            GRID_SIZE
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс змейки. Логика движения и поворота."""

    def __init__(self) -> None:
        """Создаёт змейку в центре экрана."""
        start_pos = (
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2
        )
        super().__init__(start_pos, (0, 255, 0))
        self.length = 1
        self.positions = [start_pos]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self) -> Tuple[int, int]:
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def set_direction(
        self,
        direction: Tuple[int, int]
    ) -> None:
        """Устанавливает направление. Разворот на 180 запрещён."""
        dx_sum = self.direction[0] + direction[0]
        dy_sum = self.direction[1] + direction[1]
        if not (dx_sum == 0 and dy_sum == 0):
            self.next_direction = direction

    def update_direction(self) -> None:
        """Применяет сохранённое направление."""
        if self.next_direction is None:
            return
        self.direction = self.next_direction
        self.next_direction = None

    def move(self) -> None:
        """Делает шаг: двигает голову, убирает хвост."""
        cur_head = self.get_head_position()
        new_x = (
            (cur_head[0] + self.direction[0]) % SCREEN_WIDTH
        )
        new_y = (
            (cur_head[1] + self.direction[1]) % SCREEN_HEIGHT
        )
        new_head = (new_x, new_y)
        self.last = self.positions[-1] if self.positions else None
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        start_pos = (
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2
        )
        self.positions = [start_pos]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def check_self_collision(self) -> bool:
        """Проверяет столкновение головы с телом."""
        head = self.get_head_position()
        return head in self.positions[1:]

    def grow(self) -> None:
        """Увеличивает длину на 1 сегмент."""
        self.length += 1

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает все сегменты змейки с рамкой."""
        for pos in self.positions:
            rect = pygame.Rect(
                pos[0],
                pos[1],
                GRID_SIZE,
                GRID_SIZE
            )
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


def handle_keys(snake: Snake) -> None:
    """Обработка нажатий клавиш для управления змейкой."""
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        snake.set_direction(UP)
    elif keys[pygame.K_DOWN]:
        snake.set_direction(DOWN)
    elif keys[pygame.K_LEFT]:
        snake.set_direction(LEFT)
    elif keys[pygame.K_RIGHT]:
        snake.set_direction(RIGHT)


def main() -> None:
    """Основной игровой цикл."""
    global screen, clock
    pygame.init()
    screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )
    pygame.display.set_caption('Изгиб Питона')
    clock = pygame.time.Clock()
    snake = Snake()
    apple = Apple()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        if snake.get_head_position() == apple.position:
            snake.grow()
            while True:
                apple.randomize_position()
                if apple.position not in snake.positions:
                    break
        if snake.check_self_collision():
            snake.reset()
        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw(screen)
        apple.draw(screen)
        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()


if __name__ == '__main__':
    main()
