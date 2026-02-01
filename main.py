# ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~ #
# A Pomodoro timer made with MicroPython on ESP32s
# ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~ #
#
# TODO:
#   1. Unify the UI
#   1.1. Single separator for all screens (Main-Content <-> Controls/Hint)
#   1.2. Single style ~ Gfx > text... more animations
#   1.3. IDLE: Coffee animation (steamy part)
#   1.4. WORK: Something progresive (digging a hole...)
#   1.5. BREAK: Quick break, but reminder that we are not finished yet
#   1.6. LBREAK: REWARD time!!! (jackpot maybe :D)
#   1.7. PAUSE: V. Insanity (world is stopped)
#   1.8. WAIT_W/B: Hyping user
# ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~ #
from machine import Pin, I2C, PWM
from ssd1306 import SSD1306_I2C, framebuf
import framebuf
import network
import socket
import json
import time
import sys
import os


image_clock_bits = bytearray(
    b"\x00?\xf0\x00\x00?\xf0\x00\x03\xc0\x0f\x00\x03\xc0\x0f\x00\x0c\xc3\x0c\xc0\x0c\xc3\x0c\xc00\x03\x0000\x03\x000<\x03\x00\xf0<\x03\x00\xf0\xc0\x03\x00\x0c\xc0\x03\x00\x0c\xc0\x03\x00\x0c\xc0\x03\x00\x0c\xfc\x03\x00\xfc\xfc\x03\x00\xfc\xc0\x00\xc0\x0c\xc0\x00\xc0\x0c\xc0\x000\x0c\xc0\x000\x0c<\x00\x0c\xf0<\x00\x0c\xf00\x00\x0000\x00\x000\x0c\xc3\x0c\xc0\x0c\xc3\x0c\xc0\x03\xc3\x0f\x00\x03\xc3\x0f\x00\x00?\xf0\x00\x00?\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00"
)
image_clockface_bits = bytearray(
    b"\x00?\xf0\x00\x00?\xf0\x00\x03\xc3\x0f\x00\x03\xc3\x0f\x00\x0c\xc3\x0c\xc0\x0c\xc3\x0c\xc00\x00\x0000\x00\x000<\x00\x00\xf0<\x00\x00\xf0\xc0\x00\x00\x0c\xc0\x00\x00\x0c\xc0\x00\x00\x0c\xc0\x00\x00\x0c\xfc\x03\x00\xfc\xfc\x03\x00\xfc\xc0\x00\x00\x0c\xc0\x00\x00\x0c\xc0\x00\x00\x0c\xc0\x00\x00\x0c<\x00\x00\xf0<\x00\x00\xf00\x00\x0000\x00\x000\x0c\xc3\x0c\xc0\x0c\xc3\x0c\xc0\x03\xc3\x0f\x00\x03\xc3\x0f\x00\x00?\xf0\x00\x00?\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00"
)

image_coffee_bits = bytearray(
    b"\x10\x00\x00\x00\x08\x00\x10\x00"
    b"\x02\x00\x04\x00\x12\x00\x10\x00"
    b"\x04\x00\x0a\x00\x07\x80\x0b\x60"
    b"\x00\x00\x1f\xf0\x75\x50\x9a\xb0"
    b"\x91\x10\x90\x10\x90\x10\x98\x30"
    b"\x54\x50\x3a\xb0\x35\x50\x1a\xb0"
    b"\x0f\xe0"
)

