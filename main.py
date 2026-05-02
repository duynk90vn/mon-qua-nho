import math
from pathlib import Path
import random
import sys

try:
    import pygame
except ModuleNotFoundError:
    print("Thieu thu vien pygame. Hay cai bang lenh: pip install pygame")
    sys.exit(1)


# Cau hinh man hinh va mau sac chinh
WIDTH = 900
HEIGHT = 900
FPS = 60

NIGHT_TOP = (7, 10, 28)
NIGHT_BOTTOM = (18, 20, 48)
WHITE = (246, 248, 255)
SOFT_PINK = (255, 190, 220)

WISH_TEXT = "Chúc cháu luôn vui vẻ và gặp thật nhiều điều dễ thương"
SUB_TEXT = "Một món quà nhỏ gửi đến cháu"
BACKGROUND_IMAGE = "HDT.png"
EXIT_BUTTON_TEXT = "EXIT"


def choose_font(size, bold=False):
    """Chon font co ho tro tieng Viet tot tren Windows/macOS/Linux."""
    preferred_fonts = [
        "Segoe UI",
        "Arial",
        "Tahoma",
        "Verdana",
        "DejaVu Sans",
    ]
    return pygame.font.SysFont(preferred_fonts, size, bold=bold)


def choose_fitted_font(text, start_size, max_width, bold=False):
    """Chon co chu lon nhat co the nhung van nam gon trong man hinh."""
    size = start_size

    while size >= 28:
        font = choose_font(size, bold=bold)
        if font.size(text)[0] <= max_width:
            return font
        size -= 2

    return choose_font(size, bold=bold)


def draw_vertical_gradient(surface, top_color, bottom_color):
    """Ve nen troi dem voi gradient doc."""
    height = surface.get_height()
    width = surface.get_width()

    for y in range(height):
        ratio = y / max(height - 1, 1)
        color = (
            int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio),
            int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio),
            int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio),
        )
        pygame.draw.line(surface, color, (0, y), (width, y))


def resource_path(filename):
    """Lay duong dan file dung cho ca khi chay Python va khi dong goi .exe."""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / filename
    return Path(__file__).with_name(filename)


def get_image_size(filename):
    """Lay kich thuoc anh nen de tao cua so dung ti le anh."""
    image_path = resource_path(filename)
    if not image_path.exists():
        return WIDTH, HEIGHT

    image = pygame.image.load(str(image_path))
    return image.get_size()


def load_fit_background(filename, width, height):
    """Tai anh nen va scale vua khit cua so vuong, khong de vien thua."""
    image_path = resource_path(filename)
    if not image_path.exists():
        return None

    image = pygame.image.load(str(image_path)).convert()
    return pygame.transform.smoothscale(image, (width, height)).convert()


def draw_background(surface, background_image):
    """Ve anh nen, khong phu lop mo de giu anh sac net."""
    if background_image:
        surface.blit(background_image, (0, 0))
        return

    draw_vertical_gradient(surface, NIGHT_TOP, NIGHT_BOTTOM)


def create_star_field(amount, width, height):
    """Tao cac ngoi sao nen co kich thuoc va do sang khac nhau."""
    stars = []
    for _ in range(amount):
        stars.append(
            {
                "x": random.randint(0, width),
                "y": random.randint(0, height),
                "radius": random.choice([1, 1, 1, 2]),
                "alpha": random.randint(70, 185),
                "twinkle": random.random() * math.tau,
            }
        )
    return stars


def draw_stars(surface, stars, elapsed_time):
    """Ve sao lap lanh nhe de nen khong bi trong."""
    for star in stars:
        blink = math.sin(elapsed_time * 1.6 + star["twinkle"]) * 35
        alpha = max(35, min(220, star["alpha"] + blink))
        star_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(
            star_surface,
            (255, 250, 225, int(alpha)),
            (3, 3),
            star["radius"],
        )
        surface.blit(star_surface, (star["x"], star["y"]))


class Particle:
    """Hat phao hoa sau khi no, mo dan va roi nhe theo trong luc."""

    def __init__(self, x, y, color):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(2.2, 7.2)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.life = random.randint(55, 95)
        self.max_life = self.life
        self.radius = random.uniform(1.8, 3.7)
        self.gravity = random.uniform(0.035, 0.075)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= 0.992
        self.life -= 1

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        if alpha <= 0:
            return

        glow_size = int(self.radius * 6)
        glow = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            glow,
            (*self.color, max(18, alpha // 4)),
            (glow_size, glow_size),
            glow_size,
        )
        pygame.draw.circle(
            glow,
            (*self.color, alpha),
            (glow_size, glow_size),
            max(1, int(self.radius)),
        )
        surface.blit(glow, (self.x - glow_size, self.y - glow_size))

    @property
    def is_alive(self):
        return self.life > 0


class Rocket:
    """Chum phao hoa bay len, den diem muc tieu thi no thanh nhieu hat."""

    def __init__(self, target_x=None, target_y=None):
        self.x = target_x if target_x is not None else random.randint(120, WIDTH - 120)
        self.y = HEIGHT + 20
        self.target_y = target_y if target_y is not None else random.randint(110, HEIGHT // 2)
        self.vx = random.uniform(-0.7, 0.7)
        self.vy = random.uniform(-10.8, -8.2)
        self.color = random.choice(
            [
                (255, 116, 142),
                (255, 210, 92),
                (120, 220, 255),
                (183, 151, 255),
                (145, 239, 191),
                (255, 160, 220),
            ]
        )
        self.trail = []

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 14:
            self.trail.pop(0)

        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08

    def draw(self, surface):
        for index, point in enumerate(self.trail):
            alpha = int(180 * (index + 1) / len(self.trail))
            trail_surface = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, (*self.color, alpha), (6, 6), 2)
            surface.blit(trail_surface, (point[0] - 6, point[1] - 6))

        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 4)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 2)

    def should_explode(self):
        return self.y <= self.target_y or self.vy >= -1.5

    def explode(self):
        particles = []
        palette = [
            self.color,
            (255, 245, 180),
            (255, 185, 220),
            (155, 235, 255),
            (190, 255, 205),
        ]
        for _ in range(random.randint(90, 145)):
            particles.append(Particle(self.x, self.y, random.choice(palette)))
        return particles


