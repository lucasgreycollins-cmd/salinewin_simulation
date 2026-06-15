import pygame
import random
import sys
import math
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
            pygame.mixer.init()
        except Exception as e:
            print(f"Failed to initialize Pygame: {e}")
            sys.exit(1)
        
        # Create fullscreen window
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("SalineWin Simulation")
        self.clock = pygame.time.Clock()
        
        # Load audio
        try:
            self.sound = pygame.mixer.Sound(AUDIO_FILE)
        except Exception as e:
            print(f"Failed to load audio file: {e}")
            print(f"Make sure '{AUDIO_FILE}' is in the same directory as this script.")
            self.sound = None
        
        self.sound_playing = False
        
        # Font setup
        self.font_large = pygame.font.SysFont("courier", 48, bold=True)
        self.font_medium = pygame.font.SysFont("courier", 32)
        self.font_small = pygame.font.SysFont("courier", 16)
        
        # Animation state
        self.frame_count = 0
        self.running = True
        self.animation_started = False
        self.glitch_intensity = 0
        self.startup_delay_frames = FPS * 3  # 3 second delay before audio plays
        
        # Mouse trail tracking
        self.mouse_trail = []
        self.max_trail_length = 50
        
    def play_audio(self):
        """Start playing the audio file."""
        if self.sound and not self.sound_playing:
            self.sound.play()
            self.sound_playing = True
            self.animation_started = True
    
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
        
        # Auto-play audio after 3 second startup delay
        if not self.animation_started and self.frame_count >= self.startup_delay_frames:
            self.play_audio()
        
        # Track mouse position for trail
        mouse_pos = pygame.mouse.get_pos()
        self.mouse_trail.append(mouse_pos)
        if len(self.mouse_trail) > self.max_trail_length:
            self.mouse_trail.pop(0)
        
        # Check if audio is still playing
        if self.sound_playing and not pygame.mixer.get_busy():
            self.sound_playing = False
            # Loop the animation or wait
            if self.frame_count > FPS * 2:  # Wait 2 seconds before looping
                self.play_audio()
    
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
            pygame.draw.point(self.screen, color, (x, y))
    
    def draw_waves(self):
        """Draw wavy distortion effect."""
        if not self.animation_started or not self.sound_playing:
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
        """Draw a limited-speed rainbow flash over the whole window."""
        if not self.animation_started:
            return

        seconds = self.frame_count / FPS
        pulse = (math.sin(seconds * FLASHES_PER_SECOND * 2 * math.pi) + 1) / 2
        color_index = int(seconds * FLASHES_PER_SECOND) % 7
        color = self.get_rainbow_color(color_index * 52 - self.frame_count)

        flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        flash.fill(color)
        flash.set_alpha(int(35 + pulse * (FLASH_MAX_ALPHA - 35)))
        self.screen.blit(flash, (0, 0))
    
    def draw_screen_duplication(self):
        """Draw duplicated screen effect from top-left to bottom-left."""
        if not self.animation_started:
            return
        
        # Create a copy of the current screen
        screen_copy = self.screen.copy()
        
        # Draw the copied screen at different offsets
        offset_x = int(20 * math.sin(self.frame_count * 0.05))
        offset_y = int((SCREEN_HEIGHT // 2) * (0.5 + 0.5 * math.sin(self.frame_count * 0.02)))
        
        # Draw at bottom-left with transparency
        screen_copy.set_alpha(150)
        self.screen.blit(screen_copy, (offset_x, offset_y))
    
    def render(self):
        """Render the scene."""
        self.screen.fill(COLORS['bg'])
        
        # Draw effects in order
        self.draw_geometric_patterns()
        self.draw_waves()
        self.draw_noise()
        self.draw_screen_duplication()
        self.draw_rainbow_flash()
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
        
        # Auto-start the audio after warnings
        self.play_audio()
        
        print(f"SalineWin Simulation started")
        print(f"Press ESC to exit")
        
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    sim = SalineWinSimulation()
    sim.run()