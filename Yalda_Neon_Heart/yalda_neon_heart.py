"""
Yalda Neon Heart
A single-file cinematic Pygame experience.

Controls
--------
SPACE / left click : trigger a heart burst
R                  : replay the opening sequence
F                  : toggle fullscreen
M                  : mute or unmute
ESC                : quit

Install Pygame:
    py -m pip install pygame

Run:
    py yalda_neon_heart.py
"""

from __future__ import annotations

import math
import random
import sys
from array import array
from dataclasses import dataclass

try:
    import pygame
    import pygame.gfxdraw
except ImportError:
    print("Pygame is not installed yet.")
    print("Run this command in Command Prompt:")
    print("    py -m pip install pygame")
    input("\nPress Enter to close...")
    raise SystemExit(1)


# -----------------------------------------------------------------------------
# PERSONALIZATION
# -----------------------------------------------------------------------------
NAME = "YALDA"
MESSAGE_LINES = [
    "No matter how far apart we are,",
    "my heart will always find its way to you.",
    "I love you. Always. ♥",
]
WINDOW_TITLE = "For Yalda ♥"

# Window and animation settings
START_SIZE = (1280, 720)
FPS = 60
HEART_PARTICLES = 720
BACKGROUND_STARS = 150
AMBIENT_PARTICLES = 90

# Palette
DEEP_BACKGROUND = (4, 2, 14)
TOP_BACKGROUND = (20, 6, 38)
BOTTOM_BACKGROUND = (4, 2, 14)
WHITE = (255, 248, 255)
SOFT_PINK = (255, 155, 205)
HOT_PINK = (255, 35, 145)
CRIMSON = (235, 20, 85)
VIOLET = (165, 75, 255)

TAU = math.tau


# -----------------------------------------------------------------------------
# SMALL HELPERS
# -----------------------------------------------------------------------------
def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def lerp(a: float, b: float, amount: float) -> float:
    return a + (b - a) * amount


def ease_out_cubic(value: float) -> float:
    value = clamp(value, 0.0, 1.0)
    return 1.0 - (1.0 - value) ** 3


def ease_in_out_cubic(value: float) -> float:
    value = clamp(value, 0.0, 1.0)
    if value < 0.5:
        return 4.0 * value**3
    return 1.0 - ((-2.0 * value + 2.0) ** 3) / 2.0


def smoothstep(edge0: float, edge1: float, value: float) -> float:
    if edge0 == edge1:
        return 0.0
    value = clamp((value - edge0) / (edge1 - edge0), 0.0, 1.0)
    return value * value * (3.0 - 2.0 * value)


