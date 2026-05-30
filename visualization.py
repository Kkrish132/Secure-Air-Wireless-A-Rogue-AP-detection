import matplotlib.pyplot as plt

def show_signal_strength(df):

    plt.figure(figsize=(8,4))

    plt.bar(df["SSID"], df["Signal"])

    plt.title("WiFi Signal Strength")

    plt.xlabel("Network")

    plt.ylabel("Signal (dBm)")

    plt.show()



    