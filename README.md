# SalineWin Simulation

A creative virus simulation project built with Python, Pygame, and Pillow. This is an artistic recreation inspired by retro virus simulations, featuring dynamic visual effects synchronized with audio.

## Features

- **Audio Playback**: Integrated M4A audio file with the original SalineWin sound
- **Glitch Effects**: Dynamic text glitching with color distortion
- **Visual Effects**:
  - Geometric rotating patterns
  - Wave distortion animations
  - CRT scanline effect
  - Random noise/static overlay
  - Real-time frame counter
- **Interactive Controls**:
  - SPACE: Start audio playback
  - ESC: Exit the simulation

## Requirements

- Python 3.7+
- Pygame 2.1.0+
- Pillow 9.0.0+

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure `SalineWin.m4a` is in the project directory

## Usage

Run the simulation:
```bash
python salinewin.py
```

Then press SPACE to start the audio and animation.

## Project Structure

```
salinewin_simulation/
├── salinewin.py          # Main application
├── SalineWin.m4a         # Audio file
├── requirements.txt      # Python dependencies
├── README.md             # This file
└── .gitignore           # Git ignore rules
```

## About

This project is part of a series of creative virus simulations that explore visual and audio effects using modern Python libraries. It's designed purely for educational and artistic purposes.

## License

This project is provided as-is for educational purposes.
