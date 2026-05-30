import subprocess
import pandas as pd
import re

def scan_wifi():

    try:
        result = subprocess.check_output(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            encoding="utf-8"
        )
    except:
        print("Scan failed")
        return None

    networks = []

    ssid = None

    lines = result.split("\n")

    for line in lines:

        line = line.strip()

        # SSID
        if line.startswith("SSID") and "BSSID" not in line:
            parts = line.split(":")
            if len(parts) > 1:
                ssid = parts[1].strip()

        # BSSID
        elif "BSSID" in line:
            bssid = line.split(":")[1].strip()

        # Signal
        elif "Signal" in line:
            signal = int(re.findall(r"\d+", line)[0])

        # Channel
        elif "Channel" in line:
            channel = line.split(":")[1].strip()

            # SAVE ENTRY after channel (complete block)
            networks.append([
                ssid,
                bssid,
                channel,
                signal,
                "Unknown"
            ])

    df = pd.DataFrame(networks,
        columns=["SSID","BSSID","Channel","Signal","Encryption"])

    return df