virtual_insanity = bytearray(
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1f\x00\x00\x00\x00\x00\xff\xc0\x00\x00\x00\x01\xff\xe0\x00\x00\x00\x01\xff\xe0\x00\x00\x00\x01\xff\xe0\x00\x00\x00\x01\xff\xf0\x00\x00\x00\x01\xff\xf0\x00\x00\x00\x03\xff\xe0\x00\x00\x00\x03\xff\xf8\x00\x00\x00\x03\xff\xfe\x00\x00\x00\x03\xff\xff\x00\x00\x00\x07\xff\xff\x00\x00\x00\x0f\xff\xfe\x00\x00\x00\x1f\xff\xfc\x00\x00\x00\x1f\xff\xf8\x00\x00\x00\x1f\xff\xfc\x00\x00\x00\x0f\xff\xfe\x00\x00\x00\x07\xff\xff\x00\x00\x00\x00?\xff\x00\x00\x00\x00?\xff\xc0\x00\x00\x00\xff\xff\xf0\x00\x00\x06\xff\xff\xfc\x00\x00\x03\xff\xff\xfe\x00\x00\x0f\xff\xff\xff\x00\x00\x1f\xff\xff\xff\x00\x00?\xff\xff\xff\x80\x00?\xff\xff\xff\xe0\x00?\xff\xff\xff\xf0\x00\x7f\xff\xff\xff\xf8\x00\x7f\xff\xff\xff\xfe\x00\x7f\xff\xff\xff\xff\x00\x7f\xff\xff\xff\xff\x80\xff\xff\xff\xff\xff\xe0\x7f\xff\xff\xff\xff\xf0\x7f\x7f\xff\xff\xff\xf8~\x7f\xff\xff\xff\xf8\x1c\x7f\xff\xff\xff\xfc\x00?\xff\xff\xff\xfc\x00?\xff\xff\xff\xfe\x00?\xff\xff\xff\xfe\x00?\xff\xff\xff\xfe\x00?\xff\xff\x7f\xfe\x00?\xff\xff?\xfe\x00?\xff\xff\x1f\xff\x00?\xff\xff\x1f\xff\x00?\xff\xff\x1f\xff\x00?\xff\xff\x0f\xff\x00?\xff\xff\x0f\xff\x00?\xff\xff\x07\xff\x00\x1f\xff\xff\x03\xfe\x00\x1f\xff\xff\x07\xfe\x00\x1f\xff\xff\x03\xff\x00\x1f\xff\xff\x03\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
)

image_play_bits = bytearray(
    b"?\xff\x80@\x00@\x80\x00 \x80\x00 \x81\x80 \x81\xc0 \x81\xe0 \x81\xf0 \x81\xf8 \x81\xfc \x81\xf8 \x81\xf0 \x81\xe0 \x81\xc0 \x81\x80 \x80\x00 \x80\x00 \xc0\x00`\x7f\xff\xc0?\xff\x80"
)


# ----------------------------------------------------------------------------------------->> Misc. ~utilities
def err_print(*args, **kwargs) -> None:
    """Print an error message to stderr"""
    print(*args, **kwargs, file=sys.stderr)


def oled_text_scaled(
    oled: SSD1306_I2C,
    text: str,
    x: int,
    y: int,
    scale: int,
    character_width=8,
    character_height=8,
) -> None:
    """A helper function for printing scaled text on SSD1306 display with I2C protocol"""
    # temporary buffer for the text
    width = character_width * len(text)
    height = character_height
    temp_buf = bytearray(width * height)
    temp_fb = framebuf.FrameBuffer(temp_buf, width, height, framebuf.MONO_VLSB)

    # write text to the temporary framebuffer
    temp_fb.text(text, 0, 0, 1)

    # scale and write to the display
    for i in range(width):
        for j in range(height):
            pixel = temp_fb.pixel(i, j)
            if pixel:  # If the pixel is set, draw a larger rectangle
                oled.fill_rect(x + i * scale, y + j * scale, scale, scale, 1)


def create_access_point() -> network.WLAN:
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid="pomodoro-esp32s", password="SECRET")
    return ap


SOUNDS = {
    "click": {"notes": [(1200, 0.05)]},
    "complete": {"notes": [(523, 0.15), (659, 0.15), (784, 0.15)]},
    "error": {"notes": [(800, 0.1), (600, 0.1), (400, 0.1)]},
    "pause": {"notes": [(600, 0.15)]},
    "resume": {"notes": [(1000, 0.08), (0, 0.05), (1000, 0.08)]},  # 0 = silence
    "celebration": {
        "notes": [
            (523, 0.12),
            (659, 0.12),
            (784, 0.12),
            (1047, 0.12),
            (784, 0.12),
            (1047, 0.12),
            (1319, 0.12),
        ]
    },
    "tick": {"notes": [(2000, 0.03)]},
}


class POMODORO_STATES:
    IDLE = "IDLE"
    SHORT_BREAK = "SHORT_BREAK"
    LONG_BREAK = "LONG_BREAK"
    WORK = "WORK"
    PAUSE = "PAUSE"
    WAIT_BREAK = "WAIT_BREAK"
    WAIT_WORK = "WAIT_WORK"


