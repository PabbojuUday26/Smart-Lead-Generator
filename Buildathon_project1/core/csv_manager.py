import pandas as pd

def save_to_csv(data, filename="emails.csv"):
    df = pd.DataFrame(data, columns=["username", "email"])
    df.to_csv(f"data/{filename}", index=False)
    print(f"✔ Saved {len(data)} emails into data/{filename}")

def read_csv(filename="data/emails.csv"):
    return pd.read_csv(filename)
