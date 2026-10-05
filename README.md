# Settlement Tracker - Streamlit

A Streamlit conversion of the Excel/Power Query settlement tracker.

## Inputs

Upload separately:
1. Citibank Statement
2. BOU Statement
3. Cash Flow
4. Citi Identifiers
5. BOU Identifiers

## Run locally

Open this folder in VS Code, open Terminal, then:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install:

```bash
pip install -r requirements.txt
```

Run:

```bash
streamlit run app.py
```

The browser will open the application.

## Matching approach

The application intentionally keeps the matching logic simple and close to the supplied Power Query:
- Citi receipts: Currency + Amount + Counterparty
- Citi payments: Deal No contained in Customer Reference
- BOU payments: Deal No contained in BOU REF
- BOU receipts: Counterparty + Credit amount
- Internal counterparties follow the rules in the supplied M code
- Citi London has the special multiple-receipt/payment handling
