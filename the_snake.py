import random
import pygame
from typing import Tuple, List

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

BOARD_BACKGROUND_COLOR = (0, 0, 0)
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
    """Класс, описывающий яблоко в игре."""

    def __init__(self) -> None:
        """Создаёт яблоко с фиксированным цветом и случайной позицией."""
        super().__init__(position=(0, 0), body_color=(255, 0, 0))
        self.randomize_position()

    def randomize_position(self) -> None:
        """Устанавливает случайную позицию яблока в пределах поля."""
        self.position = (
            random.randrange(0, GRID_WIDTH) * GRID_SIZE,
            random.randrange(0, GRID_HEIGHT) * GRID_SIZE,
        )

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает яблоко как цветной квадрат."""
        x, y = self.position
        rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, self.body_color, rect)


class Snake(GameObject):
    """Класс, описывающий змею в игре."""

    def __init__(self) -> None:
        """Создаёт змею с начальной позицией и направлением."""
        start_x = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2
        self.positions: List[Tuple[int, int]] = [(start_x, start_y)]
        self.direction = RIGHT
        self._body_color = (0, 255, 0)
        self.position = self.positions[0]

    @property
    def body_color(self) -> Tuple[int, int, int]:
        """Возвращает цвет тела змеи."""
        return self._body_color

    @body_color.setter
    def body_color(self, value: Tuple[int, int, int]) -> None:
        """Заглушка: цвет змеи фиксированный."""
        pass

    def get_head_position(self) -> Tuple[int, int]:
        """Возвращает позицию головы змеи."""
        return self.positions[0]

    def move(self) -> None:
        """Сдвигает змею на одну клетку в текущем направлении."""
        head = self.get_head_position()
        new_head = (
            head[0] + self.direction[0],
            head[1] + self.direction[1],
        )
        self.positions.insert(0, new_head)
        self.positions.pop()
        self.position = self.positions[0]

    def grow(self) -> None:
        """Увеличивает длину змеи на одну клетку."""
        tail = self.positions[-1]
        self.positions.append(tail)

    def reset(self) -> None:
        """Сбрасывает змею в начальное состояние."""
        start_x = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2
        self.positions = [(start_x, start_y)]
        self.direction = RIGHT
        self.position = self.positions[0]

    def check_self_collision(self) -> bool:
        """Проверяет, не столкнулась ли змея сама с собой."""
        head = self.get_head_position()
        return head in self.positions[1:]

    def update_direction(self) -> None:
        """Заглушка."""
        pass

    def set_direction(
        self,
        direction: Tuple[int, int]
    ) -> None:
        """Устанавливает направление, если оно не противоположно текущему."""
        opposite = (-self.direction[0], -self.direction[1])
        if direction != opposite:
            self.direction = direction

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает змею как набор цветных квадратов."""
        for x, y in self.positions:
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, self._body_color, rect)


def handle_keys(snake: Snake) -> None:
    """Обрабатывает нажатия клавиш и меняет направление змеи."""
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
    """Запускает игровой цикл."""
    global screen
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Изгиб Питона')

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
