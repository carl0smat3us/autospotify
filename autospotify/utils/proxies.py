import requests

from autospotify.exceptions import IpAddressError


def transform_proxy(proxy: str, as_dict: bool = False):
    """
    Transforms a proxy from 'host:port:user:pass' to 'http://user:pass@host:port' or a dictionary.
    """
    try:
        host, port, user, password = proxy.split(":")

        return (
            {"host": host, "port": port, "user": user, "password": password}
            if as_dict
            else f"http://{user}:{password}@{host}:{port}"
        )
    except ValueError:
        raise ValueError("Invalid proxy format. Expected format: host:port:user:pass")


def reverse_transform(proxy: str) -> str:
    """Reverses a proxy from 'http://user:pass@host:port' format to 'host:port:user:pass'."""
    try:
        user_pass, host_port = proxy.split("@")
        user, password = user_pass.replace("http://", "").split(":")
        host, port = host_port.split(":")
        return f"{host}:{port}:{user}:{password}"
    except ValueError:
        raise ValueError(
            "Invalid proxy format. Expected format: http://user:pass@host:port"
        )


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
