from random import randint
import pygame

# --- КОНСТАНТЫ ---
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

# --- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ (для тестов) ---
# Инициализируем pygame сразу при импорте модуля, чтобы screen и clock
# были корректных типов к моменту проверки тестами.
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
clock = pygame.time.Clock()


# --- КЛАССЫ ---

class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self):
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = (0, 0, 0)

    def draw(self, surface):
        """Заглушка отрисовки."""
        pass


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self):
        super().__init__()
        self.body_color = APPLE_COLOR
        self.randomize_position()

    def randomize_position(self):
        """Генерирует случайную позицию строго по сетке."""
        x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (x, y)

    def draw(self, surface):
        """Отрисовывает яблоко как квадрат размером в одну клетку."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self):
        # Не вызываем super().__init__(), чтобы избежать конфликта с property position
        self.body_color = SNAKE_COLOR

        start_x = (SCREEN_WIDTH // 2) // GRID_SIZE * GRID_SIZE
        start_y = (SCREEN_HEIGHT // 2) // GRID_SIZE * GRID_SIZE

        self.positions = [(start_x, start_y)]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.last = None  # Координаты последнего сегмента для очистки

    @property
    def position(self):
        """Позиция головы змейки (первый элемент списка)."""
        return self.positions[0]

    def get_head_position(self):
        """Явный метод для получения позиции головы."""
        return self.position

    def move(self):
        """Обновляет положение змейки согласно текущему направлению."""
        self.update_direction()

        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction

        new_head_x = head_x + dir_x * GRID_SIZE
        new_head_y = head_y + dir_y * GRID_SIZE

        # Проход сквозь стены
        new_head = (
            new_head_x % SCREEN_WIDTH,
            new_head_y % SCREEN_HEIGHT
        )

        self.last = self.positions[-1]
        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.positions.pop()

    def reset(self):
        """Сбрасывает состояние змейки в начальное."""
        start_x = (SCREEN_WIDTH // 2) // GRID_SIZE * GRID_SIZE
        start_y = (SCREEN_HEIGHT // 2) // GRID_SIZE * GRID_SIZE

        self.positions = [(start_x, start_y)]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Применяет следующее направление движения."""
        if self.next_direction is not None:
            self.direction = self.next_direction
            self.next_direction = None

    def check_self_collision(self):
        """Проверяет столкновение головы змейки с её собственным телом."""
        head = self.get_head_position()
        for segment in self.positions[1:]:
            if head == segment:
                return True
        return False

    def eat_apple(self):
        """Увеличивает длину змейки на 1."""
        self.length += 1

    def draw(self, surface):
        """Отрисовывает все сегменты змейки и очищает старый хвост."""
        # Очищаем старую позицию последнего сегмента
        if self.last is not None:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

        # Рисуем тело
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


# --- ФУНКЦИИ ---

def handle_keys(game_object):
    """Обрабатывает события клавиатуры."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основной игровой цикл."""
    # screen и clock уже созданы на уровне модуля, поэтому global не нужен
    pygame.display.set_caption('Змейка')

    snake = Snake()
    apple = Apple()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.eat_apple()
            apple.randomize_position()

        if snake.check_self_collision():
            snake.reset()

        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw(screen)
        snake.draw(screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()
