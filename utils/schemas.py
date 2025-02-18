from typing import Literal, Optional

from pydantic import BaseModel
from selenium.webdriver.common.by import ByType


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

    spotify_account_created: Literal["yes", "no"] = "no"
    spotify_account_activated: Literal["yes", "no"] = "no"


class AccountFilter(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None

    spotify_account_created: Literal["yes", "no"] = None
    spotify_account_activated: Literal["yes", "no"] = None
