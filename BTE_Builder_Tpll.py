import tkinter as tk
from pynput import keyboard
import pyautogui
import pyperclip
import pygetwindow as gw
import time
import threading


# ==========================================
# VARIABLES
# ==========================================

points = []

record_key = None
run_key = None

waiting_for = None

running = False
is_executing = False


# ==========================================
# FOCUS MINECRAFT
# ==========================================

def focus_minecraft():
    windows = gw.getWindowsWithTitle("Minecraft")

    if not windows:
        print("Minecraft window not found!")
        return False

    minecraft = windows[0]

    try:
        if minecraft.isMinimized:
            minecraft.restore()

        minecraft.activate()

        # Give Windows/Minecraft time to become active
        time.sleep(0.5)

        return True

    except Exception as error:
        print(f"Could not focus Minecraft: {error}")
        return False


# ==========================================
# UPDATE GUI
# ==========================================

def update_points_display():
    points_label.config(
        text=f"Points saved: {len(points)}"
    )


# ==========================================
# COPY COORDINATES
# ==========================================

def copy_coordinates():

    # Don't record while the automation is running
    if is_executing:
        return

    # Press Ctrl + Shift + C
    pyautogui.hotkey(
        "ctrl",
        "shift",
        "c"
    )

    # Wait for Minecraft to copy coordinates
    time.sleep(0.15)

    # Get clipboard contents
    coords = pyperclip.paste().strip()

    # Check that something was copied
    if coords:

        # Don't allow recording if execution started
        # while this function was waiting
        if is_executing:
            return

        points.append(coords)

        print(
            f"Saved point {len(points)}: {coords}"
        )

        # Update GUI safely
        root.after(
            0,
            update_points_display
        )

        root.after(
            0,
            lambda: status_label.config(
                text=f"Saved point {len(points)}"
            )
        )

    else:

        print("Nothing was copied!")

        root.after(
            0,
            lambda: status_label.config(
                text="ERROR: Nothing copied!"
            )
        )


# ==========================================
# RUN ALL POINTS
# ==========================================

def run_points():

    global is_executing

    # Don't run if no points exist
    if not points:

        root.after(
            0,
            lambda: status_label.config(
                text="No points saved!"
            )
        )

        return

    # Prevent multiple runs at once
    if is_executing:
        return


    # --------------------------------------
    # LOCK RECORDING
    # --------------------------------------

    is_executing = True


    # --------------------------------------
    # CREATE FIXED COPY OF POINTS
    # --------------------------------------

    # This prevents the list from changing
    # while we are looping through it.
    points_to_run = points.copy()


    print(
        f"Running {len(points_to_run)} points..."
    )


    # --------------------------------------
    # FOCUS MINECRAFT
    # --------------------------------------

    if not focus_minecraft():

        is_executing = False

        root.after(
            0,
            lambda: status_label.config(
                text="Minecraft window not found!"
            )
        )

        return


    # --------------------------------------
    # LOOP THROUGH SAVED POINTS
    # --------------------------------------

    for number, coords in enumerate(
        points_to_run,
        start=1
    ):

        # Stop immediately if STOP was pressed
        if not running:

            print("Stopped!")

            break


        # Update status
        root.after(
            0,
            lambda n=number: status_label.config(
                text=(
                    f"Running point "
                    f"{n}/{len(points_to_run)}"
                )
            )
        )


        print(
            f"Running point {number}: {coords}"
        )


        # ----------------------------------
        # OPEN MINECRAFT CHAT
        # ----------------------------------

        pyautogui.press("t")

        time.sleep(0.15)


        # ----------------------------------
        # CREATE TELEPORT COMMAND
        # ----------------------------------

        command = f"/tpll {coords}"

        print(command)


        # ----------------------------------
        # TYPE COMMAND
        # ----------------------------------

        pyautogui.write(
            command,
            interval=0.01
        )


        # ----------------------------------
        # SEND COMMAND
        # ----------------------------------

        pyautogui.press("enter")


        # ----------------------------------
        # WAIT FOR TELEPORT
        # ----------------------------------

        time.sleep(0.7)


        # ----------------------------------
        # RIGHT CLICK / PLACE BLOCK
        # ----------------------------------

        pyautogui.click(
            button="right"
        )


        # ----------------------------------
        # WAIT BEFORE NEXT POINT
        # ----------------------------------

        time.sleep(0.3)


    # ======================================
    # FINISHED
    # ======================================

    is_executing = False


    if running:

        root.after(
            0,
            lambda: status_label.config(
                text="Finished!"
            )
        )


    print("Finished running points!")


# ==========================================
# START RUN IN SEPARATE THREAD
# ==========================================

def start_run_thread():

    global is_executing

    # Must be started first
    if not running:

        status_label.config(
            text="Click START first!"
        )

        return


    # Prevent multiple threads
    if is_executing:
        return


    threading.Thread(
        target=run_points,
        daemon=True
    ).start()


# ==========================================
# CHOOSE RECORD KEY
# ==========================================

def choose_record_key():

    global waiting_for

    waiting_for = "record"

    status_label.config(
        text="Press the key for RECORD..."
    )


# ==========================================
# CHOOSE RUN KEY
# ==========================================

def choose_run_key():

    global waiting_for

    waiting_for = "run"

    status_label.config(
        text="Press the key for RUN..."
    )


