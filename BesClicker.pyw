import time
import threading
import tkinter as tk
import webbrowser
import ctypes
import sys
from pynput import mouse
import pyautogui

# =======================
# Varsayılan Ayarlar
# =======================
BUTTON = "left"
TRIGGER_CLICKS = 3
TRIGGER_WINDOW = 0.5
AUTOCLICK_DURATION = 1.0
AUTOCLICK_INTERVAL = 0.01

pyautogui.FAILSAFE = True
click_times = []
running = False
listener_thread = None
listener_running = False
listener_instance = None  # Stop için gerekli

is_windows = sys.platform.startswith("win")

if is_windows:
    PUL = ctypes.POINTER(ctypes.c_ulong)

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [
            ("dx", ctypes.c_long),
            ("dy", ctypes.c_long),
            ("mouseData", ctypes.c_ulong),
            ("dwFlags", ctypes.c_ulong),
            ("time", ctypes.c_ulong),
            ("dwExtraInfo", PUL),
        ]

    class INPUT(ctypes.Structure):
        class _I(ctypes.Union):
            _fields_ = [("mi", MOUSEINPUT)]

        _fields_ = [("type", ctypes.c_ulong), ("ii", _I)]

    INPUT_MOUSE = 0
    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    MOUSEEVENTF_RIGHTDOWN = 0x0008
    MOUSEEVENTF_RIGHTUP = 0x0010

    _extra = ctypes.c_ulong(0)

    def send_input_click(button):
        if button == "right":
            down_flag = MOUSEEVENTF_RIGHTDOWN
            up_flag = MOUSEEVENTF_RIGHTUP
        else:
            down_flag = MOUSEEVENTF_LEFTDOWN
            up_flag = MOUSEEVENTF_LEFTUP

        for flag in (down_flag, up_flag):
            mi = MOUSEINPUT(0, 0, 0, flag, 0, ctypes.pointer(_extra))
            inp = INPUT(INPUT_MOUSE, INPUT._I(mi=mi))
            ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))


def auto_clicker():
    global running
    end_time = time.time() + AUTOCLICK_DURATION
    running = True
    status_label.config(text="Auto clicking started! / Otomatik tıklama başladı!")
    while time.time() < end_time:
        if is_windows:
            send_input_click(BUTTON)
        else:
            pyautogui.click(button=BUTTON)

        if AUTOCLICK_INTERVAL > 0:
            time.sleep(AUTOCLICK_INTERVAL)

    running = False
    status_label.config(text="Auto clicking finished! / Otomatik tıklama bitti.")

def on_click(x, y, button, pressed):
    if pressed and not running:
        now = time.time()
        click_times.append(now)
        while click_times and now - click_times[0] > TRIGGER_WINDOW:
            click_times.pop(0)
        if len(click_times) >= TRIGGER_CLICKS:
            threading.Thread(target=auto_clicker).start()
            click_times.clear()

def toggle_listener():
    """Start / Stop aynı buton"""
    global listener_running
    if listener_running:
        stop_listener()
    else:
        start_listener()

def start_listener():
    global BUTTON, TRIGGER_CLICKS, TRIGGER_WINDOW, AUTOCLICK_DURATION, AUTOCLICK_INTERVAL
    global listener_thread, listener_running, listener_instance

    if listener_running:
        return  # Zaten çalışıyorsa tekrar başlatma

    try:
        BUTTON = button_var.get()
        TRIGGER_CLICKS = int(trigger_clicks_var.get())
        TRIGGER_WINDOW = float(trigger_window_var.get())
        AUTOCLICK_DURATION = float(duration_var.get())
        AUTOCLICK_INTERVAL = float(interval_var.get())

        def run_listener():
            global listener_running, listener_instance
            listener_running = True
            listener_instance = mouse.Listener(on_click=on_click)
            listener_instance.start()
            listener_instance.join()
            listener_running = False
            start_stop_btn.config(text="Start / Başlat", bg="green")

        listener_thread = threading.Thread(target=run_listener, daemon=True)
        listener_thread.start()

        status_label.config(text="Listening started! / Dinleme başladı!")
        start_stop_btn.config(text="Stop / Durdur", bg="red")

    except ValueError:
        status_label.config(text="Please enter valid numbers! / Lütfen geçerli sayılar girin!")

def stop_listener():
    global listener_running, listener_instance
    if listener_instance:
        listener_instance.stop()
        listener_instance = None
    listener_running = False
    status_label.config(text="Listening stopped! / Dinleme durdu.")
    start_stop_btn.config(text="Start / Başlat", bg="green")

def settings_changed(event=None):
    """Ayarlarda değişiklik olunca dinlemeyi durdurur"""
    if listener_running:
        stop_listener()

# =======================
# Link açma fonksiyonları
# =======================
def open_youtube():
    webbrowser.open("https://www.youtube.com/@Berkascek")

def open_instagram():
    webbrowser.open("https://berkascek.itch.io/")

# =======================
# GUI
# =======================
root = tk.Tk()
root.title("Auto Clicker / BesClicker - BERKASCEK")
root.geometry("350x370")
root.resizable(False, False)

tk.Label(root, text="Creator / Yapımcı: BERKASCEK", font=("Arial", 10, "bold")).pack(pady=5)
tk.Label(root, text="© All rights reserved / Tüm hakları saklıdır", font=("Arial", 8)).pack()
tk.Button(root, text="YouTube", command=open_youtube, fg="blue").pack()
tk.Button(root, text="berkascek.itch.oi", command=open_instagram, fg="blue").pack()

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Button / Tuş (left/right):").grid(row=0, column=0, sticky="e")
button_var = tk.StringVar(value=BUTTON)
e1 = tk.Entry(frame, textvariable=button_var)
e1.grid(row=0, column=1)

tk.Label(frame, text="Trigger Clicks / Tetikleme Tıklama Sayısı:").grid(row=1, column=0, sticky="e")
trigger_clicks_var = tk.StringVar(value=str(TRIGGER_CLICKS))
e2 = tk.Entry(frame, textvariable=trigger_clicks_var)
e2.grid(row=1, column=1)

tk.Label(frame, text="Trigger Time (s) / Tetikleme Süresi (sn):").grid(row=2, column=0, sticky="e")
trigger_window_var = tk.StringVar(value=str(TRIGGER_WINDOW))
e3 = tk.Entry(frame, textvariable=trigger_window_var)
e3.grid(row=2, column=1)

tk.Label(frame, text="AutoClick Duration (s) / OtoClick Süresi (sn):").grid(row=3, column=0, sticky="e")
duration_var = tk.StringVar(value=str(AUTOCLICK_DURATION))
e4 = tk.Entry(frame, textvariable=duration_var)
e4.grid(row=3, column=1)

tk.Label(frame, text="Click Interval (s) / Tıklama Aralığı (sn):").grid(row=4, column=0, sticky="e")
interval_var = tk.StringVar(value=str(AUTOCLICK_INTERVAL))
e5 = tk.Entry(frame, textvariable=interval_var)
e5.grid(row=4, column=1)

# Ayar değiştiğinde dinlemeyi durdur
for entry in [e1, e2, e3, e4, e5]:
    entry.bind("<KeyRelease>", settings_changed)

# Tek buton Start / Stop
start_stop_btn = tk.Button(root, text="Start / Başlat", command=toggle_listener, bg="green", fg="white")
start_stop_btn.pack(pady=10)

status_label = tk.Label(root, text="", fg="blue")
status_label.pack()

root.mainloop()
