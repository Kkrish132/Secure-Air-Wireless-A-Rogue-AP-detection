import winsound
import os
import tkinter as tk
from tkinter import ttk
import threading
import time

from scanner.wifi_scanner import scan_wifi
from detection.rogue_detector import detect_rogue
from ai.risk_model import calculate_risk, estimate_distance, get_safety_status
from dashboard.live_graph import show_graph


# Shared scan data
latest_df = None
scan_lock = threading.Lock()
last_alert_state = False


def wifi_scan_worker():
    """
    Background worker that scans WiFi continuously.
    This prevents the Tkinter dashboard from freezing.
    """
    global latest_df

    while True:
        try:
            df = scan_wifi()
            with scan_lock:
                latest_df = df
        except Exception as e:
            print("Scan error:", e)

        # Wait before next scan
        time.sleep(3)


def show_dashboard():

    global last_alert_state

    root = tk.Tk()
    root.title("SecureAir Wireless Monitor")
    root.geometry("1200x600")

    title = tk.Label(
        root,
        text="SecureAir Rogue Access Point Detection",
        font=("Arial", 18, "bold")
    )
    title.pack(pady=10)

    tree = ttk.Treeview(root)

    tree.tag_configure("safe", background="lightgreen")
    tree.tag_configure("suspicious", background="khaki")
    tree.tag_configure("rogue", background="lightcoral")
    tree.tag_configure("best", background="lightblue")

    tree["columns"] = (
        "BSSID",
        "Channel",
        "Signal",
        "Encryption",
        "Risk",
        "Distance",
        "Safety"
    )

    tree.column("#0", width=170)
    tree.column("BSSID", width=170)
    tree.column("Channel", width=70)
    tree.column("Signal", width=80)
    tree.column("Encryption", width=120)
    tree.column("Risk", width=80)
    tree.column("Distance", width=140)
    tree.column("Safety", width=120)

    tree.heading("#0", text="SSID")
    tree.heading("BSSID", text="BSSID")
    tree.heading("Channel", text="Channel")
    tree.heading("Signal", text="Signal %")
    tree.heading("Encryption", text="Encryption")
    tree.heading("Risk", text="Risk Score")
    tree.heading("Distance", text="Estimated Distance")
    tree.heading("Safety", text="Safety Status")

    tree.pack(fill="both", expand=True)

    best_network_label = tk.Label(
        root,
        text="Recommended Safe Network: Scanning...",
        font=("Arial", 12, "bold"),
        fg="blue"
    )
    best_network_label.pack(pady=6)

    status_label = tk.Label(
        root,
        text="Scanner Status: Starting...",
        font=("Arial", 10),
        fg="darkgreen"
    )
    status_label.pack(pady=2)

    alert_label = tk.Label(
        root,
        text="No Rogue Access Point Detected",
        font=("Arial", 11, "bold"),
        fg="green"
    )
    alert_label.pack(pady=4)

    sound_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "sounds",
        "alert.wav"
    )

    # Start background scanning thread
    scanner_thread = threading.Thread(target=wifi_scan_worker, daemon=True)
    scanner_thread.start()

    def refresh():

        global last_alert_state

        tree.delete(*tree.get_children())

        with scan_lock:
            df = latest_df

        if df is not None and not df.empty:

            status_label.config(text="Scanner Status: Live scan data loaded")

            rogue = detect_rogue(df)
            alert = False
            safe_candidates = []

            for index, row in df.iterrows():

                risk = calculate_risk(row)
                distance = estimate_distance(row.get("Signal"))
                safety = get_safety_status(row, rogue)

                tag = "safe"

                if safety == "ROGUE":
                    tag = "rogue"
                    alert = True
                elif safety == "SUSPICIOUS":
                    tag = "suspicious"
                else:
                    try:
                        signal_value = float(row.get("Signal", 0))
                    except:
                        signal_value = 0

                    safe_candidates.append(
                        (risk, -signal_value, row["SSID"], index)
                    )

                tree.insert(
                    "",
                    "end",
                    text=row["SSID"],
                    values=(
                        row["BSSID"],
                        row["Channel"],
                        row["Signal"],
                        row["Encryption"],
                        str(risk) + "%",
                        distance,
                        safety
                    ),
                    tags=(tag,)
                )

            if safe_candidates:
                safe_candidates.sort()
                best_ssid = safe_candidates[0][2]
                best_network_label.config(
                    text=f"Recommended Safe Network: {best_ssid}"
                )
            else:
                best_network_label.config(
                    text="Recommended Safe Network: No safe network found"
                )

            try:
                show_graph(df)
            except Exception as e:
                print("Graph error:", e)

            if alert:
                alert_label.config(
                    text="⚠ Rogue Access Point Detected!",
                    fg="red"
                )
            else:
                alert_label.config(
                    text="No Rogue Access Point Detected",
                    fg="green"
                )

            # Play sound only when state changes from no rogue -> rogue
            if alert and not last_alert_state:
                try:
                    winsound.PlaySound(
                        sound_path,
                        winsound.SND_FILENAME | winsound.SND_ASYNC
                    )
                except:
                    winsound.MessageBeep()

            last_alert_state = alert

        else:
            status_label.config(text="Scanner Status: Waiting for scan results...")
            best_network_label.config(text="Recommended Safe Network: Scanning...")
            alert_label.config(
                text="No Rogue Access Point Detected",
                fg="green"
            )

        # Fast UI refresh; scanning still happens in background
        root.after(1000, refresh)

    refresh()
    root.mainloop()