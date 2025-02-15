from typing import Literal, Optional

from pydantic import BaseModel
from selenium.webdriver.common.by import ByType


class FindElement(BaseModel):
    by: ByType
    value: str


class User(BaseModel):
    username: str
    password: str

    mail_account_used: Literal["yes", "no"] = None
    spotify_account_confirmed: Literal["yes", "no"] = None


class AccountFilter(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None

    mail_account_used: Literal["yes", "no"] = None
    spotify_account_confirmed: Literal["yes", "no"] = None
