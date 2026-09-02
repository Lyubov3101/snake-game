import random
import pygame
from typing import Tuple, Optional

# Константы экрана и сетки
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
BOARD_BACKGROUND_COLOR = (0, 0, 0)
FPS = 20

# Направления
UP = (0, -GRID_SIZE)
DOWN = (0, GRID_SIZE)
LEFT = (-GRID_SIZE, 0)
RIGHT = (GRID_SIZE, 0)

# Глобальные объекты pygame (создаются до main() для тестов)
screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(
        self,
        position: Tuple[int, int] = (0, 0),
        body_color: Tuple[int, int, int] = (255, 255, 255)
    ) -> None:
        """Инициализирует игровой объект с позицией и цветом.

        :param position: Кортеж координат (x, y).
        :param body_color: Цвет объекта в формате RGB.
        """
        self.position = position
        self.body_color = body_color

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает объект на поверхности.

        Должен быть переопределён в дочерних классах.
        """
        pass


class Apple(GameObject):
    """Класс яблока, которое ест змейка."""

    def __init__(self) -> None:
        """Инициализирует яблоко красного цвета и размещает его случайно."""
        super().__init__((0, 0), (255, 0, 0))
        self.randomize_position()

    def randomize_position(self) -> None:
        """Устанавливает случайную позицию яблока в пределах сетки."""
        x = random.randint(0, GRID_WIDTH - 1) * GRID_SIZE
        y = random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (x, y)

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает яблоко в виде закрашенного квадрата."""
        rect = pygame.Rect(
            self.position[0],
            self.position[1],
            GRID_SIZE,
            GRID_SIZE
        )
        pygame.draw.rect(surface, self.body_color, rect)


class Snake(GameObject):
    """Класс змейки, отвечающий за движение, рост и столкновения."""

    def __init__(self) -> None:
        """Инициализирует начальное состояние змейки."""
        start_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        super().__init__(start_pos, (0, 255, 0))

        self.length = 1
        self.positions = [start_pos]
        self.direction = RIGHT
        self.next_direction: Optional[Tuple[int, int]] = None
        self.last: Optional[Tuple[int, int]] = None

    def get_head_position(self) -> Tuple[int, int]:
        """Возвращает текущие координаты головы змейки."""
        return self.positions[0]

    def update_direction(self) -> None:
        """Применяет новое направление, если оно не противоположно.

        Запрещает разворот на 180 градусов.
        """
        if self.next_direction is None:
            return

        dx_sum = self.direction[0] + self.next_direction[0]
        dy_sum = self.direction[1] + self.next_direction[1]

        if not (dx_sum == 0 and dy_sum == 0):
            self.direction = self.next_direction

        self.next_direction = None

    def move(self) -> None:
        """Обновляет позицию: добавляет голову, удаляет хвост.

        Если длина не увеличилась, последний сегмент удаляется.
        """
        cur_head = self.get_head_position()
        new_x = (cur_head[0] + self.direction[0]) % SCREEN_WIDTH
        new_y = (cur_head[1] + self.direction[1]) % SCREEN_HEIGHT
        new_head = (new_x, new_y)

        self.last = self.positions[-1] if self.positions else None

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.positions.pop()

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние после проигрыша."""
        start_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [start_pos]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def check_self_collision(self) -> bool:
        """Проверяет столкновение головы с телом змейки."""
        head = self.get_head_position()
        return head in self.positions[1:]

    def grow(self) -> None:
        """Увеличивает длину змейки на один сегмент."""
        self.length += 1

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает все сегменты змейки и очищает след."""
        if self.last is not None:
            clean_rect = pygame.Rect(
                self.last[0],
                self.last[1],
                GRID_SIZE,
                GRID_SIZE
            )
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, clean_rect)

        for pos in self.positions:
            segment_rect = pygame.Rect(
                pos[0], pos[1], GRID_SIZE, GRID_SIZE
            )
            pygame.draw.rect(surface, self.body_color, segment_rect)


def handle_keys(snake: Snake) -> None:
    """Обрабатывает нажатия клавиш для изменения направления змейки."""
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        snake.next_direction = UP
    elif keys[pygame.K_DOWN]:
        snake.next_direction = DOWN
    elif keys[pygame.K_LEFT]:
        snake.next_direction = LEFT
    elif keys[pygame.K_RIGHT]:
        snake.next_direction = RIGHT


def main() -> None:
    """Основной игровой цикл приложения."""
    global screen, clock

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
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

        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw(screen)
        apple.draw(screen)

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()


if __name__ == '__main__':
    main()
