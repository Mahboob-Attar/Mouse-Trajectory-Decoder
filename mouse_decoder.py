import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# -----------------------------
# Load CSV
# -----------------------------
def load_velocity_data(file_path: str):
    return pd.read_csv(file_path)


# -----------------------------
# Detect pauses between words
# -----------------------------
def detect_word_segments(df, threshold=0.5, pause_frames=20):

    dx = df["velocity_x"].values
    dy = df["velocity_y"].values

    speed = np.sqrt(dx**2 + dy**2)

    segments = []
    start = None
    pause_count = 0

    for i in range(len(speed)):

        if speed[i] > threshold:
            if start is None:
                start = i
            pause_count = 0

        else:
            pause_count += 1

            if pause_count >= pause_frames and start is not None:
                end = i - pause_frames
                segments.append((start, end))
                start = None

    if start is not None:
        segments.append((start, len(speed)-1))

    return segments


# -----------------------------
# Convert velocity → position
# -----------------------------
def reconstruct(df, scale=15):

    dx = df["velocity_x"].values
    dy = df["velocity_y"].values

    x = np.cumsum(dx) * scale
    y = np.cumsum(dy) * scale

    y = -y   # flip vertically

    return x, y


# -----------------------------
# Smooth trajectory
# -----------------------------
def smooth(x, y):

    from scipy.signal import savgol_filter

    x = savgol_filter(x, 21, 3)
    y = savgol_filter(y, 21, 3)

    return x, y


# -----------------------------
# Static plot (BEST for reading)
# -----------------------------
def plot_static(x, y, title):

    plt.figure(figsize=(12,4))
    plt.plot(x, y)
    plt.axis("equal")
    plt.axis("off")

    for i in range(0, len(x), 200):
        plt.text(x[i], y[i], str(i), fontsize=8)

    plt.show()

# -----------------------------
# Animation (optional)
# -----------------------------
def animate_segment(x, y, title):

    fig, ax = plt.subplots(figsize=(6,6))

    ax.set_aspect("equal")
    ax.axis("off")

    ax.set_xlim(np.min(x), np.max(x))
    ax.set_ylim(np.min(y), np.max(y))

    line, = ax.plot([], [], lw=2, color="black")

    step = max(1, len(x)//1000)

    def update(frame):

        i = frame * step
        line.set_data(x[:i], y[:i])

        return line,

    frames = len(x)//step

    ani = FuncAnimation(
        fig,
        update,
        frames=frames,
        interval=10
    )

    plt.title(title)
    plt.show()


# -----------------------------
# MAIN
# -----------------------------
def main():

    if len(sys.argv) != 2:
        print("Usage: python mouse_decoder.py mouse_velocities.csv")
        sys.exit(1)

    file_path = sys.argv[1]

    df = load_velocity_data(file_path)

    print("Detecting word segments...")
    segments = detect_word_segments(df)

    print(f"Detected {len(segments)} segments")

    for i, (start, end) in enumerate(segments):

        print(f"Segment {i+1}: rows {start} → {end}")

        df_chunk = df.iloc[start:end]

        x, y = reconstruct(df_chunk)

        # optional smoothing
        x, y = smooth(x, y)

        # show plot
        plot_static(x, y, f"Segment {i+1}")

        # optional animation
        animate_segment(x, y, f"Segment {i+1}")


if __name__ == "__main__":
    main()