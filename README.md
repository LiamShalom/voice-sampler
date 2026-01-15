# Voice Sampler

A command-line tool for generating and testing voice audio using ElevenLabs. Perfect for sampling different voices, tweaking settings, and saving recordings.

## Features

- 🎙️ Generate speech from any text phrase
- 🔄 Regenerate with one keypress to hear variations
- 🎤 Browse and switch between available voices
- ⚙️ Adjust voice settings (stability, similarity, style)
- 💾 Save recordings to `recordings/` folder
- ▶️ Replay audio without regenerating

## Setup

1. **Clone the repo and create a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your ElevenLabs API key:**
   
   Create a `.env` file in the project root:
   ```
   ELEVENLABS_API_KEY=your-api-key-here
   ```
   
   Get your API key from [ElevenLabs](https://elevenlabs.io/).

## Usage

### Web UI (Streamlit)

```bash
streamlit run app.py
```

This opens a web interface with:
- Voice selection dropdown
- Text input
- Settings sliders
- Audio player
- Download/save buttons

### Command Line

**Generate audio for a phrase:**
```bash
python main.py "Hello, this is a test!"
```

**Or run interactively:**
```bash
python main.py
```

**List available voices:**
```bash
python main.py --list-voices
```

## Interactive Options

After generating audio, you'll see these options:

| Key | Action |
|-----|--------|
| `r` | Regenerate with same phrase (different variation) |
| `p` | Play the audio again |
| `s` | Save to `recordings/` folder |
| `n` | Enter a new phrase |
| `v` | Change voice |
| `e` | Edit voice settings |
| `q` | Quit |

## Voice Settings

Adjust these parameters via the `e` option:

| Setting | Range | Description |
|---------|-------|-------------|
| **Stability** | 0.0 - 1.0 | Lower = more expressive, Higher = more consistent |
| **Similarity** | 0.0 - 1.0 | How closely it matches the original voice |
| **Style** | 0.0 - 1.0 | Style exaggeration (0 = neutral) |

## Requirements

- Python 3.8+
- ElevenLabs API key
- macOS (uses `afplay`), Linux (`aplay`), or Windows for audio playback