# ==========================================
# START PROGRAM
# ==========================================

def start_program():

    global running


    # Make sure Record Key exists
    if record_key is None:

        status_label.config(
            text="Please set a Record Key!"
        )

        return


    # Make sure Run Key exists
    if run_key is None:

        status_label.config(
            text="Please set a Run Key!"
        )

        return


    # Prevent same key being used
    if record_key == run_key:

        status_label.config(
            text="Record and Run keys must differ!"
        )

        return


    running = True


    status_label.config(
        text="Program is RUNNING"
    )


    print("Program started!")


# ==========================================
# STOP PROGRAM
# ==========================================

def stop_program():

    global running

    running = False


    status_label.config(
        text="STOPPED"
    )


    print("Program stopped!")


# ==========================================
# CLEAR POINTS
# ==========================================

def clear_points():

    # Don't allow clearing during execution
    if is_executing:

        status_label.config(
            text="Cannot clear while running!"
        )

        return


    points.clear()


    update_points_display()


    status_label.config(
        text="Points cleared!"
    )


    print("Points cleared!")


# ==========================================
# KEYBOARD LISTENER
# ==========================================

def on_press(key):

    global record_key
    global run_key
    global waiting_for


    # --------------------------------------
    # CHOOSING RECORD KEY
    # --------------------------------------

    if waiting_for == "record":

        record_key = key

        waiting_for = None


        root.after(
            0,
            lambda: record_key_label.config(
                text=f"Record key: {key}"
            )
        )


        root.after(
            0,
            lambda: status_label.config(
                text="Record key selected!"
            )
        )


        print(
            f"Record key set to: {key}"
        )

        return


    # --------------------------------------
    # CHOOSING RUN KEY
    # --------------------------------------

    if waiting_for == "run":

        run_key = key

        waiting_for = None


        root.after(
            0,
            lambda: run_key_label.config(
                text=f"Run key: {key}"
            )
        )


        root.after(
            0,
            lambda: status_label.config(
                text="Run key selected!"
            )
        )


        print(
            f"Run key set to: {key}"
        )

        return


    # --------------------------------------
    # DO NOTHING IF STOPPED
    # --------------------------------------

    if not running:
        return


    # --------------------------------------
    # RECORD POINT
    # --------------------------------------

    if (
        key == record_key
        and not is_executing
    ):

        threading.Thread(
            target=copy_coordinates,
            daemon=True
        ).start()


    # --------------------------------------
    # RUN POINTS
    # --------------------------------------

    elif (
        key == run_key
        and not is_executing
    ):

        start_run_thread()


# ==========================================
# CREATE WINDOW
# ==========================================

root = tk.Tk()

root.title(
    "BTE Builder (tplls)"
)

root.geometry(
    "300x550"
)

root.resizable(
    False,
    False
)


# ==========================================
# TITLE
# ==========================================

title = tk.Label(
    root,
    text="BTE Builder (tplls)",
    font=(
        "Arial",
        18,
        "bold"
    )
)

title.pack(
    pady=15
)


# ==========================================
# RECORD KEY BUTTON
# ==========================================

record_button = tk.Button(
    root,
    text="Set Record Key",
    width=20,
    command=choose_record_key
)

record_button.pack(
    pady=5
)


record_key_label = tk.Label(
    root,
    text="Record key: Not set"
)

record_key_label.pack()


# ==========================================
# RUN KEY BUTTON
# ==========================================

run_button = tk.Button(
    root,
    text="Set Run Key",
    width=20,
    command=choose_run_key
)

run_button.pack(
    pady=10
)


run_key_label = tk.Label(
    root,
    text="Run key: Not set"
)

run_key_label.pack()

 # tpll helper down

run_button = tk.Button(
    root,
    text="Start Tpll Automator",
    width=20,
    command=choose_run_key
)

run_button.pack(
    pady=10
)


run_key_label = tk.Label(
    root,
    text="Pick key for Tpll automator."
)

run_key_label.pack()


# ==========================================
# POINT COUNTER
# ==========================================

points_label = tk.Label(
    root,
    text="Points saved: 0",
    font=(
        "Arial",
        12
    )
)

points_label.pack(
    pady=15
)


# ==========================================
# START BUTTON
# ==========================================

start_button = tk.Button(
    root,
    text="START",
    width=20,
    height=2,
    command=start_program
)

start_button.pack(
    pady=5
)


# ==========================================
# STOP BUTTON
# ==========================================

stop_button = tk.Button(
    root,
    text="STOP",
    width=20,
    height=2,
    command=stop_program
)

stop_button.pack(
    pady=5
)


# ==========================================
# CLEAR POINTS BUTTON
# ==========================================

clear_button = tk.Button(
    root,
    text="Clear Points",
    width=20,
    command=clear_points
)

clear_button.pack(
    pady=5
)


# ==========================================
# STATUS LABEL
# ==========================================

status_label = tk.Label(
    root,
    text="Choose your keys, then press START",
    font=(
        "Arial",
        11
    )
)

status_label.pack(
    pady=15
)


# ==========================================
# START KEYBOARD LISTENER
# ==========================================

listener = keyboard.Listener(
    on_press=on_press
)

listener.start()


# ==========================================
# START GUI
# ==========================================

root.mainloop()