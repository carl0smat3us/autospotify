import requests


def get_proxies():
    url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
    response = requests.get(url)

    if response.status_code == 200:
        return response.text.splitlines()
    else:
        raise Exception("Error to get the proxy list")
