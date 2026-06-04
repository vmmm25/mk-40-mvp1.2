import asyncio
import threading
import logging
import sounddevice as sd
import re
from contextlib import asynccontextmanager
from pathlib import Path

from google.genai import types

from memory.memory_manager import load_memory, update_memory, format_memory_for_prompt
from memory.config_manager import load_config
from tools.declarations import TOOL_DECLARATIONS
from tools import TOOL_IMPLEMENTATIONS
from engine.events import engine_stop
from engine.audio import find_fallback_device

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "core" / "prompt.txt"

LIVE_MODEL = "models/gemini-2.5-flash-native-audio-preview-12-2025"
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

def _load_system_prompt() -> str:
    try:
        return PROMPT_PATH.read_text(encoding="utf-8")
    except Exception:
        return (
            "You are JARVIS, Tony Stark's AI assistant running MARK XL. "
            "Be concise, direct, and always use the provided tools to complete tasks. "
            "Never simulate or guess results — always call the appropriate tool. "
            "You have access to the user's computer. Use desktop/browser/file tools as needed. "
            "Respond in the same language the user speaks to you."
        )

async def _execute_tool(name: str, args: dict, ui) -> str:
    """Execute a tool by name and args. Returns result string."""
    logger.info(f"Tool called: {name} args={args}")
    ui.set_state("THINKING")

    if name == "save_memory":
        category = args.get("category", "notes")
        key = args.get("key", "")
        value = args.get("value", "")
        if key and value:
            update_memory({category: {key: {"value": value}}})
            logger.info(f"save_memory: {category}/{key} = {value}")
        if not getattr(ui, "muted", False):
            ui.set_state("LISTENING")
        return "ok"

    result = "Done."
    try:
        handler = TOOL_IMPLEMENTATIONS.get(name)
        if handler:
            result = handler(args, ui) or "Done."
        else:
            result = f"Unknown tool: {name}"

    except Exception as e:
        result = f"Tool '{name}' failed: {e}"
        logger.exception(f"Tool execution failed: {name}")
        ui.write_log(f"ERR: {name} — {str(e)[:120]}")

    if not getattr(ui, "muted", False):
        ui.set_state("LISTENING")

    logger.info(f"Tool Result ({name}): {str(result)[:80]}")
    return result


