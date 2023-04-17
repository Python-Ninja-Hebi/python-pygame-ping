import pygame, asyncio

FRAMES_PER_SECOND = 30


class Ping:
    HEIGHT = 600
    WIDTH = 800

    PADDLE_WIDTH = 10
    PADDLE_HEIGHT = 100
    PADDLE_VELOCITY = 10

    BALL_WIDTH = 10
    BALL_VELOCITY = 160

    COLOR = (255, 255, 255)
    BK_COLOR = (0, 0, 0)

    def __init__(self):
        pygame.init()  # pygame instanz starten

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))  # Bildschirm
        pygame.display.set_caption("Ping")

        self.clock = pygame.time.Clock()  # Uhr

        self.score_left = 0
        self.score_right = 0

        self.central_line = pygame.Rect(self.WIDTH / 2, 0, 1, self.HEIGHT)

        self.paddle_left = Paddle(0, self.HEIGHT / 2 - self.PADDLE_HEIGHT / 2,
                                  self.PADDLE_WIDTH, self.PADDLE_HEIGHT,
                                  self.COLOR, pygame.K_w, pygame.K_s,
                                  self.PADDLE_VELOCITY)

        self.paddle_right = Paddle(self.WIDTH - self.PADDLE_WIDTH, self.HEIGHT / 2 - self.PADDLE_HEIGHT / 2,
                                   self.PADDLE_WIDTH, self.PADDLE_HEIGHT,
                                   self.COLOR, pygame.K_UP, pygame.K_DOWN,
                                   self.PADDLE_VELOCITY)

        self.ball = Ball(self.WIDTH / 2 - self.BALL_WIDTH, self.HEIGHT / 2 - self.BALL_WIDTH / 2,
                         self.PADDLE_WIDTH, self.COLOR,
                         self.BALL_VELOCITY)

    async def game_loop(self):
        while True:
            for event in pygame.event.get():
                if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) \
                        or (event.type == pygame.QUIT):
                    return

            self.update()
            self.draw()
            await asyncio.sleep(0)

    def draw(self):
        self.screen.fill(self.BK_COLOR)
        self.paddle_left.draw(self.screen)
        self.paddle_right.draw(self.screen)
        self.ball.draw(self.screen)
        pygame.draw.rect(self.screen, self.COLOR, self.central_line)

        font = pygame.font.Font(None, 74)
        text = font.render(str(self.score_left), 1, self.COLOR)
        self.screen.blit(text, (self.WIDTH / 4, 10))
        text = font.render(str(self.score_right), 1, self.COLOR)
        self.screen.blit(text, (self.WIDTH / 4 * 3, 10))

        pygame.display.flip()

    def update(self):
        delta_time = self.clock.tick(FRAMES_PER_SECOND)
        self.paddle_left.update()
        self.ball.update(delta_time)
        if self.ball.collider_rect.colliderect(self.paddle_left.rect) \
                or self.ball.collider_rect.colliderect(self.paddle_right.rect):
            self.ball.collides()

        if self.ball.pos.x - self.ball.radius < 0:
            self.score_right += 1
            self.ball.start_pos()
        if self.ball.pos.x + self.ball.radius > self.WIDTH:
            self.score_left += 1
            self.ball.start_pos()

        self.paddle_right.update()


class Paddle:

    def __init__(self, left, top, width, height, color, up_key, down_key, velocity):
        self.rect = pygame.Rect(left, top, width, height)
        self._color = color
        self._up_key = up_key
        self._down_key = down_key
        self._velocity = velocity

    def draw(self, surface):
        pygame.draw.rect(surface, self._color, self.rect)

    def update(self):
        keys_pressed = pygame.key.get_pressed()

        if keys_pressed[self._up_key]:
            if self.rect.y - self._velocity > 0:
                self.rect.move_ip(0, - self._velocity)
        if keys_pressed[self._down_key]:
            if self.rect.y + self._velocity < Ping.HEIGHT - self.rect.height:
                self.rect.move_ip(0, self._velocity)


class Ball:
    def __init__(self, left, top, width, color, velocity):
        self.pos = pygame.math.Vector2(left, top)
        self._start_pos = pygame.math.Vector2(left, top)
        self.radius = int(width / 2)
        self._color = color
        self._velocity = velocity
        self._direction = pygame.math.Vector2(1, 1)
        self._start_direction = pygame.math.Vector2(1, 1)
        self._direction.normalize_ip()
        self.collider_rect = None
        self._set_collider_rect()

    def _set_collider_rect(self):
        self.collider_rect = pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2,
                                         self.radius * 2)

    def draw(self, surface):
        pygame.draw.circle(surface, self._color, (int(self.pos.x), int(self.pos.y)), int(self.radius))

    def update(self, delta_time):
        self.pos += self._direction * self._velocity * delta_time / 1000
        self._set_collider_rect()
        if self.pos.y - self.radius < 0 or self.pos.y + self.radius > Ping.HEIGHT:
            self._direction.y = - self._direction.y

    def start_pos(self):
        self.pos = pygame.math.Vector2(self._start_pos)
        self._direction = pygame.math.Vector2(self._start_direction)

    def collides(self):
        self._direction.x = - self._direction.x

async def main():
    ping = Ping()
    await ping.game_loop()

asyncio.run(main())