def mix_color(a: tuple[int, int, int], b: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    amount = clamp(amount, 0.0, 1.0)
    return (
        int(lerp(a[0], b[0], amount)),
        int(lerp(a[1], b[1], amount)),
        int(lerp(a[2], b[2], amount)),
    )


def rotating_heart_color(seconds: float) -> tuple[int, int, int]:
    """Smoothly blend through crimson, pink, and violet."""
    phase = (seconds * 0.10) % 1.0
    if phase < 1 / 3:
        return mix_color(CRIMSON, HOT_PINK, phase * 3)
    if phase < 2 / 3:
        return mix_color(HOT_PINK, VIOLET, (phase - 1 / 3) * 3)
    return mix_color(VIOLET, CRIMSON, (phase - 2 / 3) * 3)




def draw_radial_glow(
    target: pygame.Surface,
    position: pygame.Vector2 | tuple[float, float],
    radius: float,
    color: tuple[int, int, int],
    alpha: int,
) -> None:
    """Draw a smoother radial glow for larger highlights."""
    maximum = max(2, int(radius))
    center = (int(position[0]), int(position[1]))
    for current in range(maximum, 0, -1):
        inward = 1.0 - current / maximum
        current_alpha = int(alpha * inward * inward)
        pygame.draw.circle(target, (*color, current_alpha), center, current)


def heart_xy(t: float) -> pygame.Vector2:
    """Return a point on the classic parametric heart curve."""
    x = 16.0 * math.sin(t) ** 3
    y = (
        13.0 * math.cos(t)
        - 5.0 * math.cos(2.0 * t)
        - 2.0 * math.cos(3.0 * t)
        - math.cos(4.0 * t)
    )
    # Normalize into roughly -1..1 coordinates and flip Y for the screen.
    return pygame.Vector2(x / 18.0, -y / 18.0)


def random_edge_position(width: int, height: int) -> pygame.Vector2:
    side = random.randrange(4)
    margin = 45
    if side == 0:
        return pygame.Vector2(random.uniform(0, width), -margin)
    if side == 1:
        return pygame.Vector2(width + margin, random.uniform(0, height))
    if side == 2:
        return pygame.Vector2(random.uniform(0, width), height + margin)
    return pygame.Vector2(-margin, random.uniform(0, height))


def draw_soft_circle(
    target: pygame.Surface,
    position: pygame.Vector2 | tuple[float, float],
    radius: float,
    color: tuple[int, int, int],
    alpha: int,
) -> None:
    """Draw a tiny layered glow without external image assets."""
    radius_i = max(1, int(radius))
    x, y = int(position[0]), int(position[1])
    for multiplier, fade in ((3.2, 0.08), (2.1, 0.16), (1.35, 0.30)):
        pygame.draw.circle(
            target,
            (*color, int(alpha * fade)),
            (x, y),
            max(1, int(radius_i * multiplier)),
        )
    pygame.draw.circle(target, (*color, alpha), (x, y), radius_i)


# -----------------------------------------------------------------------------
# PROCEDURAL AUDIO
# -----------------------------------------------------------------------------
def make_sound(kind: str) -> pygame.mixer.Sound | None:
    """Create simple sound effects in memory, with no WAV files required."""
    if pygame.mixer.get_init() is None:
        return None

    sample_rate = pygame.mixer.get_init()[0]
    duration = {"heartbeat": 0.48, "chime": 1.8, "sparkle": 0.30}[kind]
    total = int(sample_rate * duration)
    samples = array("h")

    for index in range(total):
        t = index / sample_rate
        value = 0.0

        if kind == "heartbeat":
            # Two bassy pulses make a gentle "lub-dub".
            for start, strength, frequency, decay in (
                (0.015, 0.92, 58.0, 24.0),
                (0.205, 0.58, 48.0, 28.0),
            ):
                local = t - start
                if local >= 0:
                    envelope = math.exp(-decay * local)
                    value += strength * envelope * (
                        math.sin(TAU * frequency * local)
                        + 0.30 * math.sin(TAU * frequency * 2.0 * local)
                    )

        elif kind == "chime":
            # A soft major chord with a slow decay.
            envelope = math.exp(-2.25 * t)
            frequencies = (523.25, 659.25, 783.99, 1046.50)
            value = sum(
                math.sin(TAU * frequency * t + note * 0.17)
                for note, frequency in enumerate(frequencies)
            )
            value *= envelope * 0.17

        elif kind == "sparkle":
            envelope = math.exp(-9.0 * t)
            frequency = 850.0 + 2400.0 * (t / duration)
            value = math.sin(TAU * frequency * t) * envelope * 0.26

        samples.append(int(clamp(value, -1.0, 1.0) * 32767))

    try:
        return pygame.mixer.Sound(buffer=samples.tobytes())
    except pygame.error:
        return None


# -----------------------------------------------------------------------------
# VISUAL OBJECTS
# -----------------------------------------------------------------------------
@dataclass
class Star:
    x: float
    y: float
    radius: float
    speed: float
    phase: float

    def update(self, dt: float, width: int, height: int) -> None:
        self.y += self.speed * dt
        if self.y > height + 4:
            self.y = -4
            self.x = random.uniform(0, width)

    def draw(self, surface: pygame.Surface, seconds: float) -> None:
        twinkle = 0.45 + 0.55 * math.sin(seconds * 1.8 + self.phase) ** 2
        alpha = int(35 + 125 * twinkle)
        pygame.draw.circle(
            surface,
            (235, 215, 255, alpha),
            (int(self.x), int(self.y)),
            max(1, int(self.radius)),
        )


@dataclass
class AmbientParticle:
    position: pygame.Vector2
    velocity: pygame.Vector2
    radius: float
    phase: float
    color_offset: float

    def update(self, dt: float, width: int, height: int, mouse: pygame.Vector2) -> None:
        self.position += self.velocity * dt
        self.position.x += math.sin(self.phase + self.position.y * 0.008) * dt * 5.0
        self.phase += dt * 0.7

        # Subtle mouse attraction gives the background a living quality.
        delta = mouse - self.position
        distance_sq = max(delta.length_squared(), 80.0)
        if distance_sq < 70000:
            self.velocity += delta.normalize() * (18000.0 / distance_sq) * dt
            self.velocity *= 0.992

        margin = 30
        if self.position.x < -margin:
            self.position.x = width + margin
        elif self.position.x > width + margin:
            self.position.x = -margin
        if self.position.y < -margin:
            self.position.y = height + margin
        elif self.position.y > height + margin:
            self.position.y = -margin

    def draw(self, surface: pygame.Surface, seconds: float) -> None:
        base = rotating_heart_color(seconds + self.color_offset)
        alpha = int(40 + 45 * (0.5 + 0.5 * math.sin(seconds * 2.0 + self.phase)))
        draw_soft_circle(surface, self.position, self.radius, base, alpha)


@dataclass
class AssemblyParticle:
    start: pygame.Vector2
    target_unit: pygame.Vector2
    delay: float
    duration: float
    radius: float
    phase: float

    def position(
        self,
        sequence_time: float,
        center: pygame.Vector2,
        heart_size: float,
    ) -> tuple[pygame.Vector2, float]:
        progress = clamp((sequence_time - self.delay) / self.duration, 0.0, 1.0)
        eased = ease_in_out_cubic(progress)
        target = center + self.target_unit * heart_size

        # A shrinking spiral makes the particles feel magnetized into place.
        direction = target - self.start
        perpendicular = pygame.Vector2(-direction.y, direction.x)
        if perpendicular.length_squared() > 0:
            perpendicular = perpendicular.normalize()
        swirl = perpendicular * math.sin(progress * math.pi * 3.0 + self.phase)
        swirl *= (1.0 - progress) * 70.0
        point = self.start.lerp(target, eased) + swirl
        return point, progress


@dataclass
class BurstParticle:
    position: pygame.Vector2
    velocity: pygame.Vector2
    life: float
    maximum_life: float
    radius: float
    color: tuple[int, int, int]

    def update(self, dt: float) -> None:
        self.life -= dt
        self.position += self.velocity * dt
        self.velocity *= 0.985 ** (dt * 60.0)
        self.velocity.y += 18.0 * dt

    def draw(self, surface: pygame.Surface) -> None:
        ratio = clamp(self.life / self.maximum_life, 0.0, 1.0)
        alpha = int(255 * ratio)
        draw_soft_circle(surface, self.position, self.radius * (0.5 + ratio), self.color, alpha)


@dataclass
class MouseTrailParticle:
    position: pygame.Vector2
    velocity: pygame.Vector2
    life: float
    maximum_life: float
    radius: float

    def update(self, dt: float) -> None:
        self.life -= dt
        self.position += self.velocity * dt
        self.velocity *= 0.94 ** (dt * 60.0)

    def draw(self, surface: pygame.Surface, seconds: float) -> None:
        ratio = clamp(self.life / self.maximum_life, 0.0, 1.0)
        draw_soft_circle(
            surface,
            self.position,
            self.radius * ratio,
            rotating_heart_color(seconds + self.position.x * 0.001),
            int(170 * ratio),
        )


@dataclass
class Shockwave:
    radius: float
    speed: float
    alpha: float
    width: int

    def update(self, dt: float) -> None:
        self.radius += self.speed * dt
        self.alpha -= 105.0 * dt

    def draw(self, surface: pygame.Surface, center: pygame.Vector2, color: tuple[int, int, int]) -> None:
        if self.alpha <= 0:
            return
        pygame.draw.circle(
            surface,
            (*color, int(self.alpha)),
            (int(center.x), int(center.y)),
            max(1, int(self.radius)),
            self.width,
        )


# -----------------------------------------------------------------------------
# MAIN EXPERIENCE
# -----------------------------------------------------------------------------
class NeonHeartExperience:
    def __init__(self) -> None:
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()

        self.windowed_size = START_SIZE
        self.fullscreen = False
        self.screen = pygame.display.set_mode(START_SIZE, pygame.RESIZABLE)
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()

        self.font_cache: dict[int, pygame.font.Font] = {}
        self.background: pygame.Surface | None = None
        self.background_fx_layer: pygame.Surface | None = None
        self.heart_layer: pygame.Surface | None = None
        self.foreground_fx_layer: pygame.Surface | None = None
        self.overlay_layer: pygame.Surface | None = None
        self.fade_layer: pygame.Surface | None = None

        self.stars: list[Star] = []
        self.ambient: list[AmbientParticle] = []
        self.assembly: list[AssemblyParticle] = []
        self.bursts: list[BurstParticle] = []
        self.mouse_trail: list[MouseTrailParticle] = []
        self.shockwaves: list[Shockwave] = []

        self.sequence_time = 0.0
        self.running = True
        self.muted = False
        self.last_mouse_position = pygame.Vector2(pygame.mouse.get_pos())
        self.mouse_spawn_accumulator = 0.0
        self.next_heartbeat = 4.45
        self.chime_played = False

        self.heartbeat_sound = make_sound("heartbeat")
        self.chime_sound = make_sound("chime")
        self.sparkle_sound = make_sound("sparkle")

        self.rebuild_for_size()
        self.restart_sequence()

    @property
    def size(self) -> tuple[int, int]:
        return self.screen.get_size()

    @property
    def center(self) -> pygame.Vector2:
        width, height = self.size
        return pygame.Vector2(width / 2.0, height * 0.47)

    @property
    def heart_size(self) -> float:
        width, height = self.size
        return min(width * 0.29, height * 0.37)

    def get_font(self, size: int, bold: bool = False) -> pygame.font.Font:
        key = size * 2 + int(bold)
        if key not in self.font_cache:
            # Segoe UI is common on Windows. Pygame falls back safely if absent.
            self.font_cache[key] = pygame.font.SysFont("segoeui", size, bold=bold)
        return self.font_cache[key]

    def rebuild_for_size(self) -> None:
        width, height = self.size
        self.background = self.make_gradient_background(width, height)
        self.background_fx_layer = pygame.Surface((width, height), pygame.SRCALPHA)
        self.heart_layer = pygame.Surface((width, height), pygame.SRCALPHA)
        self.foreground_fx_layer = pygame.Surface((width, height), pygame.SRCALPHA)
        self.overlay_layer = pygame.Surface((width, height), pygame.SRCALPHA)
        self.fade_layer = pygame.Surface((width, height), pygame.SRCALPHA)

        if not self.stars:
            self.stars = [
                Star(
                    random.uniform(0, width),
                    random.uniform(0, height),
                    random.choice((1.0, 1.0, 1.4, 1.8)),
                    random.uniform(3.0, 15.0),
                    random.uniform(0, TAU),
                )
                for _ in range(BACKGROUND_STARS)
            ]

        if not self.ambient:
            self.ambient = [
                AmbientParticle(
                    pygame.Vector2(random.uniform(0, width), random.uniform(0, height)),
                    pygame.Vector2(random.uniform(-6, 6), random.uniform(-10, -2)),
                    random.uniform(1.0, 2.4),
                    random.uniform(0, TAU),
                    random.uniform(0, 8),
                )
                for _ in range(AMBIENT_PARTICLES)
            ]

    @staticmethod
    def make_gradient_background(width: int, height: int) -> pygame.Surface:
        surface = pygame.Surface((width, height))
        for y in range(height):
            amount = y / max(1, height - 1)
            color = mix_color(TOP_BACKGROUND, BOTTOM_BACKGROUND, amount)
            pygame.draw.line(surface, color, (0, y), (width, y))

        # Add a gentle central vignette glow.
        vignette = pygame.Surface((width, height), pygame.SRCALPHA)
        center = (width // 2, int(height * 0.46))
        maximum = int(min(width, height) * 0.55)
        for radius in range(maximum, 0, -18):
            amount = 1.0 - radius / maximum
            alpha = int(2 + 5 * amount)
            pygame.draw.circle(vignette, (110, 25, 135, alpha), center, radius)
        surface.blit(vignette, (0, 0))
        return surface

    def restart_sequence(self) -> None:
        width, height = self.size
        self.sequence_time = 0.0
        self.next_heartbeat = 4.45
        self.chime_played = False
        self.bursts.clear()
        self.shockwaves.clear()
        self.mouse_trail.clear()
        self.assembly.clear()

        for index in range(HEART_PARTICLES):
            # Most particles land on the edge; some land inside for a fuller body.
            t = random.uniform(0, TAU)
            unit = heart_xy(t)
            if index % 4 != 0:
                unit *= math.sqrt(random.uniform(0.25, 1.0))
            jitter = pygame.Vector2(random.uniform(-0.018, 0.018), random.uniform(-0.018, 0.018))
            unit += jitter

            self.assembly.append(
                AssemblyParticle(
                    start=random_edge_position(width, height),
                    target_unit=unit,
                    delay=random.uniform(0.65, 2.45),
                    duration=random.uniform(1.45, 2.40),
                    radius=random.uniform(1.0, 2.6),
                    phase=random.uniform(0, TAU),
                )
            )

    def play_sound(self, sound: pygame.mixer.Sound | None, volume: float = 1.0) -> None:
        if sound is None or self.muted:
            return
        sound.set_volume(clamp(volume, 0.0, 1.0))
        sound.play()

    def toggle_fullscreen(self) -> None:
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.windowed_size = self.size
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
        self.font_cache.clear()
        self.rebuild_for_size()
        self.restart_sequence()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.VIDEORESIZE and not self.fullscreen:
                self.windowed_size = (max(720, event.w), max(480, event.h))
                self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
                self.font_cache.clear()
                self.rebuild_for_size()
                self.restart_sequence()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.trigger_burst(power=1.0)
                elif event.key == pygame.K_r:
                    self.restart_sequence()
                elif event.key == pygame.K_f:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_m:
                    self.muted = not self.muted

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse = pygame.Vector2(event.pos)
                if mouse.distance_to(self.center) < self.heart_size * 1.15:
                    self.trigger_burst(power=1.15)
                else:
                    self.create_click_sparkle(mouse)

    def create_click_sparkle(self, position: pygame.Vector2) -> None:
        color = rotating_heart_color(self.sequence_time)
        for _ in range(30):
            angle = random.uniform(0, TAU)
            speed = random.uniform(45, 190)
            self.bursts.append(
                BurstParticle(
                    position.copy(),
                    pygame.Vector2(math.cos(angle), math.sin(angle)) * speed,
                    random.uniform(0.55, 1.15),
                    1.15,
                    random.uniform(1.0, 2.8),
                    mix_color(color, WHITE, random.uniform(0.0, 0.55)),
                )
            )
        self.play_sound(self.sparkle_sound, 0.35)

    def trigger_burst(self, power: float) -> None:
        center = self.center
        color = rotating_heart_color(self.sequence_time)
        count = int(190 * power)

        for _ in range(count):
            t = random.uniform(0, TAU)
            source = center + heart_xy(t) * self.heart_size * random.uniform(0.35, 1.0)
            direction = source - center
            if direction.length_squared() == 0:
                direction = pygame.Vector2(1, 0)
            direction = direction.normalize().rotate(random.uniform(-30, 30))
            speed = random.uniform(65, 310) * power
            particle_color = mix_color(color, WHITE, random.uniform(0.0, 0.55))
            life = random.uniform(0.8, 1.7)
            self.bursts.append(
                BurstParticle(
                    source,
                    direction * speed,
                    life,
                    life,
                    random.uniform(1.2, 3.4),
                    particle_color,
                )
            )

        self.shockwaves.append(Shockwave(self.heart_size * 0.45, 240 * power, 210, 3))
        self.shockwaves.append(Shockwave(self.heart_size * 0.34, 150 * power, 130, 2))
        self.play_sound(self.heartbeat_sound, 0.65)
        self.play_sound(self.sparkle_sound, 0.22)

    def heartbeat_scale(self) -> float:
        if self.sequence_time < 4.35:
            return 1.0
        cycle = (self.sequence_time - 4.35) % 1.25
        first = math.exp(-((cycle - 0.10) / 0.065) ** 2)
        second = math.exp(-((cycle - 0.29) / 0.085) ** 2)
        breathing = 0.012 * math.sin(self.sequence_time * 1.6)
        return 1.0 + breathing + 0.095 * first + 0.045 * second

    def update(self, dt: float) -> None:
        self.sequence_time += dt
        width, height = self.size
        mouse = pygame.Vector2(pygame.mouse.get_pos())

        for star in self.stars:
            star.update(dt, width, height)
        for particle in self.ambient:
            particle.update(dt, width, height, mouse)

        # Make the mouse leave a glittery ribbon while moving.
        mouse_distance = mouse.distance_to(self.last_mouse_position)
        self.mouse_spawn_accumulator += mouse_distance * 0.09
        while self.mouse_spawn_accumulator >= 1.0:
            self.mouse_spawn_accumulator -= 1.0
            life = random.uniform(0.35, 0.75)
            self.mouse_trail.append(
                MouseTrailParticle(
                    position=mouse + pygame.Vector2(random.uniform(-3, 3), random.uniform(-3, 3)),
                    velocity=pygame.Vector2(random.uniform(-16, 16), random.uniform(-22, 8)),
                    life=life,
                    maximum_life=life,
                    radius=random.uniform(1.6, 3.2),
                )
            )
        self.last_mouse_position = mouse

        for particle in self.mouse_trail:
            particle.update(dt)
        self.mouse_trail = [p for p in self.mouse_trail if p.life > 0]

        for particle in self.bursts:
            particle.update(dt)
        self.bursts = [p for p in self.bursts if p.life > 0]

        for wave in self.shockwaves:
            wave.update(dt)
        self.shockwaves = [wave for wave in self.shockwaves if wave.alpha > 0]

        # Schedule regular heartbeats after the assembly completes.
        if self.sequence_time >= self.next_heartbeat:
            self.shockwaves.append(Shockwave(self.heart_size * 0.50, 105, 92, 2))
            self.play_sound(self.heartbeat_sound, 0.48)
            self.next_heartbeat += 1.25

        if self.sequence_time >= 7.15 and not self.chime_played:
            self.chime_played = True
            self.play_sound(self.chime_sound, 0.38)

    def draw_heart_polygon(
        self,
        surface: pygame.Surface,
        center: pygame.Vector2,
        size: float,
        color: tuple[int, int, int],
        alpha: int,
    ) -> None:
        points = []
        for index in range(220):
            t = TAU * index / 220
            point = center + heart_xy(t) * size
            points.append((int(point.x), int(point.y)))
        pygame.gfxdraw.filled_polygon(surface, points, (*color, alpha))
        pygame.gfxdraw.aapolygon(surface, points, (*mix_color(color, WHITE, 0.25), alpha))

    def draw_cinematic_heart(
        self,
        bloom_surface: pygame.Surface,
        heart_surface: pygame.Surface,
        sparkle_surface: pygame.Surface,
    ) -> None:
        if self.sequence_time < 3.55:
            return

        appear = smoothstep(3.55, 4.55, self.sequence_time)
        scale = self.heartbeat_scale()
        size = self.heart_size * scale
        color = rotating_heart_color(self.sequence_time)
        center = self.center

        # Large transparent silhouettes sit behind the solid heart as bloom.
        self.draw_heart_polygon(bloom_surface, center, size * 1.16, color, int(13 * appear))
        self.draw_heart_polygon(bloom_surface, center, size * 1.09, color, int(24 * appear))
        self.draw_heart_polygon(bloom_surface, center, size * 1.04, color, int(48 * appear))

        # The main body is nearly opaque, which keeps shockwaves behind it.
        self.draw_heart_polygon(heart_surface, center, size, color, int(252 * appear))

        # Add a luminous highlight that moves subtly across the heart.
        highlight_position = center + pygame.Vector2(
            -size * 0.25 + math.sin(self.sequence_time * 0.6) * 10,
            -size * 0.24,
        )
        draw_radial_glow(
            sparkle_surface,
            highlight_position,
            size * 0.085,
            WHITE,
            int(105 * appear),
        )

        # Fine sparkling points on the outline.
        for index in range(42):
            t = TAU * index / 42 + self.sequence_time * 0.04
            point = center + heart_xy(t) * size
            shimmer = 0.5 + 0.5 * math.sin(self.sequence_time * 4 + index * 1.7)
            draw_soft_circle(sparkle_surface, point, 1.0 + shimmer * 1.1, WHITE, int((35 + 100 * shimmer) * appear))

    def draw_assembly_particles(self, surface: pygame.Surface) -> None:
        if self.sequence_time > 5.35:
            return
        center = self.center
        size = self.heart_size
        color = rotating_heart_color(self.sequence_time)

        for particle in self.assembly:
            position, progress = particle.position(self.sequence_time, center, size)
            if progress <= 0:
                continue
            fade_after_arrival = 1.0 - smoothstep(4.45, 5.35, self.sequence_time)
            alpha = int((40 + 190 * progress) * fade_after_arrival)
            particle_color = mix_color(color, WHITE, 0.30 + 0.45 * math.sin(particle.phase) ** 2)
            draw_soft_circle(surface, position, particle.radius, particle_color, alpha)

    def draw_shockwaves(self, surface: pygame.Surface) -> None:
        color = rotating_heart_color(self.sequence_time)
        for wave in self.shockwaves:
            wave.draw(surface, self.center, mix_color(color, WHITE, 0.18))

    def draw_text(self, surface: pygame.Surface) -> None:
        width, height = self.size

        # Name reveal
        name_alpha = int(255 * smoothstep(5.0, 6.35, self.sequence_time))
        if name_alpha > 0:
            name_size = max(34, int(min(width, height) * 0.075))
            name_font = self.get_font(name_size, bold=True)
            name_surface = name_font.render(NAME, True, WHITE)
            name_surface.set_alpha(name_alpha)
            rect = name_surface.get_rect(center=(width // 2, int(height * 0.47)))
            surface.blit(name_surface, rect)

            # A thin glowing underline.
            underline_progress = ease_out_cubic(smoothstep(5.65, 6.7, self.sequence_time))
            underline_width = int(name_surface.get_width() * 0.82 * underline_progress)
            if underline_width > 0:
                y = rect.bottom + 9
                pygame.draw.line(
                    surface,
                    (*SOFT_PINK, int(170 * underline_progress)),
                    (width // 2 - underline_width // 2, y),
                    (width // 2 + underline_width // 2, y),
                    2,
                )

        # Typewriter message beneath the heart.
        message_start = 7.25
        characters_per_second = 24.0
        message_font_size = max(21, int(min(width, height) * 0.031))
        font = self.get_font(message_font_size)
        line_height = int(message_font_size * 1.42)
        y_start = int(height * 0.78)

        cumulative_delay = 0.0
        for line_index, full_line in enumerate(MESSAGE_LINES):
            local_time = self.sequence_time - message_start - cumulative_delay
            visible_count = int(max(0.0, local_time) * characters_per_second)
            visible_text = full_line[:visible_count]
            cumulative_delay += len(full_line) / characters_per_second + 0.36

            if not visible_text:
                continue

            text_surface = font.render(visible_text, True, (255, 220, 241))
            alpha = int(255 * smoothstep(0.0, 0.25, local_time))
            text_surface.set_alpha(alpha)
            rect = text_surface.get_rect(center=(width // 2, y_start + line_index * line_height))
            surface.blit(text_surface, rect)

        # Minimal controls, dim enough not to interrupt the scene.
        controls_font = self.get_font(max(14, int(min(width, height) * 0.019)))
        controls = "SPACE/click: burst    R: replay    F: fullscreen    M: mute    ESC: close"
        controls_surface = controls_font.render(controls, True, (155, 140, 180))
        controls_surface.set_alpha(int(135 * smoothstep(9.5, 11.0, self.sequence_time)))
        controls_rect = controls_surface.get_rect(midbottom=(width // 2, height - 15))
        surface.blit(controls_surface, controls_rect)

        if self.muted:
            mute_surface = controls_font.render("MUTED", True, (255, 170, 205))
            mute_surface.set_alpha(190)
            surface.blit(mute_surface, (15, 13))

    def draw_intro_fade(self, surface: pygame.Surface) -> None:
        if self.sequence_time >= 1.5:
            return
        alpha = int(255 * (1.0 - smoothstep(0.15, 1.5, self.sequence_time)))
        surface.fill((0, 0, 0, alpha))

    def draw(self) -> None:
        assert self.background is not None
        assert self.background_fx_layer is not None
        assert self.heart_layer is not None
        assert self.foreground_fx_layer is not None
        assert self.overlay_layer is not None
        assert self.fade_layer is not None

        self.screen.blit(self.background, (0, 0))
        self.background_fx_layer.fill((0, 0, 0, 0))
        self.heart_layer.fill((0, 0, 0, 0))
        self.foreground_fx_layer.fill((0, 0, 0, 0))
        self.overlay_layer.fill((0, 0, 0, 0))
        self.fade_layer.fill((0, 0, 0, 0))

        # Quiet living background and effects that should remain behind the heart.
        for star in self.stars:
            star.draw(self.background_fx_layer, self.sequence_time)
        for particle in self.ambient:
            particle.draw(self.background_fx_layer, self.sequence_time)
        self.draw_assembly_particles(self.background_fx_layer)
        self.draw_shockwaves(self.background_fx_layer)

        # Keep the solid heart isolated so translucent sparkles cannot punch holes in it.
        self.draw_cinematic_heart(
            self.background_fx_layer, self.heart_layer, self.foreground_fx_layer
        )

        for particle in self.bursts:
            particle.draw(self.foreground_fx_layer)
        for particle in self.mouse_trail:
            particle.draw(self.foreground_fx_layer, self.sequence_time)

        self.draw_text(self.overlay_layer)

        self.screen.blit(self.background_fx_layer, (0, 0))
        self.screen.blit(self.heart_layer, (0, 0))
        self.screen.blit(self.foreground_fx_layer, (0, 0))
        self.screen.blit(self.overlay_layer, (0, 0))

        # A black overlay creates the opening fade from darkness.
        self.draw_intro_fade(self.fade_layer)
        self.screen.blit(self.fade_layer, (0, 0))

        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()


if __name__ == "__main__":
    try:
        NeonHeartExperience().run()
    except Exception as exc:
        pygame.quit()
        print("\nThe program hit an unexpected error:")
        print(exc)
        print("\nCopy this error message and send it back so we can fix it.")
        input("Press Enter to close...")
        sys.exit(1)
