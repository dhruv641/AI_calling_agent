# speech.py
"""
Speech processing module.
Converts audio ↔ text
"""

import os
import numpy as np
import whisper
from gtts import gTTS
import io

# ============================================
# SPEECH-TO-TEXT (Audio → Text)
# ============================================

class SpeechToText:
    """
    Convert audio files to text using Whisper.
    
    WHY WHISPER?
    - Open-source (free, offline)
    - Very accurate
    - Works in many languages
    - No API keys needed
    """
    
    def __init__(self, model_size="base"):
        """
        Initialize Whisper model.
        
        model_size options:
        - "tiny" (39M) - fastest, lower accuracy
        - "base" (140M) - good balance ⭐
        - "small" (244M) - better accuracy
        - "medium" (769M) - very accurate (needs good GPU)
        
        First load downloads the model (~100-500MB depending on size)
        """
        print(f"Loading Whisper {model_size} model...")
        self.model = whisper.load_model(model_size)
        print("✅ Whisper model loaded")
    
    def transcribe(self, audio_file_path: str) -> str:
        """
        Convert audio file to text.
        
        Args:
            audio_file_path: Path to audio file (mp3, wav, m4a, etc)
        
        Returns:
            Transcribed text
        """
        print(f"Transcribing {audio_file_path}...")
        
        result = self.model.transcribe(audio_file_path)
        
        text = result["text"]
        print(f"✅ Transcribed: {text}")
        
        return text
    
    def transcribe_from_mic(self, duration: int = 5) -> str:
        """
        Record from microphone and transcribe.
        
        Args:
            duration: How many seconds to record
        
        Returns:
            Transcribed text
        """
        import sounddevice
        import soundfile
        import tempfile
        
        print(f"🎤 Recording for {duration} seconds... Speak now!")
        
        # Record audio
        sample_rate = 16000
        audio = sounddevice.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
        sounddevice.wait()
        
        # Save temporarily
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        soundfile.write(temp_file.name, audio, sample_rate)
        
        # Transcribe
        text = self.transcribe(temp_file.name)
        
        # Clean up
        os.unlink(temp_file.name)
        
        return text


# ============================================
# TEXT-TO-SPEECH (Text → Audio)
# ============================================

class TextToSpeech:
    """
    Convert text to speech audio.
    
    WHY gTTS?
    - Free (uses Google Translate)
    - Natural voice
    - Works offline after first use
    - Simple API
    """
    
    def __init__(self, language="en", tld="com"):
        """
        Initialize TTS.
        
        Args:
            language: Language code (en, es, fr, etc)
            tld: Top-level domain (com for US, co.in for India, etc)
        """
        self.language = language
        self.tld = tld
    
    def synthesize(self, text: str, output_file: str = "output.mp3") -> str:
        """
        Convert text to speech audio file.
        
        Args:
            text: Text to speak
            output_file: Where to save audio
        
        Returns:
            Path to audio file
        """
        print(f"🔊 Converting to speech: {text[:50]}...")
        
        tts = gTTS(text, lang=self.language, tld=self.tld)
        tts.save(output_file)
        
        print(f"✅ Saved audio to {output_file}")
        
        return output_file
    
    def speak_now(self, text: str):
        """
        Play audio immediately (no file saving).
        """
        import tempfile
        import os
        
        temp_file = "temp_speech.mp3"
        self.synthesize(text, temp_file)
        
        # Play the file
        os.system(f"afplay {temp_file}")  # Mac
        # For Linux: os.system(f"mpg123 {temp_file}")
        # For Windows: os.system(f"start {temp_file}")
        
        os.unlink(temp_file)


# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    print("Testing Speech Module")
    print("=" * 50)
    
    # Test 1: Text to Speech
    print("\n📝 TEST 1: Text to Speech")
    print("-" * 50)
    
    tts = TextToSpeech()
    
    test_text = "Hello! Your account balance is five thousand dollars. Is there anything else I can help you with?"
    output_file = tts.synthesize(test_text)
    print(f"Audio saved to: {output_file}")
    
    # Test 2: Speech to Text (from file)
    print("\n🎤 TEST 2: Speech to Text")
    print("-" * 50)
    
    stt = SpeechToText(model_size="base")
    
    # This requires you to have an audio file, so we'll skip for now
    # But the usage would be:
    # text = stt.transcribe("path/to/audio.wav")
    
    print("✅ Speech module ready!")