from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict
from selenium.webdriver.common.by import ByType
from selenium.webdriver.remote.webelement import WebElement


class MailBox(BaseModel):
    element: WebElement
    sender: str
    subject: str
    date: str

    model_config = ConfigDict(arbitrary_types_allowed=True)


class Proxy(BaseModel):
    host: str
    port: str
    username: str
    password: str


class FindElement(BaseModel):
    by: ByType
    value: str


class User(BaseModel):
    username: str
    password: str

    proxy_url: Optional[str] = None

    spotify_account_created: Literal["yes", "no"] = "no"
    spotify_account_added_manually: Literal["yes", "no"] = "no"
    email_account_added_manually: Literal["yes", "no"] = "no"


class AccountFilter(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None

    spotify_account_created: Literal["yes", "no"] = None
