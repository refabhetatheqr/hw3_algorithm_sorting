import imageio
import numpy as np

import tkinter as tk
from tkinter import ttk
import threading
import random
import time
from tkinter import filedialog
from PIL import Image, ImageDraw

# =========================
# Config
# =========================

DEFAULT_N = 10000
stop_flag = False

# GIF recording
recording = False
frames = []

# =========================
# Shared state (thread-safe)
# =========================

progress = {
    "selection": 0.0,
    "bubble": 0.0,
    "quick": 0.0
}

runtime = {
    "selection": None,
    "bubble": None,
    "quick": None
}


# =========================
# utility
# =========================

def swap(arr, i, j):
    arr[i], arr[j] = arr[j], arr[i]


def format_time(t):
    return "-" if t is None else f"{t:.4f}s"

# =========================
# GIF capture
# =========================

def capture_frame():

    width = 600
    height = 350

    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    # title
    draw.text((20, 20), "Sorting Algorithms Efficiency", fill="black")

    # Selection
    draw.text((20, 80), "Selection", fill="black")
    draw.rectangle(
        [150, 80, 150 + int(progress["selection"] * 3), 100],
        fill="blue"
    )
    draw.text((470, 80), f"{progress['selection']:.1f}%", fill="black")

    # Bubble
    draw.text((20, 140), "Bubble", fill="black")
    draw.rectangle(
        [150, 140, 150 + int(progress["bubble"] * 3), 160],
        fill="green"
    )
    draw.text((470, 140), f"{progress['bubble']:.1f}%", fill="black")

    # Quick
    draw.text((20, 200), "Quick", fill="black")
    draw.rectangle(
        [150, 200, 150 + int(progress["quick"] * 3), 220],
        fill="red"
    )
    draw.text((470, 200), f"{progress['quick']:.1f}%", fill="black")

    # runtime
    draw.text(
        (20, 280),
        f"Selection: {format_time(runtime['selection'])}",
        fill="black"
    )

    draw.text(
        (20, 300),
        f"Bubble: {format_time(runtime['bubble'])}",
        fill="black"
    )

    draw.text(
        (20, 320),
        f"Quick: {format_time(runtime['quick'])}",
        fill="black"
    )
    
    scale = 3

    img = img.resize(
        (width * scale, height * scale),
        Image.Resampling.LANCZOS
    )

    frames.append(np.array(img))

def start_record():
    global recording, frames
    frames = []
    recording = True
    print("Recording started")

def save_gif():
    global frames

    if len(frames) == 0:
        status_label.config(text="No GIF to save")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".gif",
        filetypes=[("GIF files", "*.gif")],
        title="Save GIF As"
    )

    if file_path:
        imageio.mimsave(file_path, frames, fps=10, loop=0)
        status_label.config(text="Saved ✔")

def stop_record():
    global recording
    recording = False

def start_all():
    start_record()
    start_sorting()

# =========================
# Selection Sort
# =========================

def selection_sort(arr):
    global stop_flag

    start = time.time()
    n = len(arr)

    for i in range(n - 1):
        if stop_flag:
            return

        min_idx = i

        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j

        swap(arr, i, min_idx)

        progress["selection"] = (i + 1) / (n - 1) * 100

    runtime["selection"] = time.time() - start
    progress["selection"] = 100


# =========================
# Bubble Sort
# =========================

def bubble_sort(arr):
    global stop_flag

    start = time.time()
    n = len(arr)

    for i in range(n - 1):
        if stop_flag:
            return

        swapped = False

        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                swap(arr, j, j + 1)
                swapped = True

        progress["bubble"] = (i + 1) / (n - 1) * 100

        if not swapped:
            break

    runtime["bubble"] = time.time() - start
    progress["bubble"] = 100


# =========================
# Quick Sort
# =========================

def partition(arr, low, high):

    pivot = arr[low]
    left = low + 1
    right = high

    while True:

        while left <= right and arr[right] >= pivot:
            right -= 1

        while left <= right and arr[left] <= pivot:
            left += 1

        if left > right:
            break

        swap(arr, left, right)

    swap(arr, low, right)
    return right


def quick_sort(arr, low, high, counter):

    if low >= high or stop_flag:
        return

    p = partition(arr, low, high)

    counter[0] += 1
    progress["quick"] = min(counter[0] / len(arr) * 10, 100)

    quick_sort(arr, low, p - 1, counter)
    quick_sort(arr, p + 1, high, counter)


def quick_worker(arr):

    counter = [0]
    start = time.time()

    quick_sort(arr, 0, len(arr) - 1, counter)

    runtime["quick"] = time.time() - start
    progress["quick"] = 100


# =========================
# thread control
# =========================

def start_sorting():

    global stop_flag
    stop_flag = False

    n = int(entry_n.get())

    base = random.sample(range(1, n * 10), n)

    threading.Thread(target=selection_sort, args=(base.copy(),)).start()
    threading.Thread(target=bubble_sort, args=(base.copy(),)).start()
    threading.Thread(target=quick_worker, args=(base.copy(),)).start()


def stop_sorting():
    global stop_flag
    stop_flag = True


# =========================
# GUI update loop (THREAD SAFE)
# =========================

