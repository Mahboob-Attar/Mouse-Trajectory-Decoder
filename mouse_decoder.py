import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def load_velocity_data(file_path: str):
    return pd.read_csv(file_path)


def detect_word_segments(df, threshold=0.5, pause_frames=20):
    dx = df["velocity_x"].values
    dy = df["velocity_y"].values

    speed = np.abs(dx) + np.abs(dy)

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


def reconstruct(df):
    dx = df["velocity_x"].values
    dy = df["velocity_y"].values

    x = np.cumsum(dx)
    y = np.cumsum(dy)

    x -= np.mean(x)
    y -= np.mean(y)
    y = -y

    return x, y


def animate_segment(x, y, title):

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect("equal")
    ax.axis("off")

    ax.set_xlim(np.nanmin(x), np.nanmax(x))
    ax.set_ylim(np.nanmin(y), np.nanmax(y))

    line, = ax.plot([], [], lw=1, color="black")

    step = max(1, len(x)//1500)

    def update(frame):
        i = frame * step
        line.set_data(x[:i], y[:i])
        return line,

    frames = len(x)//step

    ani = FuncAnimation(
        fig,
        update,
        frames=frames,
        interval=15,
        blit=False
    )

    plt.title(title)
    plt.show()


def main():
    if len(sys.argv) != 2:
        print("Usage: python mouse_decoder.py <mouse_velocities.csv>")
        sys.exit(1)

    df = load_velocity_data(sys.argv[1])

    print("Detecting word segments...")
    segments = detect_word_segments(df)

    print(f"Detected {len(segments)} word segments")

    for i, (start, end) in enumerate(segments):
        print(f"Word {i+1}: rows {start} to {end}")

        df_chunk = df.iloc[start:end]
        x, y = reconstruct(df_chunk)

        animate_segment(x, y, f"Word {i+1}")


if __name__ == "__main__":
    main() 