# ----------------------------------------------------------------------------------------->> Sys. Configuration
class Config:
    _CACHE_DELTA = 0
    _CACHE_TTL = 120
    _CACHE = None
    _LOCK_FILE = "config.lock"
    __slots__ = ["settings", "behavior", "timing"]

    def __init__(self) -> None:
        self.settings = self.Settings()
        self.behavior = self.Behavior()
        self.timing = self.Timing()

    @staticmethod
    def is_config_locked() -> bool:
        try:
            os.stat(Config._LOCK_FILE)
            return True
        except OSError:
            return False

    @staticmethod
    def from_dict(data: dict) -> Config:
        if not isinstance(data, dict):
            raise ValueError("Config data must be a dictionary")

        config = Config()

        if "timing" in data:
            t = data["timing"]
            if not isinstance(t, dict):
                raise ValueError("timing must be a dictionary")

            work = t.get("work", 25)
            short_break = t.get("short_break", 5)
            long_break = t.get("long_break", 15)

            # Validate ranges (1-120 minutes)
            if not (1 <= work <= 120):
                raise ValueError("work time must be 1-120 minutes")
            if not (1 <= short_break <= 60):
                raise ValueError("short break must be 1-60 minutes")
            if not (1 <= long_break <= 120):
                raise ValueError("long break must be 1-120 minutes")

            config.timing.work = work * 60
            config.timing.short_break = short_break * 60
            config.timing.long_break = long_break * 60

        if "behavior" in data:
            b = data["behavior"]
            if not isinstance(b, dict):
                raise ValueError("behavior must be a dictionary")
            config.behavior.auto_start_breaks = bool(b.get("auto_start_breaks", False))
            config.behavior.auto_start_work = bool(b.get("auto_start_work", False))

        if "settings" in data:
            s = data["settings"]
            if not isinstance(s, dict):
                raise ValueError("settings must be a dictionary")
            config.settings.sounds = bool(s.get("sounds", True))

        return config

    @staticmethod
    def read_config(timeout: int = 5) -> Config:
        start_delta = time.time()
        while Config.is_config_locked():
            if time.time() - start_delta > timeout:
                raise Exception("configuration read timeout")
            time.sleep(0.05)

        with open("config.json", encoding="utf-8", mode="r") as raw_config:
            json_config = json.load(raw_config)
            try:
                return Config.from_dict(json_config)
            except Exception as e:
                err_print(f"Failed to parse config: {e}")
                return Config()

    @staticmethod
    def get_config() -> Config:
        try:
            os.stat("config.json")
            file_exists = True
        except OSError:
            file_exists = False

        if not file_exists:
            config = Config()
            Config._CACHE = config
            Config._CACHE_DELTA = time.time()
            return config

        if (
            Config._CACHE is not None
            and time.time() - Config._CACHE_DELTA < Config._CACHE_TTL
        ):
            return Config._CACHE

        config = Config.read_config()
        Config._CACHE = config
        Config._CACHE_DELTA = time.time()

        return config

    @staticmethod
    def save_config(cfg: Config, timeout: int = 5) -> None:
        start_delta = time.time()
        while Config.is_config_locked():
            if time.time() - start_delta > timeout:
                raise Exception("configuration save timeout")
            time.sleep(0.05)

        Config._CACHE = None
        try:
            with open(Config._LOCK_FILE, "w") as f:
                f.write("locked")

            data = {
                "timing": {
                    "work": cfg.timing.work // 60,
                    "short_break": cfg.timing.short_break // 60,
                    "long_break": cfg.timing.long_break // 60,
                },
                "behavior": {
                    "auto_start_breaks": cfg.behavior.auto_start_breaks,
                    "auto_start_work": cfg.behavior.auto_start_work,
                },
                "settings": {"sounds": cfg.settings.sounds},
            }

            with open("config.json", "w") as f:
                json.dump(data, f)
        finally:
            try:
                os.remove(Config._LOCK_FILE)
            except OSError:
                pass

    class Timing:
        __slots__ = ["work", "short_break", "long_break"]

        def __init__(self) -> None:
            self.work = 25 * 60
            self.short_break = 5 * 60
            self.long_break = 15 * 60

    class Behavior:
        __slots__ = ["auto_start_breaks", "auto_start_work"]

        def __init__(self) -> None:
            self.auto_start_breaks = False
            self.auto_start_work = False

    class Settings:
        __slots__ = ["sounds"]

        def __init__(self) -> None:
            self.sounds = True


