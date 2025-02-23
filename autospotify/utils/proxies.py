import requests

from autospotify.exceptions import IpAddressError
from autospotify.utils.schemas import Proxy


def proxy_transformed_url_to_dict(proxy: str) -> Proxy:
    """
    Transforms a proxy from 'http://user:pass@host:port' to a Proxy object.
    """
    proxy = proxy.replace("http://", "")

    user_pass, host_port = proxy.split("@")
    username, password = user_pass.split(":")
    host, port = host_port.split(":")

    return Proxy(username=username, password=password, host=host, port=port)


def transform_proxy(proxy: str):
    """
    Transforms a proxy from 'host:port:user:pass' to 'http://user:pass@host:port
    """
    try:
        host, port, username, password = proxy.split(":")

        return f"http://{username}:{password}@{host}:{port}"
    except ValueError:
        raise ValueError("Invalid proxy format. Expected format: host:port:user:pass")


def get_user_ip(proxy_url: str = None) -> str:
    """
    Fetches the public IP address using a proxy (if provided).
    """
    try:
        proxy = (
            {
                "http": proxy_url,
                "https": proxy_url,
            }
            if proxy_url
            else None
        )
        response = requests.get(
            "https://api.ipify.org?format=json", proxies=proxy, timeout=10
        )
        response.raise_for_status()
        return response.json().get("ip", "Unknown IP")
    except requests.exceptions.RequestException as e:
        raise IpAddressError(f"Error fetching IP: {e}")
