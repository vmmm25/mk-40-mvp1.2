import subprocess
import os
import wave
import numpy as np
import sounddevice as sd
import tempfile
import threading
from pathlib import Path
from config import get_config

class PiperTTSProvider:
    def __init__(self):
        config = get_config()
        self.piper_path = config.get("piper_path", "")
        self.piper_model = config.get("piper_model", "")
        self.output_device = config.get("audio_output_device", None)
        
        if not self.piper_path or not os.path.exists(self.piper_path):
            raise FileNotFoundError(f"Piper executable not found at: {self.piper_path}")
            
        if not self.piper_model or not os.path.exists(self.piper_model):
            raise FileNotFoundError(f"Piper model not found at: {self.piper_model}")
            
        # Generar un archivo temporal para el audio de salida
        self.temp_wav = Path(tempfile.gettempdir()) / "piper_tts_output.wav"
        self._is_playing = False
        self._play_thread = None

    def speak(self, text: str, blocking: bool = False):
        """
        Sintetiza y reproduce texto.
        Si blocking=True, la llamada esperará a que termine de reproducir.
        """
        self.stop()  # Detener cualquier reproducción previa
        
        # Limpiar texto para evitar problemas con comillas en la shell
        text = text.replace('"', '\\"').replace('\n', ' ')
        if not text.strip():
            return

        try:
            # Invocar Piper usando subprocess y powershell para evitar problemas de piping en cmd normal
            cmd = f'powershell -Command "Write-Output \\"{text}\\" | & \\"{self.piper_path}\\" --model \\"{self.piper_model}\\" --output_file \\"{self.temp_wav}\\""'
            
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if self.temp_wav.exists():
                self._play_audio_file(str(self.temp_wav), blocking)
                
        except Exception as e:
            print(f"[TTS Piper Error] {e}")

    def _play_audio_file(self, filepath: str, blocking: bool):
        self._is_playing = True
        
        def _play():
            try:
                with wave.open(filepath, 'rb') as wf:
                    framerate = wf.getframerate()
                    channels = wf.getnchannels()
                    sampwidth = wf.getsampwidth()
                    
                    frames = wf.readframes(wf.getnframes())
                    
                    # Convert to numpy array for sounddevice
                    if sampwidth == 2:
                        dtype = np.int16
                    elif sampwidth == 4:
                        dtype = np.int32
                    elif sampwidth == 1:
                        dtype = np.uint8
                    else:
                        print("[TTS Piper Error] Formato de sample no soportado.")
                        return
                        
                    data = np.frombuffer(frames, dtype=dtype)
                    
                    if channels > 1:
                        data = data.reshape(-1, channels)
                    
                    # Asignar el dispositivo de salida configurado si existe
                    if self.output_device is not None:
                        sd.default.device[1] = self.output_device

                    # Play the audio
                    sd.play(data, samplerate=framerate)
                    sd.wait()
            except Exception as e:
                print(f"[TTS Playback Error] {e}")
            finally:
                self._is_playing = False

        self._play_thread = threading.Thread(target=_play, daemon=True)
        self._play_thread.start()
        
        if blocking:
            self._play_thread.join()

    def stop(self):
        """Detiene la reproducción actual."""
        if self._is_playing:
            sd.stop()
            self._is_playing = False
