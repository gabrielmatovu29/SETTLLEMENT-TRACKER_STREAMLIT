import os
import pandas as pd
from io import BytesIO
from src.utilities import money_range

DATA_DIR = "data"

def load_excel_or_csv(source):
    """Utility to read either an uploaded file object or a local file path (xlsx/csv)."""
    if isinstance(source, str):
        if source.endswith(".csv"):
            return pd.read_csv(source)
        return pd.read_excel(source)
    else:
        try:
            return pd.read_excel(source)
        except Exception:
            source.seek(0)
            return pd.read_csv(source)

def process_citi_identifiers(file=None):
    if file is None:
        file = os.path.join(DATA_DIR, "citi_identifiers.xlsx")
        if not os.path.exists(file):
            file = os.path.join(DATA_DIR, "citi_identifiers.csv")

    if isinstance(file, str) and not os.path.exists(file):
        return pd.DataFrame(columns=["IDENTIFIER", "COUNTERPARTY"])

    df = load_excel_or_csv(file)
    required = ["IDENTIFIER", "COUNTERPARTY"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Citi Identifiers are missing columns: {missing}")
    return df[required].astype(str).apply(lambda s: s.str.strip())

def process_bou_identifiers(file=None):
    if file is None:
        file = os.path.join(DATA_DIR, "bou_identifiers.xlsx")
        if not os.path.exists(file):
            file = os.path.join(DATA_DIR, "bou_identifiers.csv")

    if isinstance(file, str) and not os.path.exists(file):
        return pd.DataFrame(columns=["LOCAL BANK", "CODE"])

    df = load_excel_or_csv(file)
    required = ["LOCAL BANK", "CODE"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"BOU Identifiers are missing columns: {missing}")
    return df[required].astype(str).apply(lambda s: s.str.strip())

def save_citi_identifiers(df_or_file):
    os.makedirs(DATA_DIR, exist_ok=True)
    target_path = os.path.join(DATA_DIR, "citi_identifiers.xlsx")
    if isinstance(df_or_file, pd.DataFrame):
        df_or_file.to_excel(target_path, index=False)
    else:
        # File buffer
        df = load_excel_or_csv(df_or_file)
        df.to_excel(target_path, index=False)

def save_bou_identifiers(df_or_file):
    os.makedirs(DATA_DIR, exist_ok=True)
    target_path = os.path.join(DATA_DIR, "bou_identifiers.xlsx")
    if isinstance(df_or_file, pd.DataFrame):
        df_or_file.to_excel(target_path, index=False)
    else:
        df = load_excel_or_csv(df_or_file)
        df.to_excel(target_path, index=False)

def process_cashflow(file):
    raw = pd.read_excel(file, header=None)
    header_idx = None

    for i in range(len(raw)):
        values = [str(x).strip() for x in raw.iloc[i].tolist()]
        required_headers = {
            "Amount", "CashFlow date", "Comment",
            "Counterparty Name", "Currency", "Deal No"
        }
        if required_headers.issubset(set(values)):
            header_idx = i
            break

    if header_idx is None:
        raise ValueError(
            "Could not find Cash Flow headers: Amount, CashFlow date, Comment, Counterparty Name, Currency, Deal No."
        )

    headers = [
        str(x).strip() if pd.notna(x) else f"Column{i}"
        for i, x in enumerate(raw.iloc[header_idx])
    ]

    df = raw.iloc[header_idx + 1:].copy()
    df.columns = headers

    needed = ["Amount", "CashFlow date", "Comment", "Counterparty Name", "Currency", "Deal No"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"Cash Flow missing columns: {missing}")

    df = df[needed].copy()
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df["CashFlow date"] = pd.to_datetime(df["CashFlow date"], errors="coerce")
    df = df[df["Amount"].notna()].copy()
    df["RANGE"] = df["Amount"].apply(money_range)
    df["DIR"] = df["Amount"].apply(lambda x: "-" if x < 0 else "+")
    df["Deal No"] = df["Deal No"].astype(str).str.strip()

    rows = []
    skip_next = False
    for i in range(len(df)):
        if skip_next:
            skip_next = False
            continue

        current = df.iloc[i].copy()
        if i + 1 < len(df):
            next_row = df.iloc[i + 1]
            same_deal = str(current["Deal No"]) == str(next_row["Deal No"])
            same_direction = current["DIR"] == next_row["DIR"]

            if same_deal and same_direction:
                current["Amount"] = current["Amount"] + next_row["Amount"]
                skip_next = True

        rows.append(current)

    df = pd.DataFrame(rows).reset_index(drop=True)
    df["RANGE"] = df["Amount"].apply(money_range)

    df["Ref and dir"] = df["Deal No"].astype(str) + df["DIR"].astype(str)
    df = df.drop_duplicates(subset=["Ref and dir"], keep="first")
    df = df.sort_values("Deal No", ascending=False, na_position="last")
    df = df.drop(columns=["DIR", "Ref and dir"], errors="ignore")

    return df[["CashFlow date", "Comment", "RANGE", "Counterparty Name", "Deal No", "Currency", "Amount"]].reset_index(drop=True)

def process_citi(file, citi_ids):
    raw = pd.read_excel(file, header=None)
    currencies = {"USD", "EUR", "GBP", "CHF", "JPY", "AUD"}

    header_idx = None
    for i in range(len(raw)):
        vals = [str(x).strip() for x in raw.iloc[i].tolist()]
        if "Transaction Amount" in vals:
            header_idx = i
            break

    if header_idx is None:
        raise ValueError("Could not find the Citi header row containing 'Transaction Amount'.")

    headers = [str(x).strip() if pd.notna(x) else f"Column{i}" for i, x in enumerate(raw.iloc[header_idx])]
    data = raw.iloc[header_idx + 1:].copy()
    data.columns = headers

    currency_series = []
    current_currency = None
    for i in range(len(raw)):
        val = raw.iloc[i, 1] if raw.shape[1] > 1 else None
        if pd.notna(val) and str(val).strip() in currencies:
            current_currency = str(val).strip()
        if i > header_idx:
            currency_series.append(current_currency)
    data["CURRENCY"] = currency_series[:len(data)]

    if "CURRENCY" in data.columns:
        data["CURRENCY"] = data["CURRENCY"].fillna("").replace("", pd.NA)

    required = [
        "Entry Date", "Value Date", "Transaction Description",
        "Customer Reference", "Bank Reference",
        "By Order Of / Beneficiary", "Transaction Amount", "CURRENCY"
    ]
    for col in required:
        if col not in data.columns:
            data[col] = pd.NA

    data = data[data["Transaction Amount"].notna()].copy()
    data = data[data["Transaction Amount"].astype(str).str.strip() != "Transaction Amount"].copy()
    data["Transaction Amount"] = pd.to_numeric(data["Transaction Amount"], errors="coerce")
    data = data[data["Transaction Amount"].notna()].copy()

    ids = citi_ids.copy()
    if not ids.empty:
        ids["IDENTIFIER"] = ids["IDENTIFIER"].astype(str).str.strip()
        ids["COUNTERPARTY"] = ids["COUNTERPARTY"].astype(str).str.strip()

    data["By Order Of / Beneficiary"] = data["By Order Of / Beneficiary"].astype(str).str.strip()
    data = data.merge(
        ids, how="left",
        left_on="By Order Of / Beneficiary",
        right_on="IDENTIFIER"
    )
    data.drop(columns=["IDENTIFIER"], inplace=True, errors="ignore")
    data["RANGE"] = data["Transaction Amount"].apply(money_range)

    def irregular(row):
        cp = row.get("COUNTERPARTY")
        desc = str(row.get("Transaction Description", ""))
        amt = row.get("Transaction Amount")
        if pd.isna(cp) or str(cp).lower() in ("nan", ""):
            if pd.notna(amt) and amt > 0 and desc == "FX SETTLEMENT":
                return "Citibank N.A. London.-UG"
            if pd.notna(amt) and amt < 0 and desc == "INTERNAL SETTLEMENT":
                return "Citibank N.A. London.-UG"
            return pd.NA
        return cp

    data["COUNTERPARTY"] = data.apply(irregular, axis=1)
    cols = [
        "Entry Date", "Value Date", "RANGE", "Transaction Description",
        "Customer Reference", "Bank Reference", "By Order Of / Beneficiary",
        "COUNTERPARTY", "CURRENCY", "Transaction Amount"
    ]
    return data[cols].reset_index(drop=True)

def process_bou(file, bou_ids):
    raw = pd.read_excel(file, header=None)
    raw = raw.dropna(subset=[2, 3], how="any").copy()

    raw.columns = raw.iloc[0].tolist()
    df = raw.iloc[1:].copy()

    drop_cols = [
        "Entry Seq no", "Setlm agrmnt name./ batch seq no.",
        "Concurrently settled", "Balance"
    ]
    df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True, errors="ignore")

    ref_col = "Originator instruction reference code"
    if ref_col not in df.columns:
        raise ValueError(f"BOU Statement is missing '{ref_col}'.")

    df["Originator instruction reference code.1"] = df[ref_col].astype(str).str[:4]
    df["Originator instruction reference code.2"] = df[ref_col].astype(str).str[4:]

    ids = bou_ids.copy()
    if not ids.empty:
        ids["CODE"] = ids["CODE"].astype(str).str.strip()
        ids["LOCAL BANK"] = ids["LOCAL BANK"].astype(str).str.strip()

    df["Originator instruction reference code.1"] = df["Originator instruction reference code.1"].str.strip()
    df = df.merge(
        ids, how="left",
        left_on="Originator instruction reference code.1",
        right_on="CODE"
    )
    df.rename(columns={"LOCAL BANK": "COUNTERPARTY"}, inplace=True)

    if "Debit" in df.columns:
        df["Debit"] = df["Debit"].apply(
            lambda x: "-" + str(x) if pd.notna(x) and str(x).strip() != "" else pd.NA
        )
        df["Debit"] = pd.to_numeric(df["Debit"], errors="coerce")

    df.rename(columns={"Originator instruction reference code.2": "REF"}, inplace=True)
    return df.reset_index(drop=True)

