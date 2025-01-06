import csv


def load(filepath: str):
    ROWS = []
    with open(filepath, "r") as file:
        lines = file.readlines()
        fields = [f.strip().replace("#", "") for f in lines[37].split(";")]
        r = csv.DictReader(lines[38:708], fields, delimiter=";")
        for row in r:
            if row["Tytuł"].startswith("PAYPAL *") or row["Tytuł"].startswith("PP*") or row["Tytuł"].startswith("PP *"):
                _, date = row["Tytuł"].split("DATA TRANSAKCJI: ")
                ROWS.append({"date": date, "amount": row["Kwota"]})
            if "BLUE MEDIA" in row["Nadawca/Odbiorca"]:
                ROWS.append({"date": row["Data operacji"], "amount": row["Kwota"], "op": True})

    fields = ["date", "amount", "op"]
    with open("data/statements/output/paypal_in.csv", "w", newline="", encoding="utf-8") as file:
        w = csv.DictWriter(file, fields)
        w.writeheader()
        w.writerows(ROWS)


if __name__ == "__main__":
    load("data/statements/mbank/mbank_2014-2024.csv")
