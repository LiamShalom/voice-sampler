#!/usr/bin/env python3
"""
Voice Sampler - Generate audio from text using ElevenLabs
Allows regeneration until you're happy with the result.
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from elevenlabs import ElevenLabs, VoiceSettings

# Load environment variables from .env file
load_dotenv(Path(__file__).parent / ".env")


def get_api_key() -> str:
    """Get ElevenLabs API key from environment."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("Error: ELEVENLABS_API_KEY environment variable not set.")
        print("Set it with: export ELEVENLABS_API_KEY='your-api-key'")
        sys.exit(1)
    return api_key


def play_audio(file_path: str) -> None:
    """Play audio file using system player."""
    if sys.platform == "darwin":
        subprocess.run(["afplay", file_path], check=True)
    elif sys.platform == "linux":
        subprocess.run(["aplay", file_path], check=True)
    elif sys.platform == "win32":
        import winsound
        winsound.PlaySound(file_path, winsound.SND_FILENAME)
    else:
        print(f"Audio saved to: {file_path}")
        print("Automatic playback not supported on this platform.")


def get_voices(client: ElevenLabs) -> list:
    """Get all available voices."""
    response = client.voices.get_all()
    return response.voices


def list_voices(client: ElevenLabs) -> None:
    """List all available voices."""
    print("\n🎤 Available Voices:\n")
    print(f"{'#':<4} {'Name':<25} {'Voice ID':<25} {'Category'}")
    print("─" * 75)
    
    voices = get_voices(client)
    for i, voice in enumerate(voices, 1):
        category = getattr(voice, 'category', 'unknown')
        print(f"{i:<4} {voice.name:<25} {voice.voice_id:<25} {category}")
    
    print()


def select_voice(client: ElevenLabs, current_voice: str) -> str:
    """Interactive voice selection. Returns selected voice ID."""
    voices = get_voices(client)
    
    print("\n🎤 Available Voices:\n")
    print(f"{'#':<4} {'Name':<25} {'Category'}")
    print("─" * 50)
    
    for i, voice in enumerate(voices, 1):
        category = getattr(voice, 'category', 'unknown')
        marker = " ◀" if voice.voice_id == current_voice else ""
        print(f"{i:<4} {voice.name:<25} {category}{marker}")
    
    print("\nEnter number to select, or press Enter to keep current:")
    choice = input("Voice #: ").strip()
    
    if choice and choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(voices):
            selected = voices[idx]
            print(f"✅ Selected: {selected.name}")
            return selected.voice_id
        else:
            print("Invalid number, keeping current voice.")
    
    return current_voice


def generate_audio(
    client: ElevenLabs,
    text: str,
    voice: str = "bIHbv24MWmeRgasZH58o",
    settings: dict = None,
) -> bytes:
    """Generate audio from text using ElevenLabs."""
    settings = settings or {}
    
    print(f"\n🎙️  Generating audio for: \"{text}\"")
    print(f"   Voice: {voice}")
    print(f"   Stability: {settings.get('stability', 0.5):.2f}")
    print(f"   Similarity: {settings.get('similarity_boost', 0.75):.2f}")
    print(f"   Style: {settings.get('style', 0.0):.2f}")
    
    voice_settings = VoiceSettings(
        stability=settings.get("stability", 0.5),
        similarity_boost=settings.get("similarity_boost", 0.75),
        style=settings.get("style", 0.0),
        use_speaker_boost=settings.get("use_speaker_boost", True),
    )
    
    audio_generator = client.text_to_speech.convert(
        voice_id=voice,
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings=voice_settings,
    )
    
    # Collect all audio chunks
    audio_data = b"".join(audio_generator)
    return audio_data


def print_settings(settings: dict) -> None:
    """Print current voice settings."""
    print("\n⚙️  Current Settings:")
    print(f"   Stability:  {settings.get('stability', 0.5):.2f}  (0=variable, 1=stable)")
    print(f"   Similarity: {settings.get('similarity_boost', 0.75):.2f}  (0=diverse, 1=close to original)")
    print(f"   Style:      {settings.get('style', 0.0):.2f}  (0=neutral, 1=exaggerated)")


