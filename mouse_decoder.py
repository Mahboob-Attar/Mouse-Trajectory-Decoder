"""Decode the handwritten string hidden in mouse_velocities.csv.

Steps: load -> integrate velocities to positions -> split into strokes at idle
gaps -> plot each stroke -> (visual reading) -> verify with check_answer.py.
Run:  python solve.py
"""
import subprocess, sys
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CSV = "data/mouse_velocities.csv"
MIN_GAP = 30          # >=30 consecutive all-zero samples (~0.45 s) = pause between letters
# Letters read by eye from images/letters_grid.png (stroke index -> character)
READING = ["M","O","N","K","E","Y"," ","M","I","N","D","P","O","N","G"]

# 1. Load. NOTE: velocity_y is used as-is (not zeroed) - vertical strokes are needed.
df = pd.read_csv(CSV)
vx, vy = df.velocity_x.values, df.velocity_y.values

# 2. Integrate velocity -> position (screen y points down, so flip for plotting)
x, y = np.cumsum(vx), -np.cumsum(vy)
fig, ax = plt.subplots(figsize=(10, 8))
ax.plot(x, y, lw=0.5); ax.set_aspect("equal")
ax.set_title("All samples integrated: letters overlap in one spot")
fig.savefig("images/01_full_trajectory.png", dpi=100); plt.close(fig)

# 3. Find idle gaps (runs of exact zero velocity)
idle = (vx == 0) & (vy == 0)
runs, i = [], 0
while i < len(idle):
    if idle[i]:
        j = i
        while j < len(idle) and idle[j]: j += 1
        if j - i >= MIN_GAP: runs.append((i, j))
        i = j
    else: i += 1
print("idle gaps:", runs)

fig, ax = plt.subplots(figsize=(14, 3))
ax.plot(np.hypot(vx, vy), lw=0.4)
for a, b in runs: ax.axvspan(a, b, color="red", alpha=0.4)
ax.set_title("Speed over time; red = idle gaps separating letters")
fig.savefig("images/02_idle_gaps.png", dpi=100); plt.close(fig)

# 4. Split into strokes
bounds = [0] + [b for _, b in runs]
ends = [a for a, _ in runs] + [len(df)]
strokes = [(s, e) for s, e in zip(bounds, ends) if e > s]
print("strokes:", len(strokes))

# 5. Plot each stroke (colored by time: blue=start, red=end; the dark-red tail is the

# cursor returning to the starting point before the next letter)
cols = 5; rows = int(np.ceil(len(strokes) / cols))
fig, axs = plt.subplots(rows, cols, figsize=(20, 4.2 * rows))

for k, (ax, (s, e)) in enumerate(zip(axs.flat, strokes)):
    px = np.cumsum(vx[s:e]); py = -np.cumsum(vy[s:e])
    ax.scatter(px, py, c=np.arange(len(px)), s=3, cmap="jet")
    ax.set_aspect("equal"); ax.set_title(f"stroke {k} -> '{READING[k]}'")
    
    fig.savefig  # (individual image below)
    f2, a2 = plt.subplots(figsize=(5, 5))
    a2.scatter(px, py, c=np.arange(len(px)), s=3, cmap="jet"); a2.set_aspect("equal")
    a2.set_title(f"stroke {k} -> '{READING[k]}'")
    f2.savefig(f"images/stroke_{k:02d}.png", dpi=80); plt.close(f2)
    
for ax in list(axs.flat)[len(strokes):]: ax.axis("off")
fig.savefig("images/letters_grid.png", dpi=70); plt.close(fig)

# 6. Verify
answer = "".join(READING)
print("answer:", answer)
r = subprocess.run([sys.executable, "data/check_answer.py", answer], capture_output=True, text=True)
print(r.stdout.strip()[-6:], "(exit code", r.returncode, ")")
