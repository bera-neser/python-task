import itertools
import requests
from fastapi import FastAPI


class Vehicle(dict):
    gruppe: str
    kurzname: str
    langtext: str
    info: str
    lagerort: str
    labelIds: int


app = FastAPI()

login = "https://api.baubuddy.de/index.php/login"
resources = "https://api.baubuddy.de/dev/index.php/v1/vehicles/select/active"
headers = {"Authorization": "Basic QVBJX0V4cGxvcmVyOjEyMzQ1NmlzQUxhbWVQYXNz"}
auth = {"username": "365", "password": "1"}


@app.post("/vehicles", status_code=201)
async def vehicles(vehicles: list[Vehicle]):
    global headers
    with requests.Session() as session:
        session.headers.update(headers)

        r = session.post(url=login, json=auth)

        access_token = r.json()["oauth"]["access_token"]
        token_header = {"Authorization": f"Bearer {access_token}"}

        session.headers.update(token_header)

        # Take the resources and set them to "data" variable with a JSON format
        r = session.get(url=resources)

        data = r.json()

        # Filter out the resources that do not have value set for "hu" field
        data = [valid for valid in data if valid["hu"] is not None]

        colorCode = ""

        for resource in itertools.chain(vehicles, data):
            if resource["labelIds"] != None and resource["labelIds"] != "":
                r = session.get(
                    f"https://api.baubuddy.de/dev/index.php/v1/labels/{resource['labelIds']}"
                )
                if (
                    r.status_code == requests.codes.ok
                    and r.json()
                    and r.json()[0].get("colorCode")
                ):
                    colorCode = r.json()[0]["colorCode"]
                    break

    return data + vehicles, colorCode
