init:
	@python3 -m venv .venv
	@.venv/bin/pip3 install -r requirements.txt
lint:
	@.venv/bin/black .
auth:
	@python3 -m finance.monzo.monzo_auth
run:
	@python3 app.py
	@open files/finance_master_sheet_test.xlsx