def main():
    # Initialize client first for --list-voices
    api_key = get_api_key()
    client = ElevenLabs(api_key=api_key)
    
    # Check for --list-voices flag
    if len(sys.argv) > 1 and sys.argv[1] == "--list-voices":
        list_voices(client)
        sys.exit(0)
    
    # Get phrase from command line or prompt
    if len(sys.argv) > 1:
        phrase = " ".join(sys.argv[1:])
    else:
        phrase = input("Enter the phrase to generate: ").strip()
        if not phrase:
            print("No phrase provided. Exiting.")
            sys.exit(1)
    
    # Create temp directory for audio files
    temp_dir = tempfile.mkdtemp(prefix="voice_sampler_")
    audio_path = Path(temp_dir) / "output.mp3"
    
    # Current voice
    current_voice = "bIHbv24MWmeRgasZH58o"
    
    # Voice settings (adjustable)
    settings = {
        "stability": 0.5,
        "similarity_boost": 0.75,
        "style": 0.0,
        "use_speaker_boost": True,
    }
    
    generation_count = 0
    
    while True:
        generation_count += 1
        
        try:
            # Generate audio
            audio_data = generate_audio(client, phrase, voice=current_voice, settings=settings)
            
            # Save to file
            with open(audio_path, "wb") as f:
                f.write(audio_data)
            
            print(f"\n▶️  Playing audio (generation #{generation_count})...")
            play_audio(str(audio_path))
            
        except Exception as e:
            print(f"\n❌ Error generating audio: {e}")
            retry = input("Try again? [y/n]: ").strip().lower()
            if retry == "y":
                continue
            else:
                break
        
        # Ask user what to do next
        print("\n" + "─" * 40)
        print("Options:")
        print("  [r] Regenerate with same phrase")
        print("  [p] Play again")
        print("  [s] Save to file")
        print("  [n] New phrase")
        print("  [v] Change voice")
        print("  [e] Edit voice settings")
        print("  [q] Quit")
        
        while True:
            choice = input("\nYour choice: ").strip().lower()
            
            if choice == "r":
                print("\n🔄 Regenerating...")
                break
            
            elif choice == "p":
                print("\n▶️  Playing again...")
                play_audio(str(audio_path))
            
            elif choice == "s":
                save_name = input("Save as (filename without extension): ").strip()
                if save_name:
                    recordings_dir = Path.cwd() / "recordings"
                    recordings_dir.mkdir(exist_ok=True)
                    save_path = recordings_dir / f"{save_name}.mp3"
                    with open(audio_path, "rb") as src:
                        with open(save_path, "wb") as dst:
                            dst.write(src.read())
                    print(f"✅ Saved to: {save_path}")
            
            elif choice == "n":
                phrase = input("Enter new phrase: ").strip()
                if phrase:
                    generation_count = 0
                    break
                print("No phrase entered.")
            
            elif choice == "v":
                current_voice = select_voice(client, current_voice)
                print("\n🔄 Regenerating with new voice...")
                break
            
            elif choice == "e":
                print_settings(settings)
                print("\nEnter new values (0.0-1.0) or press Enter to keep current:")
                
                val = input(f"  Stability [{settings['stability']:.2f}]: ").strip()
                if val:
                    settings["stability"] = max(0.0, min(1.0, float(val)))
                
                val = input(f"  Similarity [{settings['similarity_boost']:.2f}]: ").strip()
                if val:
                    settings["similarity_boost"] = max(0.0, min(1.0, float(val)))
                
                val = input(f"  Style [{settings['style']:.2f}]: ").strip()
                if val:
                    settings["style"] = max(0.0, min(1.0, float(val)))
                
                print_settings(settings)
                print("\n🔄 Regenerating with new settings...")
                break
            
            elif choice == "q":
                print("\n👋 Goodbye!")
                # Cleanup temp file
                if audio_path.exists():
                    audio_path.unlink()
                os.rmdir(temp_dir)
                sys.exit(0)
            
            else:
                print("Invalid choice. Please enter r, p, s, n, v, e, or q.")
    
    # Cleanup
    if audio_path.exists():
        audio_path.unlink()
    os.rmdir(temp_dir)


if __name__ == "__main__":
    main()