# ----------------------------------------------------------------------------------------->> POMODORO
class Pomodoro:
    def __init__(self) -> None:
        try:
            self.config = Config.get_config()
        except Exception as e:
            err_print(f"Failed to load config: {e}")
            self.config = Config()

        self.pomodoros: int = 0
        self.state: str = POMODORO_STATES.IDLE
        self.paused_state = None
        self.next_state = None
        self.start_time: float = time.time()
        self.duration: float = 0
        self.time_remaining: float = 0
        self.show_splash: bool = False

    def start(self):
        """Start a work session from IDLE"""
        if self.state == POMODORO_STATES.IDLE:
            self.state = POMODORO_STATES.WORK
            self.set_duration(POMODORO_STATES.WORK)
        # Start break from waiting state
        elif self.state == POMODORO_STATES.WAIT_BREAK:
            if self.next_state == POMODORO_STATES.SHORT_BREAK:
                self.state = POMODORO_STATES.SHORT_BREAK
                self.set_duration(POMODORO_STATES.SHORT_BREAK)
            else:
                self.state = POMODORO_STATES.LONG_BREAK
                self.set_duration(POMODORO_STATES.LONG_BREAK)
        # Start work from waiting state
        elif self.state == POMODORO_STATES.WAIT_WORK:
            self.state = POMODORO_STATES.WORK
            self.set_duration(POMODORO_STATES.WORK)

    def tick(self, hw: Hardware) -> None:
        """Check if time's up and transition to waiting states"""
        if self.state == POMODORO_STATES.PAUSE:
            return

        # Skip waiting states
        if (
            not self.config.behavior.auto_start_work
            and self.state is POMODORO_STATES.WAIT_WORK
        ):
            return

        if (
            not self.config.behavior.auto_start_breaks
            and self.state is POMODORO_STATES.WAIT_BREAK
        ):
            return

        elapsed = time.time() - self.start_time

        if elapsed >= self.duration:
            if self.state == POMODORO_STATES.WORK:
                self.pomodoros += 1
                hw.play_sound("complete")

                # Determine next break type
                if self.pomodoros % 4 == 0:
                    self.next_state = POMODORO_STATES.LONG_BREAK
                else:
                    self.next_state = POMODORO_STATES.SHORT_BREAK

                # Go to waiting state instead of starting break
                self.state = POMODORO_STATES.WAIT_BREAK

            elif self.state in [
                POMODORO_STATES.SHORT_BREAK,
                POMODORO_STATES.LONG_BREAK,
            ]:
                hw.play_sound("complete")
                # Go to waiting state instead of starting work
                self.state = POMODORO_STATES.WAIT_WORK

    def set_duration(self, state: str):
        """Set duration and reset start time for a new phase"""
        self.start_time = time.time()
        if state == POMODORO_STATES.WORK:
            self.duration = self.config.timing.work
        elif state == POMODORO_STATES.SHORT_BREAK:
            self.duration = self.config.timing.short_break
        else:
            self.duration = self.config.timing.long_break

    def pause(self):
        """Pause the current timer"""
        if self.state not in [
            POMODORO_STATES.PAUSE,
            POMODORO_STATES.IDLE,
            POMODORO_STATES.WAIT_BREAK,
            POMODORO_STATES.WAIT_WORK,
        ]:
            self.paused_state = self.state
            self.state = POMODORO_STATES.PAUSE
            self.time_remaining = self.duration - (time.time() - self.start_time)

    def resume(self):
        """Resume from pause"""
        if self.state == POMODORO_STATES.PAUSE:
            if self.paused_state:
                self.state = self.paused_state
            self.start_time = time.time()
            self.duration = self.time_remaining

    def get_remaining_time(self) -> tuple:
        """Returns (minutes, seconds) remaining"""
        if self.state == POMODORO_STATES.IDLE:
            return (0, 0)
        elif self.state == POMODORO_STATES.PAUSE:
            remaining = self.time_remaining
        elif self.state in [
            POMODORO_STATES.WAIT_BREAK,
            POMODORO_STATES.WAIT_WORK,
        ]:
            return (0, 0)  # No time shown in waiting state
        else:
            elapsed = time.time() - self.start_time
            remaining = max(0, self.duration - elapsed)

        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        return (minutes, seconds)


