def calculate_risk(row):

    score = 0

    encryption = str(row.get("Encryption", "")).upper()
    signal = row.get("Signal")
    ssid = str(row.get("SSID", "")).lower()
    channel = str(row.get("Channel", ""))

    # Open network risk
    if "OPEN" in encryption:
        score += 40

    # Weak or unknown encryption
    if "WEP" in encryption:
        score += 30

    # Strong signal can indicate nearby fake AP
    if signal is not None:
        try:
            signal = float(signal)
            if signal > 80:
                score += 20
            elif signal > 60:
                score += 10
        except:
            pass

    # Common suspicious names
    suspicious_words = ["free", "guest", "public", "wifi"]
    for word in suspicious_words:
        if word in ssid:
            score += 10

    # Some commonly crowded channels
    if channel in ["1", "6", "11"]:
        score += 5

    if score > 100:
        score = 100

    return score


def estimate_distance(signal):
    """
    Rough distance estimate based on signal percentage.
    This is approximate, not exact.
    """
    try:
        signal = float(signal)
    except:
        return "Unknown"

    if signal >= 80:
        return "Within 20 metres"
    elif signal >= 60:
        return "Within 50 metres"
    elif signal >= 40:
        return "Within 100 metres"
    else:
        return "More than 100 metres"


def get_safety_status(row, rogue_networks):
    """
    Gives final user-friendly safety recommendation.
    """
    ssid = str(row.get("SSID", ""))
    encryption = str(row.get("Encryption", "")).upper()
    risk = calculate_risk(row)

    if ssid in rogue_networks:
        return "ROGUE"

    if "OPEN" in encryption and risk >= 40:
        return "SUSPICIOUS"

    if risk >= 60:
        return "SUSPICIOUS"

    return "SAFE"


    