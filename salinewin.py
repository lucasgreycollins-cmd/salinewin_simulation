import pygame
import random
import sys
import math
import os
import subprocess
from PIL import ImageGrab, Image, ImageDraw, ImageFilter
from tkinter import messagebox
import tkinter as tk

# ── Configuration ──────────────────────────────────────────────────────────────
FPS = 60
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
AUDIO_FILE = r"C:\Users\lucas\Music\SalineWin.m4a"
FLASHES_PER_SECOND = 1.5
FLASH_MAX_ALPHA = 120
INTRO_MESSAGE_SECONDS = 5
INTRO_FADE_SECONDS = 1
AUDIO_PLAY_COUNT = 3
INTRO_MESSAGES = [
    ["hello! and thank you for downloading this program. :)"],
    [
        "If you have epilepsy please leave by clicking the escape",
        "button on your computer. But if you don't have epilepsy",
        "enjoy!",
    ],
    [
        "Lucas Collins presents",
        "salinewin.exe, a simulation of a malware",
    ],
    ["enjoy the simulation"],
]

# ── Color Palette ──────────────────────────────────────────────────────────────
COLORS = {
    'bg': (0, 0, 0),
    'text': (255, 255, 255),
    'glitch_red': (255, 50, 50),
    'glitch_green': (50, 255, 50),
    'glitch_blue': (50, 50, 255),
    'cyan': (0, 255, 255),
    'magenta': (255, 0, 255),
}