# ----------------------------------------------------------------------------------------->> Hardware
class Hardware:
    def __init__(self) -> None:
        self.buzzer = PWM(Pin(15), freq=1000, duty=0)
        self.start_btn = Pin(4, Pin.IN, Pin.PULL_UP)
        self.reset_btn = Pin(2, Pin.IN, Pin.PULL_UP)
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(21))
        self.oled = SSD1306_I2C(128, 64, self.i2c)
        self.prev_start_btn = 1  # Not pressed initially
        self.prev_reset_btn = 1

    def read_start_btn(self) -> bool:
        current = self.start_btn.value()
        if self.prev_start_btn == 1 and current == 0:  # Transition to pressed
            self.prev_start_btn = current
            return True
        self.prev_start_btn = current
        return False

    def read_reset_btn(self) -> bool:
        current = self.reset_btn.value()
        if self.prev_reset_btn == 1 and current == 0:  # Transition to pressed
            self.prev_reset_btn = current
            return True
        self.prev_reset_btn = current
        return False

    def update_display(self, state, minutes, seconds, pomodoros):
        cfg = UiCfg(state, minutes, seconds, pomodoros)
        self.oled.fill(0)

        if cfg.state == POMODORO_STATES.IDLE:
            UI.idle_screen(self.oled, cfg)
        elif cfg.state == POMODORO_STATES.WORK:
            UI.work_screen(self.oled, cfg)
        elif cfg.state == POMODORO_STATES.SHORT_BREAK:
            UI.short_break_screen(self.oled, cfg)
        elif cfg.state == POMODORO_STATES.LONG_BREAK:
            UI.long_break_screen(self.oled, cfg)
        elif cfg.state == POMODORO_STATES.PAUSE:
            UI.pause_screen(self.oled, cfg)
        elif cfg.state == POMODORO_STATES.WAIT_BREAK:
            UI.waiting_break_screen(self.oled, cfg)
        elif cfg.state == POMODORO_STATES.WAIT_WORK:
            UI.waiting_work_screen(self.oled, cfg)

    def play_sound(self, sound_name: str) -> None:
        if sound_name not in SOUNDS:
            return

        config = Config.get_config()
        if not config.settings.sounds:
            return

        try:
            self.buzzer.init(freq=1000, duty=0)
            for freq, duration in SOUNDS[sound_name]["notes"]:
                if freq == 0:  # Silence
                    self.buzzer.duty(0)
                else:
                    self.buzzer.freq(freq)
                    self.buzzer.duty(512)
                time.sleep(duration)
        finally:
            self.buzzer.duty(0)


# ----------------------------------------------------------------------------------------->> UI Config object
class UiCfg:
    __slots__ = ["state", "minutes", "seconds", "pomodoros"]

    def __init__(self, state=None, minutes=0, seconds=0, pomodoros=0) -> None:
        self.state = state
        self.minutes = minutes
        self.seconds = seconds
        self.pomodoros = pomodoros


