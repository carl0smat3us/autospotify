import requests


def transform_proxy(proxy: str) -> str:
    """Transforms a proxy from 'host:port:user:pass' format to 'http://user:pass@host:port'."""
    try:
        host, port, user, password = proxy.split(":")
        return f"http://{user}:{password}@{host}:{port}"
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
    """Fetches the public IP address using a proxy (if provided)."""
    try:
        proxy_dict = {"http": proxy_url, "https": proxy_url} if proxy_url else None
        response = requests.get(
            "https://api.ipify.org?format=json", proxies=proxy_dict, timeout=10
        )
        response.raise_for_status()
        return response.json().get("ip")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
