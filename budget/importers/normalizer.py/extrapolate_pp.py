import csv, copy, datetime
from paypal import load
from decimal import Decimal


def main():
    rows = load("data/statements/20140725-20171225-manual.csv", ";")

    with open("data/statements/output/paypal_in.csv", "r") as file:
        lines = file.readlines()
        fields = [f.strip() for f in lines[0].split(",")]
        r = csv.DictReader(lines[1:], fields, delimiter=",")
        for row in r:
            if row["op"]:
                rows.append(
                    {
                        "Data": datetime.date(*[int(i) for i in row["date"].split("-")]),
                        "Godzina": "00:00:00",
                        "Strefa Czasowa": "Europe/Warsaw",
                        "Opis": "Ogólna wpłata z rachunku karty",
                        "Waluta": "PLN",
                        "Brutto": Decimal(row["amount"].strip("-").replace(",", ".")),
                    }
                )
                continue
            t = None
            for _row in rows:
                if (
                    row["date"] == str(_row["Data"])
                    and Decimal(row["amount"].replace(",", ".")) == _row["Brutto"]
                    and "-" in str(_row["Brutto"])
                ):
                    t = copy.copy(_row)
                elif not t and row["date"] == str(_row["Data"]) and "-" in str(_row["Brutto"]):
                    t = copy.copy(_row)
            if not t:
                print(row)
                continue

            conversion = False
            if t["Waluta"] != "PLN":
                conversion = True
                original = copy.copy(t)
                original["Opis"] = "Ogólne przeliczenie waluty"
                original["Brutto"] = -original["Brutto"]
                rows.append(original)

            t["Brutto"] = Decimal(row["amount"].strip("-").replace(",", "."))
            t["Waluta"] = "PLN"
            t["Opis"] = "Ogólna wpłata z rachunku karty"
            t["Z adresu e-mail"] = ""
            rows.append(t)

            if conversion:
                converted = copy.copy(t)
                converted["Brutto"] = -converted["Brutto"]
                converted["Opis"] = "Ogólne przeliczenie waluty"
                rows.append(converted)
    rows = sorted(rows, key=lambda x: (x["Data"], x["Godzina"]))

    fields = list(rows[0].keys())
    with open("data/statements/output/20140725-20171225-manual.csv", "w", newline="", encoding="utf-8") as file:
        w = csv.DictWriter(file, fields)
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