# ----------------------------------------------------------------------------------------->> UI
class UI:
    @staticmethod
    def draw_line(oled: SSD1306_I2C, y: int) -> None:
        """Draw a horizontal line across the screen"""
        oled.hline(0, y, 128, 1)

    @staticmethod
    def draw_box(oled: SSD1306_I2C, x: int, y: int, w: int, h: int) -> None:
        """Draw a rectangle outline"""
        oled.rect(x, y, w, h, 1)

    @staticmethod
    def center_text(oled: SSD1306_I2C, text: str, y: int):
        """Center text horizontally on the display"""
        text_width = len(text) * 8
        x = (128 - text_width) // 2
        oled.text(text, x, y)

    @staticmethod
    def waiting_break_screen(oled: SSD1306_I2C, cfg: UiCfg) -> None:
        """Waiting to start break screen"""
        oled.fill(0)

        # Celebration
        UI.center_text(oled, "WORK DONE!", 10)
        UI.center_text(oled, "\\o/", 22)

        UI.draw_line(oled, 35)
        if cfg.pomodoros % 4 == 0:
            UI.center_text(oled, "Time for a", 38)
            UI.center_text(oled, "LONG BREAK!", 46)
        else:
            UI.center_text(oled, "Time for a", 38)
            UI.center_text(oled, "SHORT BREAK!", 46)

        UI.draw_line(oled, 54)
        UI.center_text(oled, "[A] Start Break", 56)
        oled.show()

    @staticmethod
    def waiting_work_screen(oled: SSD1306_I2C, cfg: UiCfg):
        """Waiting to start work screen"""
        oled.fill(0)

        # Encouragement
        UI.center_text(oled, "BREAK DONE!", 10)
        UI.center_text(oled, "Ready to", 26)
        UI.center_text(oled, "focus again?", 34)

        UI.draw_line(oled, 46)
        session_num = (cfg.pomodoros % 4) + 1
        session_text = f"Session #{session_num}/4"
        UI.center_text(oled, session_text, 48)

        UI.draw_line(oled, 54)
        UI.center_text(oled, "[A] Start Work", 56)
        oled.show()

    @staticmethod
    def splash_screen(oled: SSD1306_I2C, cfg: UiCfg):
        """Boot screen with title and version"""
        bits = [
            framebuf.FrameBuffer(image_clock_bits, 30, 32, framebuf.MONO_HLSB),
            framebuf.FrameBuffer(image_clockface_bits, 30, 32, framebuf.MONO_HLSB),
        ]

        for _ in range(3):
            idx = _ % 2
            oled.fill(0)
            oled.text("Quanta", 45, 26, 1)
            oled.text("pomodoro", 45, 36, 1)
            oled.blit(bits[idx], 13, 16)
            oled.show()
            time.sleep(1)

    @staticmethod
    def idle_screen(oled: SSD1306_I2C, cfg: UiCfg):
        """Ready/Idle screen"""
        # Top border
        UI.draw_line(oled, 0)
        for i in range(3):
            oled.pixel(i, 0, 0)
            oled.pixel(127 - i, 0, 0)

        # READY text centered
        UI.center_text(oled, "Ready to get", 20)
        UI.center_text(oled, "  things DONE?", 30)

        # Coffee cup icon
        coffee_bits = framebuf.FrameBuffer(
            image_coffee_bits, 12, 25, framebuf.MONO_HLSB
        )
        oled.blit(coffee_bits, 12, 32)

        # Bottom border with button hints
        UI.draw_line(oled, 56)
        for i in range(3):
            oled.pixel(i, 56, 0)
            oled.pixel(127 - i, 56, 0)

        oled.text("[A]Start", 10, 58)

        oled.show()

    @staticmethod
    def work_screen(oled: SSD1306_I2C, cfg: UiCfg) -> None:
        """Work/Focus timer screen"""
        # Header
        header = f"FOCUS       #{cfg.pomodoros}"
        oled.text(header, 0, 0)
        UI.draw_line(oled, 9)

        # Large timer
        time_str = f"{cfg.minutes:02d}:{cfg.seconds:02d}"
        oled_text_scaled(oled, time_str, 10, 15, 3, 8, 8)

        # Progress bar
        UI.draw_box(oled, 0, 42, 128, 8)
        # Calculate progress (25 minutes = 1500 seconds)
        config = Config.get_config()
        total_secs = config.timing.work
        elapsed = total_secs - (cfg.minutes * 60 + cfg.seconds)
        progress_width = int((elapsed / total_secs) * 124)
        if progress_width > 0:
            oled.fill_rect(2, 44, progress_width, 4, 1)

        # Bottom controls
        UI.draw_line(oled, 52)
        oled.text("[A]STOP [B]RESET", 0, 56)

        oled.show()

    @staticmethod
    def short_break_screen(oled, cfg):
        """Short break timer screen"""
        # Header
        UI.center_text(oled, "SHORT BREAK", 0)
        UI.draw_line(oled, 9)

        # Large timer
        time_str = f"{cfg.minutes:02d}:{cfg.seconds:02d}"
        oled_text_scaled(oled, time_str, 10, 15, 3, 8, 8)
        config = Config.get_config()

        # Progress bar
        UI.draw_box(oled, 0, 42, 128, 8)
        total_secs = config.timing.short_break
        elapsed = total_secs - (cfg.minutes * 60 + cfg.seconds)
        progress_width = int((elapsed / total_secs) * 124)
        if progress_width > 0:
            oled.fill_rect(2, 44, progress_width, 4, 1)

        # Bottom text
        UI.draw_line(oled, 52)
        UI.center_text(oled, "~ RELAX ~", 56)

        oled.show()

    @staticmethod
    def long_break_screen(oled: SSD1306_I2C, cfg: UiCfg):
        """Long break timer screen"""
        # Header
        UI.center_text(oled, "LONG BREAK", 0)
        UI.draw_line(oled, 9)

        # Large timer
        time_str = f"{cfg.minutes:02d}:{cfg.seconds:02d}"
        oled_text_scaled(oled, time_str, 10, 15, 3, 8, 8)

        # Progress bar
        UI.draw_box(oled, 0, 42, 128, 8)
        config = Config.get_config()
        total_secs = config.timing.long_break
        elapsed = total_secs - (cfg.minutes * 60 + cfg.seconds)
        progress_width = int((elapsed / total_secs) * 124)
        if progress_width > 0:
            oled.fill_rect(2, 44, progress_width, 4, 1)

        # Bottom text
        UI.draw_line(oled, 52)
        UI.center_text(oled, "~ RELAX ~", 56)

        oled.show()

    @staticmethod
    def pause_screen(oled: SSD1306_I2C, cfg: UiCfg):
        """Paused screen"""
        # bg_f8f8f8_flat_750x_075_f_pad_750x1000_f8f8f8
        vi_bits = framebuf.FrameBuffer(virtual_insanity, 48, 64, framebuf.MONO_HLSB)
        oled.blit(vi_bits, 2, -5)
        oled.text("PAUSED", 62, 37, 1)
        oled.line(0, 54, 127, 54, 1)

        fb_image_play_bits = framebuf.FrameBuffer(
            image_play_bits, 19, 20, framebuf.MONO_HLSB
        )
        oled.blit(fb_image_play_bits, 76, 13)
        oled.text("[A]STOP", 0, 56)
        oled.show()


