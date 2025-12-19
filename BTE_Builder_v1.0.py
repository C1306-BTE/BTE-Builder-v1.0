import tkinter as tk
from tkinter import simpledialog
import threading
import time
import keyboard
import pyautogui
import pygetwindow as gw

running = False
last_number = None  # store last number for "=" key repeat
last_block = None   # store last block for "]" key repeat

def start_program():
    global running
    if running:
        return
    running = True
    status_label.config(text="Program running... Press `, -, =, [, ], or \\ to execute commands")
    threading.Thread(target=key_listener, daemon=True).start()

def stop_program():
    global running
    running = False
    keyboard.unhook_all()
    status_label.config(text="Program stopped.")

# --- Main key listener ---
def key_listener():
    global running
    last_press_time = 0
    cooldown = 0.5  # seconds between triggers

    while running:
        current_time = time.time()

        if keyboard.is_pressed('`') and (current_time - last_press_time > cooldown):
            window.after(0, backtick_action)
            last_press_time = current_time

        elif keyboard.is_pressed('-') and (current_time - last_press_time > cooldown):
            window.after(0, minus_action)
            last_press_time = current_time

        elif keyboard.is_pressed(']') and (current_time - last_press_time > cooldown):
            window.after(0, right_bracket_action)
            last_press_time = current_time

        elif (keyboard.is_pressed('\\') or keyboard.is_pressed('backslash')) and (current_time - last_press_time > cooldown):
            window.after(0, backslash)
            last_press_time = current_time

        time.sleep(0.05)

# --- Actions for keys ---
def backtick_action():
    mc_window = find_minecraft_window()
    if mc_window:
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'shift', 'c')
        time.sleep(0.2)
        mc_window.activate()
        time.sleep(0.2)
        pyautogui.press('esc')
        time.sleep(0.2)
        pyautogui.press('t')
        time.sleep(0.2)
        pyautogui.typewrite('/tpll ')
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.2)
        pyautogui.press('enter')
        time.sleep(0.2)
        pyautogui.press('space')
        time.sleep(0.4)
        pyautogui.click(button='right')
        status_label.config(text="` action executed!")
    else:
        status_label.config(text="Minecraft window not found.")

# --- Press keys ---
def minus_action():
    mc_window = find_minecraft_window()
    if mc_window:
        mc_window.activate()
        pyautogui.press('esc')
        time.sleep(0.5)
        pyautogui.press('t')
        time.sleep(0.5)
        pyautogui.typewrite('//line 35:1')
        pyautogui.press('enter')
        status_label.config(text="- action executed!")
    else:
        status_label.config(text="Minecraft window not found.")

# --- "]" key functions ---
def right_bracket_action():
    global last_block
    if last_block is None:
        walls = simpledialog.askstring("Input", "Enter a Block ID for the walls:")
        if not walls:
            status_label.config(text="No block entered.")
            return
        last_block = walls
    else:
        walls = last_block

    times = simpledialog.askinteger("Input", "Enter how many times to repeat:")
    if not times or times <= 0:
        status_label.config(text="Invalid repeat number.")
        return

    mc_window = find_minecraft_window()
    if mc_window:
        mc_window.activate()
        for i in range(times):
            time.sleep(0.4)
            pyautogui.press('esc')
            time.sleep(0.1)
            pyautogui.press('t')
            time.sleep(0.2)
            pyautogui.typewrite(f'//replace 35:1 {walls}')
            pyautogui.press('enter')
            time.sleep(0.1)
            pyautogui.press('t')
            time.sleep(0.1)
            pyautogui.typewrite('//shift 1 up')
            pyautogui.press('enter')

        status_label.config(text=f"] action executed! Replaced walls {times} times.")
    else:
        status_label.config(text="Minecraft window not found.")

# --- "\" key function (UPDATED ONLY) ---
def backslash():
    mc_window = find_minecraft_window()
    if not mc_window:
        status_label.config(text="Minecraft window not found.")
        return

    block = simpledialog.askstring("Input", "Enter block ID for //fill:")
    if not block:
        status_label.config(text="No block entered.")
        return

    amount = simpledialog.askinteger("Input", "Enter amount for //stack:")
    if not amount or amount <= 0:
        status_label.config(text="Invalid stack amount.")
        return

    mc_window.activate()
    time.sleep(0.5)
    pyautogui.press('esc')
    pyautogui.press('t')
    time.sleep(0.2)
    pyautogui.typewrite(f'//fill {block} 50')
    pyautogui.press('enter')

    pyautogui.press('t')
    time.sleep(0.2)
    pyautogui.typewrite(f'//stack {amount} up')
    pyautogui.press('enter')

    pyautogui.press('t')
    time.sleep(0.2)
    pyautogui.typewrite('/ascend 50')
    pyautogui.press('enter')

    status_label.config(text="\\ Fill → Stack → Ascend executed!")

# --- Helper function ---
def find_minecraft_window():
    for w in gw.getAllTitles():
        if "Minecraft" in w:
            return gw.getWindowsWithTitle(w)[0]
    return None

# --- GUI setup ---
window = tk.Tk()
window.title("Minecraft Control")
window.geometry("370x200")

start_button = tk.Button(window, text="Start Program", command=start_program)
start_button.pack(pady=10)

stop_button = tk.Button(window, text="Stop Program", command=stop_program)
stop_button.pack(pady=10)

status_label = tk.Label(window, text="Program not running.")
status_label.pack(pady=10)

def on_closing():
    stop_program()
    window.destroy()

window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()
