def detect_rogue(df):

    rogue_networks = []

    grouped = df.groupby("SSID")

    for ssid, group in grouped:

        if len(group["BSSID"].unique()) > 1:
            rogue_networks.append(ssid)

    return rogue_networks