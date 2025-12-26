import os
import logging
import wave
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
        self.is_active = False
        self.voice_map = {
            "manager": "alloy",
            "planner": "fable",
            "coder": "onyx",
            "analyst": "nova",
            "researcher": "shimmer",
            "security": "echo"
        }

    def text_to_speech(self, text: str, agent_name: str = "manager", output_path: str = "logs/response.mp3") -> bool:
        """텍스트를 음성으로 변환하여 파일로 저장 (에이전트 고유 목소리 반영)"""
        if not self.client:
            return False
            
        try:
            voice = self.voice_map.get(agent_name.lower(), "alloy")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            response.stream_to_file(output_path)
            logger.info(f"🔊 {agent_name.upper()} ({voice}): {output_path}")
            return True
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            return False

    def record_audio(self, duration: int = 5, output_path: str = "logs/input.wav") -> str:
        """마이크로부터 음성을 녹음함"""
        try:
            import pyaudio
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100
            
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
            
            logger.info(f"🎤 Listening for {duration} seconds...")
            frames = []
            for _ in range(0, int(RATE / CHUNK * duration)):
                data = stream.read(CHUNK)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            wf = wave.open(output_path, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            return output_path
        except Exception as e:
            logger.error(f"Recording failed: {e}")
            return ""

    def speech_to_text(self, audio_path: str) -> Optional[str]:
        """음성 파일을 텍스트로 변환 (Whisper)"""
        if not self.client or not os.path.exists(audio_path):
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

    def map_to_command(self, text: str) -> str:
        """인식된 텍스트를 시스템 명령어로 변환"""
        if not text: return ""
        
        text = text.lower().strip()
        # 1. 명시적 슬래시 명령어 감지
        if text.startswith("/") or "slash" in text:
            return text.replace("slash ", "/").replace(" ", "")
            
        # 2. 자연어 명령어 매핑
        mappings = {
            "도움말": "/help", "help": "/help",
            "상태": "/status", "status": "/status",
            "정리": "/clear", "clear": "/clear",
            "인덱스": "/index", "reindex": "/index",
            "에이전트": "/agents", "agents": "/agents"
        }
        
        for k, v in mappings.items():
            if k in text:
                return v
                
        return text

    def play_audio(self, path: str):
        """저장된 음성 파일 재생"""
        if os.path.exists(path):
            if os.name == 'posix':
                os.system(f"afplay {path} &")
            elif os.name == 'nt':
                os.system(f"start /min powershell -c (New-Object Media.SoundPlayer '{path}').PlaySync()")