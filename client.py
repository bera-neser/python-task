import argparse
import csv
import requests
import datetime
import pandas as pd

examples = """
Examples:
[+] python3 client.py -k string1 string2
[+] python3 client.py -k string1 --no-colored
"""

parser = argparse.ArgumentParser(
    description="Scrape websites to find every URL in it recursively.",
    epilog=examples,
    formatter_class=argparse.RawDescriptionHelpFormatter,
)

parser.add_argument(
    "-k",
    "--keys",
    dest="keys",
    type=str,
    nargs="+",
    help="arbitrary amount of string arguments",
)

parser.add_argument(
    "-c",
    "--colored",
    dest="colored",
    action=argparse.BooleanOptionalAction,
    default=True,
    help="switch the colored option of cells. Default is colored",
)


def transmit(file):
    """
    Transmit CSV file containing vehicle information to the POST Call of the server.
    """
    with open(file, "r") as f:
        csv_reader = csv.DictReader(f, delimiter=";")
        vehicles = [vehicle for vehicle in csv_reader]

    r = requests.post(url="http://127.0.0.1:8000/vehicles", json=vehicles)

    data, colorCode = r.json()

    convert(data, colorCode)


def convert(data, colorCode):
    """
    Convert the server's response into an excel file.
    """

    months = datetime.datetime.today() - datetime.timedelta(days=90)
    year = datetime.datetime.today() - datetime.timedelta(days=365)

    df = pd.DataFrame(data=data)
    writer = pd.ExcelWriter(vehicles_xlsx, "xlsxwriter")

    df.sort_values("gruppe", inplace=True)
    df.to_excel(writer, "vehicles", index=False)

    # TODO: "If the -c flag is True, color each row depending on the following logic:"
    if args.colored:
        for d in data:
            if d.get("hu") and datetime.datetime.strptime(d["hu"], "%Y-%m-%d") > months:
                rnr = d["rnr"]
                color = "#007500"
            elif d.get("hu") and datetime.datetime.strptime(d["hu"], "%Y-%m-%d") > year:
                rnr = d["rnr"]
                color = "#FFA500"
            elif d.get("hu") and datetime.datetime.strptime(d["hu"], "%Y-%m-%d") < year:
                rnr = d["rnr"]
                color = "#B30000"

    # TODO: "..., use the first colorCode to tint the cell's text (if labelIds is given in -k)"
    if "labelIds" in args.keys:
        pass  # colorCode

    writer.close()


if __name__ == "__main__":
    args = parser.parse_args()

    csv_file = "vehicles.csv"
    vehicles_xlsx = f"vehicles_{datetime.date.today()}.xlsx"
    vehicles = list()

    if args.keys:
        for i, key in enumerate(args.keys):
            if key.endswith(","):
                args.keys[i] = key[:-1]

    transmit(csv_file)
