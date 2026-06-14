import pygame
import random
import sys
import math
from PIL import ImageGrab, Image, ImageDraw, ImageFilter

# ── Configuration ──────────────────────────────────────────────────────────────
FPS = 60
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
AUDIO_FILE = "SalineWin.m4a"

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
        
        # Initialize audio state
        self.sound = None
        self.sound_playing = False
        
        # Load audio
        try:
            self.sound = pygame.mixer.Sound(AUDIO_FILE)
        except Exception as e:
            print(f"Failed to load audio file: {e}")
            print(f"Make sure '{AUDIO_FILE}' is in the same directory as this script.")
        
        # Font setup
        self.font_large = pygame.font.SysFont("courier", 48, bold=True)
        self.font_medium = pygame.font.SysFont("courier", 32)
        self.font_small = pygame.font.SysFont("courier", 16)
        
        # Animation state
        self.frame_count = 0
        self.running = True
        self.animation_started = False
        self.glitch_intensity = 0
        
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
                elif event.key == pygame.K_SPACE:
                    self.play_audio()
    
    def update(self):
        """Update animation state."""
        self.frame_count += 1
        
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
            # Initial state - waiting for audio
            self.draw_glitch_text("SALINEWIN SIMULATION", 100, 100, self.font_large, COLORS['cyan'])
            self.draw_glitch_text("Press SPACE to start", 100, 200, self.font_medium, COLORS['text'])
            self.draw_glitch_text("Press ESC to exit", 100, 260, self.font_medium, COLORS['text'])
        else:
            # During animation
            self.draw_glitch_text("SYSTEM PROCESSING...", 100, 100, self.font_large, COLORS['magenta'])
            
            # Display frame count and audio status
            status = "Audio: PLAYING" if self.sound_playing else "Audio: IDLE"
            self.draw_glitch_text(status, 100, SCREEN_HEIGHT - 100, self.font_small, COLORS['glitch_green'])
            
            frame_text = f"Frame: {self.frame_count}"
            self.draw_glitch_text(frame_text, 100, SCREEN_HEIGHT - 50, self.font_small, COLORS['text'])
    
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
    
    def render(self):
        """Render the scene."""
        self.screen.fill(COLORS['bg'])
        
        # Draw effects in order
        self.draw_geometric_patterns()
        self.draw_waves()
        self.draw_noise()
        self.draw_status_text()
        self.draw_scanlines()
        
        pygame.display.flip()
    
    def run(self):
        """Main loop."""
        print(f"SalineWin Simulation started")
        print(f"Press SPACE to start audio, ESC to exit")
        
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