class JarvisLive:
    """Gemini Live real-time audio session."""

    def __init__(self, ui, provider):
        self.ui = ui
        self.provider = provider
        self.session = None
        self.audio_in_queue = None
        self.out_queue = None
        self._loop = None
        self._is_speaking = False
        self._speaking_lock = threading.Lock()
        self.ui.on_text_command = self._on_text_command
        self._turn_done_event = None

    def _on_text_command(self, text: str):
        if not self._loop or not self.session or engine_stop.is_set():
            return
        cfg = load_config()
        if not cfg.get("llm_active", True):
            self.ui.write_log("SYS: El motor LLM está desactivado. Actívalo para enviar comandos.")
            return
        asyncio.run_coroutine_threadsafe(
            self.session.send_client_content(
                turns={"parts": [{"text": text}]},
                turn_complete=True
            ),
            self._loop
        )

    def set_speaking(self, value: bool):
        with self._speaking_lock:
            self._is_speaking = value
        if value:
            self.ui.set_state("SPEAKING")
        elif not getattr(self.ui, "muted", False):
            self.ui.set_state("LISTENING")

    async def _send_realtime(self):
        while not engine_stop.is_set():
            try:
                msg = await asyncio.wait_for(self.out_queue.get(), timeout=1.0)
                await self.session.send_realtime_input(media=msg)
            except asyncio.TimeoutError:
                continue

    async def _listen_audio(self):
        logger.info("Mic started")
        loop = asyncio.get_event_loop()

        def callback(indata, frames, time_info, status):
            cfg = load_config()
            if not cfg.get("llm_active", True):
                return
            with self._speaking_lock:
                jarvis_speaking = self._is_speaking
            if not jarvis_speaking and not getattr(self.ui, "muted", False):
                data = indata.tobytes()
                try:
                    self.ui._win.hud.push_audio_chunk(data)
                except Exception:
                    pass
                def _put_audio(data):
                    try:
                        self.out_queue.put_nowait({"data": data, "mime_type": "audio/pcm"})
                    except asyncio.QueueFull:
                        pass
                loop.call_soon_threadsafe(_put_audio, data)

        try:
            mic_cfg = load_config().get("audio_input_device")
            if isinstance(mic_cfg, int) and mic_cfg == 0:
                import platform
                if platform.system() == "Windows":
                    logger.warning("audio_input_device=0 is the Windows Sound Mapper — using system default mic instead.")
                    mic_dev = None
                else:
                    mic_dev = 0
            elif isinstance(mic_cfg, int):
                mic_dev = mic_cfg
            else:
                mic_dev = None

            dev_name = str(sd.query_devices(mic_dev or sd.default.device[0])["name"]) if mic_dev is not None else "system default"
            logger.info(f"Using mic: {dev_name} (device={mic_dev})")

            try:
                stream = sd.InputStream(
                    samplerate=SEND_SAMPLE_RATE,
                    channels=CHANNELS,
                    dtype="int16",
                    blocksize=CHUNK_SIZE,
                    callback=callback,
                    device=mic_dev,
                )
            except sd.PortAudioError as pa_err:
                if "Invalid sample rate" in str(pa_err) and mic_dev is not None:
                    fallback = find_fallback_device(mic_dev, "input", SEND_SAMPLE_RATE, CHANNELS)
                    logger.warning(f"Mic device {mic_dev} doesn't support {SEND_SAMPLE_RATE}Hz. Falling back to device index {fallback}.")
                    mic_dev = fallback
                    stream = sd.InputStream(
                        samplerate=SEND_SAMPLE_RATE,
                        channels=CHANNELS,
                        dtype="int16",
                        blocksize=CHUNK_SIZE,
                        callback=callback,
                        device=mic_dev,
                    )
                else:
                    raise

            with stream:
                logger.info("Mic stream open")
                while not engine_stop.is_set():
                    await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Mic: {e}")
            raise

    async def _receive_audio(self):
        logger.info("Recv started")
        out_buf, in_buf = [], []
        _CTRL_RE = re.compile(r"<ctrl\d+>", re.IGNORECASE)

        def clean(t: str) -> str:
            return _CTRL_RE.sub("", re.sub(r"[\x00-\x08\x0b-\x1f]", "", t)).strip()

        try:
            while not engine_stop.is_set():
                async for response in self.session.receive():
                    if response.data:
                        if self._turn_done_event and self._turn_done_event.is_set():
                            self._turn_done_event.clear()
                        self.audio_in_queue.put_nowait(response.data)

                    if response.server_content:
                        sc = response.server_content
                        if sc.output_transcription and sc.output_transcription.text:
                            txt = clean(sc.output_transcription.text)
                            if txt:
                                out_buf.append(txt)

                        if sc.input_transcription and sc.input_transcription.text:
                            txt = clean(sc.input_transcription.text)
                            if txt:
                                in_buf.append(txt)

                        if sc.turn_complete:
                            if self._turn_done_event:
                                self._turn_done_event.set()

                            full_in = " ".join(in_buf).strip()
                            if full_in:
                                self.ui.write_log(f"You: {full_in}")
                            in_buf = []

                            full_out = " ".join(out_buf).strip()
                            if full_out:
                                self.ui.write_log(f"Jarvis: {full_out}")
                            out_buf = []

                    if response.tool_call:
                        fn_responses = []
                        for fc in response.tool_call.function_calls:
                            logger.info(f"Calling tool via Gemini Live: {fc.name}")
                            result = await _execute_tool(fc.name, dict(fc.args or {}), self.ui)
                            fn_responses.append(types.FunctionResponse(
                                id=fc.id, name=fc.name,
                                response={"result": result}
                            ))
                        await self.session.send_tool_response(
                            function_responses=fn_responses
                        )
        except Exception as e:
            logger.exception("Recv error")
            raise

    async def _play_audio(self):
        logger.info("Play started")
        cfg = load_config()
        spk_cfg = cfg.get("audio_output_device")
        import platform as _platform
        if isinstance(spk_cfg, int) and spk_cfg in (0, 2) and _platform.system() == "Windows":
            logger.warning("audio_output_device is a Windows Sound Mapper — using system default speaker.")
            spk_dev = None
        elif isinstance(spk_cfg, int):
            spk_dev = spk_cfg
        else:
            spk_dev = None
        vol = max(0, min(100, cfg.get("audio_volume", 80))) / 100.0
        try:
            stream = sd.RawOutputStream(
                samplerate=RECEIVE_SAMPLE_RATE,
                channels=CHANNELS,
                dtype="int16",
                blocksize=CHUNK_SIZE,
                device=spk_dev,
            )
        except sd.PortAudioError as pa_err:
            if "Invalid sample rate" in str(pa_err) and spk_dev is not None:
                fallback = find_fallback_device(spk_dev, "output", RECEIVE_SAMPLE_RATE, CHANNELS)
                logger.warning(f"Speaker device {spk_dev} doesn't support {RECEIVE_SAMPLE_RATE}Hz. Falling back to device index {fallback}.")
                spk_dev = fallback
                stream = sd.RawOutputStream(
                    samplerate=RECEIVE_SAMPLE_RATE,
                    channels=CHANNELS,
                    dtype="int16",
                    blocksize=CHUNK_SIZE,
                    device=spk_dev,
                )
            else:
                raise
        stream.start()

        from array import array
        try:
            while not engine_stop.is_set():
                try:
                    chunk = await asyncio.wait_for(
                        self.audio_in_queue.get(),
                        timeout=0.2
                    )
                except asyncio.TimeoutError:
                    if self.audio_in_queue.empty():
                        self.set_speaking(False)
                    continue
                self.set_speaking(True)
                if vol < 1.0:
                    data = array('h', chunk)
                    data = array('h', (int(s * vol) for s in data))
                    chunk = data.tobytes()
                await asyncio.to_thread(stream.write, chunk)
        except Exception as e:
            logger.exception("Play error")
            raise
        finally:
            self.set_speaking(False)
            stream.stop()
            stream.close()

    async def _shutdown_monitor(self):
        try:
            while not engine_stop.is_set():
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            pass
        finally:
            if self.session:
                try:
                    await self.session.close()
                except Exception:
                    pass

    @asynccontextmanager
    async def _build_live_session(self):
        from datetime import datetime
        memory = load_memory()
        mem_str = format_memory_for_prompt(memory)
        sys_prompt = _load_system_prompt()
        now = datetime.now()
        time_str = now.strftime("%A, %B %d, %Y — %I:%M %p")

        parts = [
            f"[CURRENT DATE & TIME]\nRight now it is: {time_str}\n"
            f"Use this to calculate exact times for reminders.\n\n"
        ]
        if mem_str:
            parts.append(mem_str)
        parts.append(sys_prompt)

        async with self.provider.create_live_session({
            "system_prompt": "\n".join(parts),
            "tools": TOOL_DECLARATIONS,
            "memory_str": mem_str if mem_str else "",
        }) as session:
            yield session

    async def run(self):
        while not engine_stop.is_set():
            try:
                logger.info(f"Connecting to Gemini Live with model: {LIVE_MODEL}...")
                self.ui.set_state("THINKING")

                async with self._build_live_session() as session:
                    try:
                        async with asyncio.TaskGroup() as tg:
                            self.session = session
                            self._loop = asyncio.get_event_loop()
                            self.audio_in_queue = asyncio.Queue()
                            self.out_queue = asyncio.Queue(maxsize=10)
                            self._turn_done_event = asyncio.Event()

                            logger.info("Connected to Gemini Live.")
                            self.ui.set_state("LISTENING")
                            self.ui.write_log("SYS: JARVIS online (Gemini Live Audio).")

                            tg.create_task(self._send_realtime())
                            tg.create_task(self._listen_audio())
                            tg.create_task(self._receive_audio())
                            tg.create_task(self._play_audio())
                            tg.create_task(self._shutdown_monitor())
                    except* Exception as ex_group:
                        for e in ex_group.exceptions:
                            if engine_stop.is_set():
                                continue
                            try:
                                from google.genai.errors import APIError
                                if isinstance(e, APIError) and "1000" in str(e):
                                    continue
                            except Exception:
                                pass

                            logger.exception("Task error in live session")
                            self.ui.write_log(f"SYS: Task error: {e}")

            except Exception as e:
                logger.exception("Connection failed")
                self.ui.write_log(f"SYS: Connection error: {e}")

            self.set_speaking(False)
            self.ui.set_state("THINKING")
            logger.info("Reconnecting in 3s...")
            for _ in range(30):
                if engine_stop.is_set():
                    break
                await asyncio.sleep(0.1)

    async def stop(self):
        engine_stop.set()