hw = Hardware()
pomodoro = Pomodoro()

ap = create_access_point()
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
s.setblocking(False)

while True:
    # non-blocking http server
    try:
        cl, addr = s.accept()
        request = cl.recv(1024).decode()
        if "POST /" in request:
            try:
                parts = request.split("\r\n\r\n")
                if len(parts) < 2:
                    raise ValueError("No body")

                body = parts[1]
                if not body.strip():
                    raise ValueError("Empty body")

                data = json.loads(body)
                config = Config.from_dict(data)
                Config.save_config(config)
                pomodoro = Pomodoro()

                response = json.dumps({"status": "success"})
                cl.send(
                    "HTTP/1.1 201 CREATED\r\nContent-Type: application/json\r\n\r\n"
                )
                cl.send(response)

            except (ValueError, Exception) as e:
                error_response = json.dumps({"error": str(e)})
                cl.send(
                    "HTTP/1.1 400 Bad Request\r\nContent-Type: application/json\r\n\r\n"
                )
                cl.send(error_response)
        elif "GET /config" in request:
            config = Config.get_config()
            response = json.dumps(
                {
                    "work": config.timing.work // 60,
                    "short_break": config.timing.short_break // 60,
                    "long_break": config.timing.long_break // 60,
                    "auto_start_breaks": config.behavior.auto_start_breaks,
                    "auto_start_work": config.behavior.auto_start_work,
                    "sounds": config.settings.sounds,
                }
            )
            cl.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
            cl.send(response)
        cl.close()
    except OSError:
        pass

    # Handle start/pause button
    if hw.read_start_btn():
        if pomodoro.state == POMODORO_STATES.IDLE:
            hw.play_sound("celebration")
            hw.oled.fill(0)
            UI.splash_screen(hw.oled, UiCfg(pomodoro.state, 0, 0, pomodoro.pomodoros))
            pomodoro.start()
        elif pomodoro.state == POMODORO_STATES.PAUSE:
            hw.play_sound("resume")
            pomodoro.resume()
        elif pomodoro.state == POMODORO_STATES.WAIT_BREAK:
            hw.play_sound("complete")
            pomodoro.start()
        elif pomodoro.state == POMODORO_STATES.WAIT_WORK:
            hw.play_sound("complete")
            pomodoro.start()
        else:
            hw.play_sound("pause")
            pomodoro.pause()

    # Handle reset button
    if hw.read_reset_btn():
        hw.play_sound("error")
        pomodoro = Pomodoro()  # Reset everything

    # Check timer
    pomodoro.tick(hw)

    # Update display
    mins, secs = pomodoro.get_remaining_time()
    hw.update_display(pomodoro.state, mins, secs, pomodoro.pomodoros)
