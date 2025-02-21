import subprocess


def get_chrome_version():
    try:
        output = subprocess.check_output(
            r'wmic datafile where name="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" get Version /value',
            shell=True,
        ).decode()
        return output.strip().split("=")[-1]
    except Exception:
        return None
