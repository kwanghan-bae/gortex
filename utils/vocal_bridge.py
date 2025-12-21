import os
import logging
from typing import Optional
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger("GortexVocalBridge")

class VocalBridge:
    """
    사용자의 음성을 이해하고 에이전트의 답변을 목소리로 변환하는 보컬 엔진.
    """
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if (OpenAI and self.api_key) else None

    def text_to_speech(self, text: str, output_path: str = "logs/response.mp3") -> bool:
        """텍스트를 음성으로 변환하여 파일로 저장"""
        if not self.client:
            logger.warning("OpenAI client not configured for TTS.")
            return False
            
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            response.stream_to_file(output_path)
            logger.info(f"🔊 Response converted to speech: {output_path}")
            return True
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            return False

    def speech_to_text(self, audio_path: str) -> Optional[str]:
        """음성 파일을 텍스트로 변환 (Whisper)"""
        if not self.client:
            return None
            
        try:
            with open(audio_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            return transcript.text
        except Exception as e:
            logger.error(f"STT failed: {e}")
            return None

    def play_audio(self, path: str):
        """저장된 음성 파일 재생 (시스템 명령어 활용)"""
        if os.path.exists(path):
            if os.name == 'posix': # macOS/Linux
                os.system(f"afplay {path} &") # Mac
                # os.system(f"play {path} &") # Linux (sox)
            elif os.name == 'nt': # Windows
                os.system(f"start /min powershell -c (New-Object Media.SoundPlayer '{path}').PlaySync()")
