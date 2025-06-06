from portfolio.loaders.utils import asset_pair, currency, number, pair, parse_date

FUNCTIONS = {"currency": currency, "date": parse_date, "pair": pair, "asset_pair": asset_pair}


class Parser:
    def __init__(self, row: dict[str, str], schema: dict[str, str]):
        self.t = {}
        self.row = row
        for key, locator in schema.items():
            if type(locator) is dict:
                self.t[key] = self.parse_dict(locator)
            elif type(locator) is str:
                self.t[key] = self.parse_str(locator)

    def parse_dict(self, locator: dict[str, str | dict | list[str]]) -> bool:
        match locator["TYPE"]:
            case "ANY":
                value = self.row[locator["KEY"]].lower()
                if type(locator["ANY"]) is dict:
                    for k, v in locator["ANY"].items():
                        if type(v) is not list or k == "DEFAULT":
                            continue
                        if any(i.lower() in value for i in v):
                            return k
                    else:
                        return locator["ANY"]["DEFAULT"]
                else:
                    return any(i.lower() in value for i in locator["ANY"])

    def parse_str(self, locator: str) -> str:
        _type, value = locator.split(":", 1)
        match _type:
            case "KEY":
                return self.row[value].replace(",", ".")
            case "SUB":
                a, b = value.split(",", 1)
                return str(number(self.row.get(a, self.t.get(a))) - number(self.row[b]))
            case "MUL_OR_DIV":
                a, b, c = value.split(",", 2)
                if self.row[c] == "False":
                    return str(number(self.row[a]) * number(self.row[b]))
                else:
                    return f"{number(self.row[b]) / number(self.row[a]):<.16f}"
            case "STRING":
                return value
            case "FUNC":
                f, v = value.split(":", 1)
                return FUNCTIONS[f](self.row[v])

    def __getitem__(self, id):
        return self.t.get(id)
