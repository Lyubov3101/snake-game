from random import randint
import pygame
from typing import Optional, Tuple, List


# --- Константы ---
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
SPEED = 20

screen = pygame.Surface((1, 1))
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс игрового объекта."""

    def __init__(
        self,
        position: Optional[Tuple[int, int]] = None,
        body_color: Optional[Tuple[int, int, int]] = None,
    ) -> None:
        self.position = position
        self.body_color = body_color

    def draw(self, surface: pygame.Surface) -> None:
        pass

    @staticmethod
    def draw_cell(
        surface: pygame.Surface,
        position: Tuple[int, int],
        color: Optional[Tuple[int, int, int]],
    ) -> None:
        """Отрисовывает одну клетку игрового поля с рамкой."""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс яблока в игре «Змейка»."""

    def __init__(
        self,
        position: Optional[Tuple[int, int]] = None,
        body_color: Tuple[int, int, int] = APPLE_COLOR,
    ) -> None:
        super().__init__(position, body_color)
        if position is None:
            self.randomize_position()

    def randomize_position(self) -> None:
        """Размещает яблоко в случайной клетке сетки."""
        x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (x, y)

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает яблоко на поверхности."""
        if self.position:
            GameObject.draw_cell(surface, self.position, self.body_color)


class Snake(GameObject):
    """Класс змейки в игре."""

    def __init__(
        self,
        position: Optional[Tuple[int, int]] = None,
        body_color: Tuple[int, int, int] = SNAKE_COLOR,
    ) -> None:
        start_x = (GRID_WIDTH // 2) * GRID_SIZE
        start_y = (GRID_HEIGHT // 2) * GRID_SIZE
        default_position = position if position else (start_x, start_y)

        super().__init__(default_position, body_color)

        self.length: int = 1
        self.positions: List[Tuple[int, int]] = [self.position]
        self.direction: Tuple[int, int] = RIGHT
        self.next_direction: Optional[Tuple[int, int]] = None

    @property
    def get_head_position(self) -> Tuple[int, int]:
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def update_direction(self, new_direction: Tuple[int, int]) -> None:
        """Обновляет направление движения змейки, если оно не противоположно текущему."""
        opposite = (self.direction[0] * -1, self.direction[1] * -1)
        if new_direction != opposite:
            self.next_direction = new_direction

    def move(self) -> None:
        """Двигает змейку: обновляет позицию головы и сдвигает хвост."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

        cur_head = self.positions[0]
        x, y = self.direction
        new_head = (
            (cur_head[0] + (x * GRID_SIZE)) % SCREEN_WIDTH,
            (cur_head[1] + (y * GRID_SIZE)) % SCREEN_HEIGHT,
        )

        if len(self.positions) > 2 and new_head in self.positions[2:]:
            self.reset()
        else:
            self.positions.insert(0, new_head)
            if len(self.positions) > self.length:
                self.positions.pop()

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает тело и голову змейки на поверхности."""
        for i, position in enumerate(self.positions):
            color = SNAKE_COLOR if i == 0 else self.body_color
            GameObject.draw_cell(surface, position, color)

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние (одна клетка, направление вправо)."""
        start_x = (GRID_WIDTH // 2) * GRID_SIZE
        start_y = (GRID_HEIGHT // 2) * GRID_SIZE

        self.length = 1
        self.positions = [(start_x, start_y)]
        self.position = (start_x, start_y)
        self.direction = RIGHT
        self.next_direction = None


def handle_keys(snake: Snake) -> None:
    """Обрабатывает события клавиатуры и обновляет направление змейки."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                snake.update_direction(UP)
            elif event.key == pygame.K_DOWN:
                snake.update_direction(DOWN)
            elif event.key == pygame.K_LEFT:
                snake.update_direction(LEFT)
            elif event.key == pygame.K_RIGHT:
                snake.update_direction(RIGHT)


def main() -> None:
    """Запускает игру «Змейка»: инициализирует окно, игровой цикл и обработку событий."""
    global screen, clock

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
    pygame.display.set_caption("Змейка")
    clock = pygame.time.Clock()

    snake = Snake()
    apple = Apple()

    running = True
    while running:
        try:
            handle_keys(snake)
        except SystemExit:
            running = False
            continue

        snake.move()

        if snake.get_head_position == apple.position:
            snake.length += 1
            apple.randomize_position()
            while apple.position in snake.positions:
                apple.randomize_position()

        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw(screen)
        apple.draw(screen)

        pygame.display.update()
        clock.tick(SPEED)

    pygame.quit()


if __name__ == "__main__":
    main()
