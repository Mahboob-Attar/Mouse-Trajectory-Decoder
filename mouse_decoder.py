import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def load_velocity_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)

    required_columns = {"timestamp", "velocity_x", "velocity_y"}
    if not required_columns.issubset(df.columns):
        raise ValueError("CSV missing required columns.")

    return df


def reconstruct_trajectory(df: pd.DataFrame):
    dx = df["velocity_x"].values
    dy = df["velocity_y"].values

    x_points = []
    y_points = []

    current_x = 0
    current_y = 0

    pause_counter = 0
    pause_limit = 10

    for i in range(len(dx)):
        movement = abs(dx[i]) + abs(dy[i])

        if movement < 0.3:
            pause_counter += 1
        else:
            pause_counter = 0

        if pause_counter >= pause_limit:
            x_points.append(np.nan)
            y_points.append(np.nan)
            continue

        current_x += dx[i]
        current_y += dy[i]

        x_points.append(current_x)
        y_points.append(current_y)

    x = np.array(x_points)
    y = np.array(y_points)

    x -= np.nanmean(x)
    y -= np.nanmean(y)
    y = -y

    return x, y


def plot_trajectory(x: np.ndarray, y: np.ndarray, title: str):
    os.makedirs("plots", exist_ok=True)

    plt.figure(figsize=(6, 6))
    plt.plot(x, y, linewidth=1)
    plt.gca().set_aspect("equal", adjustable="box")
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()

    filename = title.replace("%", "pct").replace(" ", "_") + ".png"
    plt.savefig(os.path.join("plots", filename), dpi=400)
    plt.close()


def main():
    if len(sys.argv) != 2:
        print("Usage: python mouse_decoder.py <mouse_velocities.csv>")
        sys.exit(1)

    file_path = sys.argv[1]

    df = load_velocity_data(file_path)
    n = len(df)

    print("Total rows:", n)

    step = int(n * 0.15)

    for i in range(0, n, step):
        start_pct = int((i / n) * 100)
        end_pct = int(((min(i + step, n)) / n) * 100)

        df_chunk = df.iloc[i : i + step]
        x, y = reconstruct_trajectory(df_chunk)

        title = f"{start_pct}% to {end_pct}%"
        plot_trajectory(x, y, title)

    # Also save full dataset
    x, y = reconstruct_trajectory(df)
    plot_trajectory(x, y, "Full Dataset")

    print("All 15% segment plots saved in 'plots/' folder.")


if __name__ == "__main__":
    main()