def update_gui():

    # progress
    sel_bar["value"] = progress["selection"]
    bub_bar["value"] = progress["bubble"]
    qui_bar["value"] = progress["quick"]

    sel_percent.config(text=f"{progress['selection']:.1f}%")
    bub_percent.config(text=f"{progress['bubble']:.1f}%")
    qui_percent.config(text=f"{progress['quick']:.1f}%")

    # runtime
    sel_time.config(text=f"Selection: {format_time(runtime['selection'])}")
    bub_time.config(text=f"Bubble: {format_time(runtime['bubble'])}")
    qui_time.config(text=f"Quick: {format_time(runtime['quick'])}")

    if recording:
        capture_frame()

    root.after(50, update_gui)


# =========================
# N control (▲▼ +1000)
# =========================

def change_n(delta):
    val = int(entry_n.get())
    val = max(1000, val + delta)
    entry_n.delete(0, tk.END)
    entry_n.insert(0, str(val))

# =========================
# Reset
# =========================

def reset_all():
    global stop_flag

    stop_flag = True

    # reset progress
    progress["selection"] = 0
    progress["bubble"] = 0
    progress["quick"] = 0

    # reset runtime
    runtime["selection"] = None
    runtime["bubble"] = None
    runtime["quick"] = None

    # reset UI bars
    sel_bar["value"] = 0
    bub_bar["value"] = 0
    qui_bar["value"] = 0

    sel_percent.config(text="0%")
    bub_percent.config(text="0%")
    qui_percent.config(text="0%")

    sel_time.config(text="Selection: -")
    bub_time.config(text="Bubble: -")
    qui_time.config(text="Quick: -")

# =========================
# UI
# =========================

root = tk.Tk()
root.title("Sorting Algorithms Efficiency")
root.geometry("600x500")


# =========================
# Title
# =========================

tk.Label(root, text="Sorting Algorithms Efficiency", font=("Arial", 16)).pack()


# =========================
# N input
# =========================

frame_n = tk.Frame(root)
frame_n.pack(pady=5)

tk.Label(frame_n, text="Data Size (N):").pack(side=tk.LEFT)

entry_n = tk.Entry(frame_n, width=10)
entry_n.insert(0, str(DEFAULT_N))
entry_n.pack(side=tk.LEFT)

tk.Button(frame_n, text="▲", command=lambda: change_n(1000)).pack(side=tk.LEFT)
tk.Button(frame_n, text="▼", command=lambda: change_n(-1000)).pack(side=tk.LEFT)


# =========================
# Algorithm Table
# =========================

table = tk.Frame(root)
table.pack(pady=10)

# header
tk.Label(table, text="Algorithm", width=12).grid(row=0, column=0, padx=10, pady=5)
tk.Label(table, text="Progress", width=30).grid(row=0, column=1, padx=10, pady=5)
tk.Label(table, text="%", width=8).grid(row=0, column=2, padx=10, pady=5)

# Selection
tk.Label(table, text="Selection", width=12).grid(row=1, column=0, padx=10, pady=6)

sel_bar = ttk.Progressbar(table, length=250)
sel_bar.grid(row=1, column=1, padx=10, pady=6)

sel_percent = tk.Label(table, text="0%")
sel_percent.grid(row=1, column=2, padx=10, pady=6)

# Bubble
tk.Label(table, text="Bubble", width=12).grid(row=2, column=0, padx=10, pady=6)

bub_bar = ttk.Progressbar(table, length=250)
bub_bar.grid(row=2, column=1, padx=10, pady=6)

bub_percent = tk.Label(table, text="0%")
bub_percent.grid(row=2, column=2, padx=10, pady=6)

# Quick
tk.Label(table, text="Quick", width=12).grid(row=3, column=0, padx=10, pady=6)

qui_bar = ttk.Progressbar(table, length=250)
qui_bar.grid(row=3, column=1, padx=10, pady=6)

qui_percent = tk.Label(table, text="0%")
qui_percent.grid(row=3, column=2, padx=10, pady=6)


# =========================
# Total runtime
# =========================

tk.Label(root, text="========================================").pack()

tk.Label(root, text="Total runtime(s)", font=("Arial", 12, "bold")).pack()

runtime_frame = tk.Frame(root)
runtime_frame.pack(pady=5)

sel_time = tk.Label(runtime_frame, text="Selection: -")
sel_time.grid(row=0, column=0, sticky="w", pady=2)

bub_time = tk.Label(runtime_frame, text="Bubble: -")
bub_time.grid(row=1, column=0, sticky="w", pady=2)

qui_time = tk.Label(runtime_frame, text="Quick: -")
qui_time.grid(row=2, column=0, sticky="w", pady=2)

status_label = tk.Label(root, text="Status: Idle")
status_label.pack()

# =========================
# buttons
# =========================

btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

tk.Button(btn_frame, text="Start Sorting", command=start_sorting).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Stop", command=stop_sorting).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Reset", command=reset_all).pack(side=tk.LEFT, padx=10)

btn_frame2 = tk.Frame(root)
btn_frame2.pack(pady=5)

tk.Button(btn_frame2, text="Start GIF + Sort", command=start_all).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame2, text="Stop GIF", command=stop_record).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame2, text="Save GIF", command=save_gif).pack(side=tk.LEFT, padx=10)

# start loop
update_gui()
root.mainloop()