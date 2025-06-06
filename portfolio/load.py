from collections import defaultdict
from datetime import UTC, datetime

from portfolio.models import Transaction
from portfolio.loaders.helpers import save, load_statement
from portfolio.loaders.schema import Schema
from portfolio.loaders.parser import Parser
import tqdm


def fix_transfers(seen: dict[datetime, list[Transaction]]):
    for ts in tqdm.tqdm(seen, unit="tx", desc="Fixing transfer transactions"):
        note = seen[ts][0].note
        for t in seen[ts]:
            if any(i in note for i in [" to ", " from "]):
                break
            if "USDCs" in t.note and len(seen[ts]) == 1:
                t.type = "BORROW"
                t.note = t.note.replace(" LIQUIDATION", "")


def parse(rows, schema, skip_dupes=False, ledger: list[Transaction] = list):
    transactions: list[Transaction] = []
    seen: dict[datetime, list[Transaction]] = defaultdict(lambda: list())
    for row in tqdm.tqdm(rows, unit="tx", desc="Parsing transactions"):
        d = Schema(**Parser(row, schema).t)
        t = d.to_transaction()

        if skip_dupes:
            if any(t.timestamp == i.timestamp for i in ledger):
                continue
        if "Advanced" in t.exchange and t.timestamp < datetime(2025, 6, 1, tzinfo=UTC) and t.note != "LIQUIDATION":
            continue

        if "LIQUIDATION" in t.note:
            seen[t.timestamp].append(t)
        transactions.append(t)

        if tc := d.should_convert(t, d.trade):
            if d.buy:
                transactions.insert(-1, tc)
            else:
                transactions.append(tc)
    fix_transfers(seen)

    return transactions


if __name__ == "__main__":
    t = []
    # t += parse(*load_statement("coinbase/coinbase_2024"))
    t += parse(*load_statement("coinbase/coinbase_2024-20250531"))
    # t += parse(*load_statement("cdp/cdp_spot"), skip_dupes=True, ledger=t)
    # t += parse(*load_statement("cdp/cdp_perp"), skip_dupes=True, ledger=t)
    # t += parse(*load_statement("revolut/crypto-account-statement_2024-08-12_2025-03-14_pl-pl_d1b997"))
    # t += parse(*load_statement("revolut/revx-account-statement_2024-07-28_2025-03-14_pl-pl_b0e83c", x=True))
    save(t)
