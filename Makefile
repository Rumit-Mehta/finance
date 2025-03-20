init:
	@python3 -m venv .venv
	@.venv/bin/pip3 install -r requirements.txt
setup:
	@python3 setup.py
lint:
	@.venv/bin/black .
auth:
	@python3 -m finance.monzo.monzo_auth
run:
	@osascript -e 'if application "Microsoft Excel" is running then tell application "Microsoft Excel" to if (count of workbooks) > 0 then close active workbook without saving'
	@python3 app.py
	@open files/finance_master_sheet_test.xlsx