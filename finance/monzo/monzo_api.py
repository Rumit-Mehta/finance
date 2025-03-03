import requests
import pandas as pd

from finance.constants import ACCESS_TOKEN


# Fetch account ID
def get_account_id():
    url = "https://api.monzo.com/accounts"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        accounts = response.json()["accounts"]
        print("DONE - get")
        if accounts:
            return accounts[0]["id"]  # Using the first account
    raise Exception("Failed to retrieve Monzo account ID.")

# Fetch transactions
def get_transactions(account_id, date_from):
    url = f"https://api.monzo.com/transactions"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    params = {
        "account_id": account_id,
        "expand[]": "merchant",  # Expands merchant info if available
        "since": date_from
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()["transactions"]
    raise Exception("Failed to retrieve transactions.")

# Convert transactions to a DataFrame
def transactions_to_dataframe(transactions):
    data = []
    for txn in transactions:
        data.append({
            "Date": txn["created"].split("T")[0], # removing the time from the date
            "Amount (GBP)": txn["amount"] / 100,  # Monzo amounts are in pence
            "Description": txn.get("description", ""), 
            "Merchant": txn.get("merchant", {}).get("name", "N/A") if txn.get("merchant") else "N/A",
            "Category": txn.get("category", "N/A"),
            "Notes": txn.get("notes", ""),
        })
    
    return pd.DataFrame(data)

# Save DataFrame to CSV
def save_to_csv(df, filename="files/monzo_transactions.csv"):
    df.to_csv(filename, index=False)
    print(f"Transactions saved to {filename}")



