init:
	@python3 -m venv .venv
	@.venv/bin/pip3 install -r requirements.txt

run:
	@python3 app.py
	@open files/finance_master_sheet_test.xlsx