def create_click_firework(x, y):
    """Click chuot tao phao hoa no ngay tai vi tri chon."""
    color = random.choice(
        [
            (255, 132, 160),
            (255, 220, 105),
            (130, 220, 255),
            (175, 155, 255),
            (150, 245, 198),
        ]
    )
    return [Particle(x, y, color) for _ in range(130)]


def draw_text_sharp(surface, font, text, center, text_color, outline_color):
    """Ve chu sac net voi vien toi ro, de doc tren anh nen."""
    outline_surface = font.render(text, True, outline_color)
    outline_rect = outline_surface.get_rect(center=center)

    for dx, dy in [
        (-3, 0),
        (3, 0),
        (0, -3),
        (0, 3),
        (-2, -2),
        (2, -2),
        (-2, 2),
        (2, 2),
    ]:
        surface.blit(outline_surface, outline_rect.move(dx, dy))

    text_surface = font.render(text, True, text_color)
    rect = text_surface.get_rect(center=center)
    surface.blit(text_surface, rect)


def draw_exit_button(surface, font, button_rect):
    """Ve nut thoat o goc duoi ben phai."""
    button_surface = pygame.Surface(button_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(
        button_surface,
        (8, 10, 22, 185),
        button_surface.get_rect(),
        border_radius=10,
    )
    pygame.draw.rect(
        button_surface,
        (255, 255, 255, 130),
        button_surface.get_rect(),
        width=2,
        border_radius=10,
    )

    text_surface = font.render(EXIT_BUTTON_TEXT, True, (255, 245, 250))
    text_rect = text_surface.get_rect(center=button_surface.get_rect().center)
    button_surface.blit(text_surface, text_rect)
    surface.blit(button_surface, button_rect)


def draw_center_message(surface, width, height, title_font, sub_font):
    """Ve loi chuc o phia duoi de khong che phan mat."""
    title_y = height - 145
    second_y = height - 96
    sub_y = height - 46

    draw_text_sharp(
        surface,
        title_font,
        "Chúc cháu luôn vui vẻ",
        (width // 2, title_y),
        WHITE,
        (0, 0, 0),
    )
    draw_text_sharp(
        surface,
        title_font,
        "và gặp thật nhiều điều dễ thương",
        (width // 2, second_y),
        WHITE,
        (0, 0, 0),
    )
    draw_text_sharp(
        surface,
        sub_font,
        SUB_TEXT,
        (width // 2, sub_y),
        (255, 236, 246),
        (0, 0, 0),
    )


def main():
    global WIDTH, HEIGHT

    pygame.init()
    pygame.display.set_caption("Loi chuc ngay moi ")

    image_width, image_height = get_image_size(BACKGROUND_IMAGE)
    info = pygame.display.Info()
    max_size = min(image_width, image_height, info.current_w - 80, info.current_h - 120)
    WIDTH = max(720, int(max_size))
    HEIGHT = WIDTH

    # Cua so vuong bang voi phan anh dang hien thi, khong con vien thua hai ben.
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    title_font = choose_fitted_font("và gặp thật nhiều điều dễ thương", 42, WIDTH - 70, bold=True)
    sub_font = choose_fitted_font(SUB_TEXT, 26, WIDTH - 80)
    exit_font = choose_font(20, bold=True)
    exit_button_rect = pygame.Rect(WIDTH - 98, HEIGHT - 48, 78, 32)
    stars = create_star_field(130, WIDTH, HEIGHT)
    background_image = load_fit_background(BACKGROUND_IMAGE, WIDTH, HEIGHT)

    rockets = []
    particles = []
    spawn_timer = 0
    running = True

    while running:
        dt = clock.tick(FPS) / 1000
        elapsed_time = pygame.time.get_ticks() / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if exit_button_rect.collidepoint(event.pos):
                    running = False
                else:
                    particles.extend(create_click_firework(*event.pos))

        draw_background(screen, background_image)
        draw_stars(screen, stars, elapsed_time)

        # Tu dong ban phao hoa lien tuc o nhieu vi tri.
        spawn_timer -= dt
        if spawn_timer <= 0:
            rockets.append(Rocket())
            spawn_timer = random.uniform(0.28, 0.75)

        for rocket in rockets[:]:
            rocket.update()
            rocket.draw(screen)

            if rocket.should_explode():
                particles.extend(rocket.explode())
                rockets.remove(rocket)

        for particle in particles[:]:
            particle.update()
            particle.draw(screen)

            if not particle.is_alive:
                particles.remove(particle)

        draw_center_message(screen, WIDTH, HEIGHT, title_font, sub_font)
        draw_exit_button(screen, exit_font, exit_button_rect)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
