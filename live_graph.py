import matplotlib.pyplot as plt
import math

# Store signal history
signal_history = {}
time_points = []
time_step = 0

# Show only last N scans in graph
MAX_POINTS = 15

# Interactive mode ON
plt.ion()

# Create one fixed figure
fig, ax = plt.subplots(figsize=(8, 5))


def show_graph(df):
    global signal_history
    global time_points
    global time_step
    global fig, ax

    time_step += 1
    time_points.append(time_step)

    # Keep only recent time points
    if len(time_points) > MAX_POINTS:
        time_points = time_points[-MAX_POINTS:]

    current_ssids = set()

    for _, row in df.iterrows():
        ssid = str(row.get("SSID", "Unknown")).strip()
        signal = row.get("Signal")

        if not ssid:
            ssid = "Unknown"

        if signal is None:
            continue

        try:
            signal = float(signal)
        except:
            continue

        if math.isnan(signal):
            continue

        current_ssids.add(ssid)

        if ssid not in signal_history:
            signal_history[ssid] = []

        signal_history[ssid].append(signal)

        # Keep only recent values
        if len(signal_history[ssid]) > MAX_POINTS:
            signal_history[ssid] = signal_history[ssid][-MAX_POINTS:]

    # For networks not seen in this scan, pad with None
    for ssid in list(signal_history.keys()):
        if ssid not in current_ssids:
            signal_history[ssid].append(None)
            if len(signal_history[ssid]) > MAX_POINTS:
                signal_history[ssid] = signal_history[ssid][-MAX_POINTS:]

    ax.clear()

    plotted = False
    valid_values = []

    for ssid, signals in signal_history.items():
        # Make x same length as y
        x = time_points[-len(signals):]

        # Count valid values
        valid_count = sum(1 for s in signals if s is not None)

        if valid_count < 2:
            continue

        y = signals
        valid_values.extend([s for s in y if s is not None])

        ax.plot(
            x,
            y,
            marker="o",
            linewidth=2,
            markersize=4,
            label=ssid
        )
        plotted = True

    ax.set_title("Live WiFi Signal Strength Over Time", fontsize=14, fontweight="bold")
    ax.set_xlabel("Scan Number", fontsize=11)
    ax.set_ylabel("Signal (%)", fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.5)

    if valid_values:
        ymin = max(0, min(valid_values) - 5)
        ymax = min(100, max(valid_values) + 5)

        if ymin == ymax:
            ymin = max(0, ymin - 5)
            ymax = min(100, ymax + 5)

        ax.set_ylim(ymin, ymax)

    if time_points:
        ax.set_xlim(time_points[0], time_points[-1] if time_points[-1] > time_points[0] else time_points[0] + 1)

    if plotted:
        ax.legend(loc="best", fontsize=9)

    fig.tight_layout()
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(0.01)