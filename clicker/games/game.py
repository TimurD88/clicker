from abc import ABC, abstractmethod
import base64
import random
import traceback
from typing import Tuple
import httpx
import playwright
from playwright.async_api import Page, Error, Route, TimeoutError
import asyncio
import hashlib
import coloredlogs
import logging

from getuseragent import UserAgent
from async_timeout import timeout
import playwright.async_api

useragent = UserAgent("android")


def route_intercept(route):
    if route.request.resource_type == "font":
        return route.abort()
    return route.continue_()


class Game(ABC):
    logger: logging.Logger
    page: Page
    url: str
    balance: float
    sub_balance: float
    storage: dict
    error: str
    owner_id: int
    user_id: str
    debug: bool

    def __init__(
        self,
        page: Page,
        url: str,
        user_id: str,
        owner_id: int,
        storage: dict = None,
        debug: bool = False,
    ) -> None:
        self.error = ""
        self.logger = logging.getLogger().getChild(self.name)
        # coloredlogs.install(logger=self.logger, level=logging.INFO)
        self.loop = asyncio.get_event_loop()
        self.page = page
        self.url = url
        # TODO: user_id replace with account_id
        self.user_id = user_id
        self.account_id = user_id

        self.owner_id = owner_id
        self.hash = int(hashlib.sha1(user_id.encode("utf-8")).hexdigest(), 16) % (
            10**12
        )
        self.balance = 0.0
        self.sub_balance = 0.0
        self.storage = storage
        self.debug = debug

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError()

    def provide_ref_url(self, ref_url: str, limit: int = None) -> None:
        self.logger.info(f"[provide_ref_url]:{self.owner_id}:{self.name}:{ref_url}")
        
    async def goto(self, url: str, timeout=60000, retry=5):
        while retry > 0:
            try:
                await self.page.goto(url, timeout=timeout)
                break
            except Error as e:
                retry -= 1
                if retry == 0:
                    raise e
                await asyncio.sleep(30)

    async def run(self):
        result = {
            "project": self.name,
            "balance": 0.0,
            "sub_balance": 0.0,
            "error": "",
        }
        self.logger.info("run start")
        try:
            async with timeout(900) as cm:
                await self._run()
                self.logger.info(f"run done:{self.balance}:{self.sub_balance}")
                await asyncio.sleep(random.randint(10, 15))
                await self.page.close()
        except asyncio.TimeoutError:
            self.logger.info("timeout game run")
            await asyncio.sleep(random.randint(10, 15))
        except Exception as e:
            self.error = traceback.format_exc()
            self.logger.error(traceback.format_exc())
            self.logger.error(e)
            await asyncio.sleep(random.randint(10, 15))
            if self.debug:
                await asyncio.sleep(600000)
        finally:
            await self.page.close()
        result["balance"] = self.balance
        result["sub_balance"] = self.sub_balance
        result["storage"] = self.storage
        result["error"] = self.error
        return result

    @abstractmethod
    async def _run(self) -> Tuple[float, float]:
        raise NotImplementedError()