def build_big_statement(cashflow, citi, bou):
    cf = cashflow.copy()
    c = citi.copy()
    b = bou.copy()

    cf["Currency"] = cf["Currency"].astype(str).str.strip()
    cf["Counterparty Name"] = cf["Counterparty Name"].astype(str).str.strip()
    cf["Deal No"] = cf["Deal No"].astype(str).str.strip()
    c["COUNTERPARTY"] = c["COUNTERPARTY"].astype(str).str.strip()
    c["CURRENCY"] = c["CURRENCY"].astype(str).str.strip()

    receipt_counts = []
    for _, row in cf.iterrows():
        matches = c[
            (c["CURRENCY"] == row["Currency"]) &
            (pd.to_numeric(c["Transaction Amount"], errors="coerce") == row["Amount"]) &
            (c["COUNTERPARTY"] == row["Counterparty Name"])
        ]
        receipt_counts.append(len(matches))

    cf["CITI RECEIVE STATUS"] = [
        None if (pd.isna(a) or a < 0 or cur == "UGX") else
        ("Not Received" if n == 0 else "Received" if n == 1 else f"{n}-Received")
        for a, cur, n in zip(cf["Amount"], cf["Currency"], receipt_counts)
    ]

    customer_refs = c["Customer Reference"].astype(str).tolist()
    paid_status = []
    for _, row in cf.iterrows():
        if pd.isna(row["Amount"]) or row["Amount"] > 0 or row["Currency"] == "UGX":
            paid_status.append(None)
        else:
            deal = str(row["Deal No"])
            found = any(deal in ref for ref in customer_refs)
            paid_status.append("Paid" if found else "Not Paid")
    cf["CITI PAID STATUS"] = paid_status

    def citi_status(row):
        cp = str(row["Counterparty Name"])
        up = cp.upper()
        if "ZEAL" in cp or "HYDERY" in up or "UNIMONI" in up or "ECONOMIC" in up:
            return "Internal"
        if "PRIDE" in up or "SALAAM" in up:
            return "CHECK BOU"
        if pd.notna(row["CITI RECEIVE STATUS"]):
            return row["CITI RECEIVE STATUS"]
        if pd.notna(row["CITI PAID STATUS"]):
            return row["CITI PAID STATUS"]
        return "N/A"

    cf["CITIBANK PAYMENT STATUS"] = cf.apply(citi_status, axis=1)

    london_counts = []
    for _, row in cf.iterrows():
        matches = c[
            (c["CURRENCY"] == row["Currency"]) &
            (pd.to_numeric(c["Transaction Amount"], errors="coerce") == row["Amount"]) &
            (c["COUNTERPARTY"] == row["Counterparty Name"])
        ]
        london_counts.append(len(matches))
    cf["CITILONDON RECIPT COUNT"] = london_counts

    cf["CITILONDON RECIEVED"] = [
        ("Not Received" if n == 0 else "Received" if n == 1 else f"{n}-Received")
        if cp == "Citibank N.A. London.-UG" and status == "Not Received"
        else None
        for cp, status, n in zip(cf["Counterparty Name"], cf["CITIBANK PAYMENT STATUS"], london_counts)
    ]

    cf["citilondon paid status"] = [
        ("Not Paid" if n == 0 else "Paid" if n == 1 else f"Paid Multiple-{n}")
        if cp == "Citibank N.A. London.-UG" and status == "Not Paid"
        else None
        for cp, status, n in zip(cf["Counterparty Name"], cf["CITIBANK PAYMENT STATUS"], london_counts)
    ]

    cf["CITI"] = cf["CITILONDON RECIEVED"].combine_first(
        cf["citilondon paid status"]
    ).combine_first(cf["CITIBANK PAYMENT STATUS"])

    bou_counterparty = b["COUNTERPARTY"].astype(str).str.strip() if "COUNTERPARTY" in b.columns else pd.Series(dtype=str)
    bou_credit = pd.to_numeric(b["Credit"], errors="coerce") if "Credit" in b.columns else pd.Series(dtype=float)
    bou_refs = b["REF"].astype(str).tolist() if "REF" in b.columns else []

    bou_paid = []
    bou_received = []
    for _, row in cf.iterrows():
        if row["Currency"] != "UGX" or row["Amount"] > 0 or str(row["CITI"]).upper() == "INTERNAL":
            bou_paid.append(None)
        else:
            deal = str(row["Deal No"])
            bou_paid.append("Paid" if any(deal in ref for ref in bou_refs) else "Not Paid")

        if row["Currency"] != "UGX" or row["Amount"] < 0 or str(row["CITI"]).upper() == "INTERNAL":
            bou_received.append(None)
        else:
            count = int(((bou_counterparty == row["Counterparty Name"]) & (bou_credit == row["Amount"])).sum())
            bou_received.append(
                "Received" if count == 1 else f"{count}-Received" if count > 1 else "Not Received"
            )

    cf["BOU PAID"] = bou_paid
    cf["BOU RECEIVED"] = bou_received
    cf["BOU STATUS"] = [p if p is not None else r for p, r in zip(bou_paid, bou_received)]

    cf["GEN STATUS"] = [
        bou if pd.notna(bou) and bou not in ("", "None") else citi
        for bou, citi in zip(cf["BOU STATUS"], cf["CITI"])
    ]

    cf.drop(
        columns=[
            "CITI RECEIVE STATUS", "CITI PAID STATUS",
            "CITIBANK PAYMENT STATUS", "CITILONDON RECIPT COUNT",
            "CITILONDON RECIEVED", "citilondon paid status",
            "BOU PAID", "BOU RECEIVED", "BOU STATUS"
        ],
        inplace=True,
        errors="ignore"
    )

    return cf.reset_index(drop=True)