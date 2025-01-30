import random

import requests


def get_proxies():
    url = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&country=us,fr,be&protocol=http&proxy_format=protocolipport&format=text&anonymity=Elite,Anonymous&timeout=20000"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text.splitlines()
    except requests.exceptions.RequestException as e:
        print(f"Error getting proxy list: {e}")
        return []


def test_proxy(proxy):
    try:
        proxy_dict = {"http": proxy, "https": proxy}
        response = requests.get("http://www.spotify.com", proxies=proxy_dict, timeout=5)
        response.raise_for_status()
        return proxy
    except requests.exceptions.RequestException:
        return None


def get_a_working_proxy():
    proxies = get_proxies()
    if not proxies:
        return None

    while proxies:
        proxy = random.choice(proxies)
        result = test_proxy(proxy)
        if result:
            return result
        else:
            proxies.remove(proxy)
            print(f"Proxy {proxy} failed. Trying another one.")

    return None


def get_user_ip(proxy: str):
    proxy_dict = None
    try:
        if proxy:
            proxy_dict = {"http": proxy, "https": proxy}
        response = requests.get(
            "https://api.ipify.org?format=json", proxies=proxy_dict, timeout=10
        )
        response.raise_for_status()
        ip_data = response.json()
        return ip_data.get("ip")
    except requests.exceptions.RequestException as e:
        print(f"Failed to get user IP using proxy {proxy}: {e}")
        return None
