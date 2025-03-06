import requests
import logging
import pandas as pd
from finance.constants import ACCESS_TOKEN

logger = logging.getLogger(__name__)

# Fetch account ID
def get_account_id():
    url = "https://api.monzo.com/accounts"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)
    
    # response.raise_for_status()
    if response.status_code in [200, 201, 204] :
        accounts = response.json()["accounts"]
        logging.debug(f"successful connection to {url}")
        if accounts:
            logging.info("DONE 1/4 - Access acount ID")
            return accounts[0]["id"]  # Using the first account
    raise Exception("Failed to retrieve Monzo account ID.")

# Fetch transactions
def get_transactions(account_id, date_from):
    url = f"https://api.monzo.com/transactions"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    print(f"Date from: {date_from}")
    params = {
        "account_id": account_id,
        "expand[]": "merchant",  # Expands merchant info if available
        "since": str(date_from)
    }
    
    response = requests.get(url, headers=headers, params=params)
    print(f"params: {params}")

    if response.status_code == 200:
        transactions = response.json()["transactions"]    
        
        # if transactions isnt empty
        if transactions:
            # Get the date of the last transaction (assuming the list is in chronological order)
            last_transaction_date = transactions[-1]["created"]

            # Send the date to a text file, overriding previous date
            with open("files/monzo_last_transaction_date.txt", "w") as file:
                file.write(f"{last_transaction_date}")
                logging.info(f"Last transaction date saved: {last_transaction_date}")
        else: 
            logging.info("No transactions found.")

        logging.info("DONE 2/4  - Got transactions from Monzo API")
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
    
    if data:
        logging.info("DONE 3/4 - Converted transactions to dataframe")

    return pd.DataFrame(data)

# Save DataFrame to CSV
def save_to_csv(df, filename="files/monzo_transactions.csv"):
    df.to_csv(filename, index=False)
    logging.info(f"DONE 4/4 - Transactions saved to {filename}")



