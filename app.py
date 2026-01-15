"""
Voice Sampler - Streamlit UI
A web interface for generating audio using ElevenLabs.
"""

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from elevenlabs import ElevenLabs, VoiceSettings

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")

# Page config
st.set_page_config(
    page_title="Voice Sampler",
    page_icon="🎙️",
    layout="centered",
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    .voice-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background: #1e1e1e;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_client():
    """Initialize ElevenLabs client."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        st.error("❌ ELEVENLABS_API_KEY not found in .env file")
        st.stop()
    return ElevenLabs(api_key=api_key)


@st.cache_data(ttl=300)
def get_voices(_client):
    """Fetch available voices (cached for 5 minutes)."""
    response = _client.voices.get_all()
    return [(v.voice_id, v.name, getattr(v, 'category', 'unknown')) for v in response.voices]


def generate_audio(client, text: str, voice_id: str, settings: dict) -> bytes:
    """Generate audio from text."""
    voice_settings = VoiceSettings(
        stability=settings["stability"],
        similarity_boost=settings["similarity"],
        style=settings["style"],
        use_speaker_boost=True,
        speed=settings["speed"],
    )
    
    audio_generator = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings=voice_settings,
    )
    
    return b"".join(audio_generator)


def save_recording(audio_data: bytes, filename: str) -> Path:
    """Save audio to recordings folder."""
    recordings_dir = Path(__file__).parent / "recordings"
    recordings_dir.mkdir(exist_ok=True)
    save_path = recordings_dir / f"{filename}.mp3"
    save_path.write_bytes(audio_data)
    return save_path


# Main UI
st.title("🎙️ Voice Sampler")
st.caption("Generate and test voice audio using ElevenLabs")

# Initialize client
client = get_client()
voices = get_voices(client)

# Create voice options
voice_options = {f"{name} ({category})": vid for vid, name, category in voices}

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Voice Settings")
    
    stability = st.slider(
        "Stability",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05,
        help="Lower = more expressive, Higher = more consistent"
    )
    
    similarity = st.slider(
        "Similarity",
        min_value=0.0,
        max_value=1.0,
        value=0.75,
        step=0.05,
        help="How closely it matches the original voice"
    )
    
    style = st.slider(
        "Style",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.05,
        help="Style exaggeration (0 = neutral)"
    )
    
    speed = st.slider(
        "Speed",
        min_value=0.7,
        max_value=1.2,
        value=1.0,
        step=0.05,
        help="Speaking speed (0.7 = slow, 1.0 = normal, 1.2 = fast)"
    )
    
    st.divider()
    
    if st.button("Refresh Voices", use_container_width=True):
        get_voices.clear()
        st.rerun()

# Main content
selected_voice = st.selectbox(
    "🎤 Select Voice",
    options=list(voice_options.keys()),
    index=0,
)

phrase = st.text_area(
    "📝 Enter phrase to generate",
    placeholder="Hello, this is a test of the voice sampler...",
    height=100,
)

col1, col2 = st.columns(2)

with col1:
    generate_btn = st.button("🎙️ Generate", type="primary", use_container_width=True)

with col2:
    regenerate_btn = st.button("🔄 Regenerate", use_container_width=True)

# Generate audio
if generate_btn or regenerate_btn:
    if not phrase.strip():
        st.warning("Please enter a phrase to generate.")
    else:
        voice_id = voice_options[selected_voice]
        settings = {
            "stability": stability,
            "similarity": similarity,
            "style": style,
            "speed": speed,
        }
        
        with st.spinner("Generating audio..."):
            try:
                audio_data = generate_audio(client, phrase.strip(), voice_id, settings)
                st.session_state.audio_data = audio_data
                st.session_state.last_phrase = phrase.strip()
            except Exception as e:
                st.error(f"Error generating audio: {e}")

# Display audio player if we have audio
if "audio_data" in st.session_state:
    st.divider()
    st.subheader("▶️ Generated Audio")
    st.audio(st.session_state.audio_data, format="audio/mp3")
    
    # Save section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        save_name = st.text_input(
            "Filename",
            placeholder="my_recording",
            label_visibility="collapsed",
        )
    
    with col2:
        if st.button("💾 Save", use_container_width=True):
            if save_name.strip():
                save_path = save_recording(st.session_state.audio_data, save_name.strip())
                st.success(f"Saved to {save_path}")
            else:
                st.warning("Enter a filename")
    
    # Download button
    st.download_button(
        label="⬇️ Download MP3",
        data=st.session_state.audio_data,
        file_name="voice_sample.mp3",
        mime="audio/mp3",
        use_container_width=True,
    )