class SalineWinSimulation:
    def __init__(self):
        try:
            pygame.init()
        except Exception as e:
            print(f"Failed to initialize Pygame: {e}")
            sys.exit(1)

        self.mixer_ready = False
        try:
            pygame.mixer.init()
            self.mixer_ready = True
        except Exception as e:
            print(f"Pygame audio could not start: {e}")

        self.desktop_image, self.blurred_desktop = self.capture_desktop()

        # Create fullscreen window
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("SalineWin Simulation")
        self.clock = pygame.time.Clock()
        self.tunnel_layers = [
            pygame.transform.smoothscale(
                self.desktop_image,
                (int(SCREEN_WIDTH * scale), int(SCREEN_HEIGHT * scale)),
            )
            for scale in (0.82, 0.64, 0.48, 0.34, 0.22)
        ]
        self.blurred_center = pygame.transform.smoothscale(
            self.blurred_desktop,
            (360, 360),
        )
        
        self.audio_backend = None
        self.audio_process = None
        self.sound_playing = False
        self.audio_finished = False
        self.load_audio()
        
        # Font setup
        self.font_large = pygame.font.SysFont("courier", 48, bold=True)
        self.font_medium = pygame.font.SysFont("courier", 32)
        self.font_small = pygame.font.SysFont("courier", 16)
        
        # Animation state
        self.frame_count = 0
        self.running = True
        self.animation_started = False
        self.intro_active = True
        self.intro_frame = 0
        self.glitch_intensity = 0
        self.stars = [
            (
                random.randrange(SCREEN_WIDTH),
                random.randrange(SCREEN_HEIGHT),
                random.choice((1, 1, 1, 2, 2, 3)),
                random.random() * math.tau,
                random.uniform(0.02, 0.06),
            )
            for _ in range(350)
        ]
        
        # Mouse trail tracking
        self.mouse_trail = []
        self.max_trail_length = 50

    def pil_to_surface(self, image):
        """Turn a Pillow image into a Pygame image."""
        image = image.convert("RGB")
        return pygame.image.fromstring(image.tobytes(), image.size, "RGB")

    def capture_desktop(self):
        """Capture the desktop before the animation window appears."""
        try:
            resampling = getattr(Image, "Resampling", Image)
            desktop = ImageGrab.grab().resize(
                (SCREEN_WIDTH, SCREEN_HEIGHT),
                resampling.LANCZOS,
            )
            blurred = desktop.filter(ImageFilter.GaussianBlur(radius=18))
            return self.pil_to_surface(desktop), self.pil_to_surface(blurred)
        except Exception as e:
            print(f"Could not capture the desktop: {e}")
            fallback = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fallback.fill(COLORS["bg"])
            return fallback, fallback.copy()
        
    def load_audio_with_windows(self):
        """Use Windows' modern media engine for M4A playback."""
        if not os.path.isfile(AUDIO_FILE):
            print(f"Audio file was not found: {AUDIO_FILE}")
            self.audio_backend = None
            return False

        self.audio_backend = "windows_media"
        print("Audio will play with Windows Media.")
        return True

    def load_audio(self):
        """Load the M4A with Pygame or Windows as a backup."""
        if self.mixer_ready:
            try:
                pygame.mixer.music.load(AUDIO_FILE)
                self.audio_backend = "pygame"
                print("Audio loaded with Pygame.")
                return
            except Exception as e:
                print(f"Pygame could not load the M4A: {e}")

        self.load_audio_with_windows()

    def play_audio(self):
        """Play the audio exactly three times."""
        if self.sound_playing or self.audio_finished:
            return

        if self.audio_backend == "pygame":
            try:
                pygame.mixer.music.play(loops=AUDIO_PLAY_COUNT - 1)
                self.sound_playing = True
            except Exception as e:
                print(f"Pygame could not play the M4A: {e}")
                if self.load_audio_with_windows():
                    self.play_audio()
        elif self.audio_backend == "windows_media":
            escaped_path = AUDIO_FILE.replace("'", "''")
            parent_pid = os.getpid()
            script = (
                "Add-Type -AssemblyName PresentationCore; "
                "$player = New-Object System.Windows.Media.MediaPlayer; "
                f"$player.Open([Uri]::new('{escaped_path}')); "
                "$player.Volume = 1.0; "
                "Start-Sleep -Milliseconds 500; "
                "$player.Play(); "
                "$plays = 0; "
                f"while (Get-Process -Id {parent_pid} -ErrorAction SilentlyContinue) {{ "
                "Start-Sleep -Milliseconds 200; "
                "if ($player.NaturalDuration.HasTimeSpan -and "
                "$player.Position -ge $player.NaturalDuration.TimeSpan) { "
                "$plays++; "
                f"if ($plays -ge {AUDIO_PLAY_COUNT}) {{ break }}; "
                "$player.Position = [TimeSpan]::Zero; $player.Play() } }; "
                "$player.Close()"
            )
            try:
                self.audio_process = subprocess.Popen(
                    [
                        "powershell.exe",
                        "-NoProfile",
                        "-STA",
                        "-WindowStyle",
                        "Hidden",
                        "-Command",
                        script,
                    ],
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                self.sound_playing = True
            except Exception as e:
                print(f"Windows Media could not play the audio: {e}")
    
    def handle_events(self):
        """Handle user input and window events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def update(self):
        """Update animation state."""
        self.frame_count += 1

        if self.intro_active:
            self.intro_frame += 1
            total_intro_frames = len(INTRO_MESSAGES) * INTRO_MESSAGE_SECONDS * FPS
            if self.intro_frame >= total_intro_frames:
                self.intro_active = False
                self.animation_started = True
                self.frame_count = 0
                self.play_audio()
            return

        if (
            self.animation_started
            and self.audio_backend
            and not self.sound_playing
            and not self.audio_finished
        ):
            self.play_audio()
        
        # Track mouse position for trail
        mouse_pos = pygame.mouse.get_pos()
        self.mouse_trail.append(mouse_pos)
        if len(self.mouse_trail) > self.max_trail_length:
            self.mouse_trail.pop(0)
        
        # Mark the audio finished after all three plays.
        if (
            self.sound_playing
            and self.audio_backend == "pygame"
            and not pygame.mixer.music.get_busy()
        ):
            self.sound_playing = False
            self.audio_finished = True
        elif (
            self.sound_playing
            and self.audio_backend == "windows_media"
            and self.audio_process
            and self.audio_process.poll() is not None
        ):
            self.sound_playing = False
            self.audio_finished = True
    
    def draw_glitch_text(self, text, x, y, font, color):
        """Draw text with glitch effect."""
        # Main text
        text_surf = font.render(text, True, color)
        self.screen.blit(text_surf, (x, y))
        
        # Glitch effect - offset copies with different colors
        if self.animation_started and random.random() > 0.85:
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-3, 3)
            
            glitch_colors = [COLORS['glitch_red'], COLORS['glitch_green'], COLORS['glitch_blue']]
            glitch_color = random.choice(glitch_colors)
            
            glitch_surf = font.render(text, True, glitch_color)
            glitch_surf.set_alpha(150)
            self.screen.blit(glitch_surf, (x + offset_x, y + offset_y))
    
    def draw_scanlines(self):
        """Draw CRT scanline effect."""
        if not self.animation_started:
            return
        
        line_height = 2
        for y in range(0, SCREEN_HEIGHT, line_height * 2):
            pygame.draw.line(self.screen, (0, 0, 0), (0, y), (SCREEN_WIDTH, y), 1)
    
    def draw_noise(self):
        """Draw random noise/static."""
        if not self.animation_started:
            return
        
        noise_alpha = int(50 * (self.glitch_intensity / 100))
        for _ in range(500):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            color = (
                random.randint(200, 255),
                random.randint(200, 255),
                random.randint(200, 255)
            )
            self.screen.set_at((x, y), color)
    
    def draw_waves(self):
        """Draw wavy distortion effect."""
        if not self.animation_started:
            return
        
        # Get audio level for dynamic effect
        amplitude = 15
        frequency = 0.02
        
        # Create surface with wave effect
        for y in range(0, SCREEN_HEIGHT, 4):
            offset = int(amplitude * math.sin(frequency * y + self.frame_count * 0.2))
            pygame.draw.line(
                self.screen,
                (random.randint(100, 150), random.randint(100, 150), random.randint(100, 150)),
                (offset, y),
                (SCREEN_WIDTH + offset, y),
                2
            )
    
    def draw_status_text(self):
        """Draw status text on screen."""
        if not self.animation_started:
            # Show black screen during 3 second startup delay
            return
        
        # During animation
        self.draw_glitch_text("SYSTEM PROCESSING...", 100, 100, self.font_large, COLORS['magenta'])
        
        # Display frame count and audio status
        status = "Audio: PLAYING" if self.sound_playing else "Audio: IDLE"
        self.draw_glitch_text(status, 100, SCREEN_HEIGHT - 100, self.font_small, COLORS['glitch_green'])
        
        frame_text = f"Frame: {self.frame_count}"
        self.draw_glitch_text(frame_text, 100, SCREEN_HEIGHT - 50, self.font_small, COLORS['text'])
        
        # Show exit tip
        self.draw_glitch_text("Press ESC or close window to exit", 100, SCREEN_HEIGHT - 150, self.font_small, COLORS['cyan'])
    
    def draw_geometric_patterns(self):
        """Draw animated geometric patterns."""
        if not self.animation_started:
            return
        
        # Draw rotating lines from center
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        num_lines = 12
        for i in range(num_lines):
            angle = (self.frame_count * 0.05 + (i * 2 * math.pi / num_lines))
            length = 300 + 100 * math.sin(self.frame_count * 0.03)
            
            end_x = center_x + length * math.cos(angle)
            end_y = center_y + length * math.sin(angle)
            
            color_idx = (i + self.frame_count // 10) % 3
            colors = [COLORS['glitch_red'], COLORS['glitch_green'], COLORS['glitch_blue']]
            
            pygame.draw.line(self.screen, colors[color_idx], (center_x, center_y), (end_x, end_y), 2)
    
    def get_rainbow_color(self, index):
        """Generate rainbow color based on index."""
        hue = (index + self.frame_count) % 360
        # Simple rainbow: red -> yellow -> green -> cyan -> blue -> magenta -> red
        rainbow_colors = [
            (255, 0, 0),      # red
            (255, 127, 0),    # orange
            (255, 255, 0),    # yellow
            (0, 255, 0),      # green
            (0, 255, 255),    # cyan
            (0, 0, 255),      # blue
            (255, 0, 255),    # magenta
        ]
        return rainbow_colors[hue // 52]
    
    def draw_mouse_trail(self):
        """Draw trail of mouse cursors."""
        if not self.animation_started or len(self.mouse_trail) == 0:
            return
        
        for i, pos in enumerate(self.mouse_trail):
            # Alpha increases towards the current position
            alpha = int(255 * (i / len(self.mouse_trail)))
            
            # Draw cursor symbol at each trail position
            color = self.get_rainbow_color(i)
            
            # Draw a small circle for cursor trail
            pygame.draw.circle(self.screen, color, pos, 5)
            
            # Draw crosshair
            pygame.draw.line(self.screen, color, (pos[0] - 10, pos[1]), (pos[0] + 10, pos[1]), 1)
            pygame.draw.line(self.screen, color, (pos[0], pos[1] - 10), (pos[0], pos[1] + 10), 1)

    def draw_rainbow_flash(self):
        """Draw bright moving rainbow bands over the whole window."""
        if not self.animation_started:
            return

        seconds = self.frame_count / FPS
        pulse = (math.sin(seconds * FLASHES_PER_SECOND * 2 * math.pi) + 1) / 2
        rainbow_colors = [
            (255, 0, 0),
            (255, 127, 0),
            (255, 255, 0),
            (0, 255, 0),
            (0, 255, 255),
            (0, 0, 255),
            (255, 0, 255),
        ]
        band_height = math.ceil(SCREEN_HEIGHT / len(rainbow_colors))
        color_shift = int(seconds * FLASHES_PER_SECOND) % len(rainbow_colors)

        rainbow = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for band_number in range(len(rainbow_colors)):
            color = rainbow_colors[(band_number + color_shift) % len(rainbow_colors)]
            y = band_number * band_height
            pygame.draw.rect(
                rainbow,
                color,
                (0, y, SCREEN_WIDTH, band_height + 1),
            )

        rainbow.set_alpha(int(90 + pulse * (FLASH_MAX_ALPHA - 20)))
        self.screen.blit(rainbow, (0, 0))
    
    def draw_screen_duplication(self):
        """Draw a spinning tunnel made from copies of the desktop."""
        if not self.animation_started:
            return

        center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.screen.blit(self.desktop_image, (0, 0))

        base_angle = (self.frame_count * 1.2) % 360

        for layer_number, copy in enumerate(self.tunnel_layers):
            angle = base_angle * (1 if layer_number % 2 == 0 else -1)
            angle += layer_number * 14
            spinning_copy = pygame.transform.rotate(copy, angle)
            self.screen.blit(spinning_copy, spinning_copy.get_rect(center=center))

        # Put a soft, circular blurred copy in the middle of the tunnel.
        blur_size = 360
        blurred = pygame.transform.rotate(self.blurred_center, -base_angle * 0.7)
        blurred = pygame.transform.smoothscale(blurred, (blur_size, blur_size))

        circle = pygame.Surface((blur_size, blur_size), pygame.SRCALPHA)
        circle.blit(blurred, (0, 0))
        mask = pygame.Surface((blur_size, blur_size), pygame.SRCALPHA)
        mask.fill((255, 255, 255, 0))
        pygame.draw.circle(
            mask,
            (255, 255, 255, 255),
            (blur_size // 2, blur_size // 2),
            blur_size // 2,
        )
        circle.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.screen.blit(circle, circle.get_rect(center=center))

    def draw_space_background(self):
        """Draw a dark space background with twinkling stars."""
        self.screen.fill((1, 2, 12))

        for x, y, radius, phase, speed in self.stars:
            brightness = int(
                130 + 125 * (math.sin(self.intro_frame * speed + phase) + 1) / 2
            )
            color = (brightness, brightness, min(255, brightness + 20))
            pygame.draw.circle(self.screen, color, (x, y), radius)

    def draw_intro(self):
        """Show each intro message with a fade in and fade out."""
        message_frames = INTRO_MESSAGE_SECONDS * FPS
        fade_frames = INTRO_FADE_SECONDS * FPS
        message_index = min(self.intro_frame // message_frames, len(INTRO_MESSAGES) - 1)
        frame_in_message = self.intro_frame % message_frames

        if frame_in_message < fade_frames:
            alpha = int(255 * frame_in_message / fade_frames)
        elif frame_in_message >= message_frames - fade_frames:
            frames_left = message_frames - frame_in_message
            alpha = int(255 * frames_left / fade_frames)
        else:
            alpha = 255

        lines = INTRO_MESSAGES[message_index]

        if message_index == 2:
            move_frames = 2 * FPS
            move_progress = min(frame_in_message / move_frames, 1)
            top_y = int(
                SCREEN_HEIGHT // 2
                - 55 * (1 - math.cos(move_progress * math.pi)) / 2
            )

            second_line_start = FPS
            second_alpha = max(
                0,
                min(255, int((frame_in_message - second_line_start) * 255 / FPS)),
            )
            second_alpha = min(second_alpha, alpha)

            title = self.font_medium.render(lines[0], True, COLORS["text"])
            title.set_alpha(alpha)
            self.screen.blit(
                title,
                title.get_rect(center=(SCREEN_WIDTH // 2, top_y)),
            )

            subtitle = self.font_medium.render(lines[1], True, COLORS["text"])
            subtitle.set_alpha(second_alpha)
            self.screen.blit(
                subtitle,
                subtitle.get_rect(
                    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 55)
                ),
            )
            return

        line_height = self.font_medium.get_linesize()
        first_y = SCREEN_HEIGHT // 2 - (len(lines) * line_height) // 2

        for line_number, line in enumerate(lines):
            text = self.font_medium.render(line, True, COLORS['text'])
            text.set_alpha(alpha)
            text_rect = text.get_rect(
                center=(SCREEN_WIDTH // 2, first_y + line_number * line_height)
            )
            self.screen.blit(text, text_rect)
    
    def render(self):
        """Render the scene."""
        self.screen.fill(COLORS['bg'])

        if self.intro_active:
            self.draw_space_background()
            self.draw_intro()
            pygame.display.flip()
            return

        # Draw the spinning desktop tunnel, then add lighter effects on top.
        self.draw_screen_duplication()
        self.draw_geometric_patterns()
        self.draw_noise()
        self.draw_status_text()
        self.draw_mouse_trail()
        self.draw_scanlines()
        
        pygame.display.flip()
    
    def run(self):
        """Main loop."""
        # Create a hidden root window for message boxes
        root = tk.Tk()
        root.withdraw()
        
        # Safety warning before any flashing begins.
        result1 = messagebox.askyesno(
            "Flashing Lights Warning",
            "This simulation contains flashing rainbow colors.\n\n"
            "Flashing lights can cause seizures or make some people feel sick. "
            "Do not run it if you or someone nearby may be sensitive.\n\n"
            "Continue?"
        )
        if not result1:
            root.destroy()
            pygame.quit()
            sys.exit()
        
        # Make it clear that this program is a visual simulation.
        result2 = messagebox.askyesno(
            "Start Simulation",
            "This is a visual simulation and will not destroy your computer.\n\n"
            "Press ESC at any time to stop. Start now?"
        )
        if not result2:
            root.destroy()
            pygame.quit()
            sys.exit()
        
        root.destroy()
        
        print(f"SalineWin Simulation started")
        print(f"Press ESC to exit")
        
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

        if self.audio_process and self.audio_process.poll() is None:
            self.audio_process.terminate()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    sim = SalineWinSimulation()
    sim.run()
