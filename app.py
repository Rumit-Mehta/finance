from finance.monzo import monzo
import logging 

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def main():
    # Get Monzo transactions and add to spreadsheet
    monzo.run()

if __name__ == "__main__":
    main()
    print("- - DONE - -")





