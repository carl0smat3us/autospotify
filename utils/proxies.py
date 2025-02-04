import os
import tempfile
import zipfile

import requests

from utils.logs import logger


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
        proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
        response = requests.get(
            "https://api.ipify.org?format=json", proxies=proxies, timeout=10
        )
        response.raise_for_status()
        return response.json().get("ip", "Unknown IP")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching IP: {e}")
        return "Unknown IP"


def create_proxy_extension(proxy: str) -> str:
    """
    Creates a Chrome extension for proxy authentication using extracted proxy details.
    """
    proxy_data = transform_proxy(reverse_transform(proxy), as_dict=True)
    manifest_json = """{
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Proxy Auth Extension",
        "permissions": ["proxy", "tabs", "unlimitedStorage", "storage", "<all_urls>", "webRequest", "webRequestBlocking"],
        "background": {"scripts": ["background.js"]},
        "minimum_chrome_version": "22.0.0"
    }"""

    background_js = f"""
    var config = {{
        mode: "fixed_servers",
        rules: {{
            singleProxy: {{
                scheme: "http",
                host: "{proxy_data['host']}",
                port: parseInt({proxy_data['port']})
            }},
            bypassList: ["localhost"]
        }}
    }};

    chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

    chrome.webRequest.onAuthRequired.addListener(
        function(details) {{
            return {{
                authCredentials: {{
                    username: "{proxy_data['user']}",
                    password: "{proxy_data['password']}"
                }}
            }};
        }},
        {{urls: ["<all_urls>"]}},
        ["blocking"]
    );
    """
    plugin_file_path = os.path.join(tempfile.gettempdir(), "proxy_auth_plugin.zip")

    with zipfile.ZipFile(plugin_file_path, "w") as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    return plugin_file_path
