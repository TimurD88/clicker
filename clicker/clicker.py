import datetime
import glob
import json
import os
import httpx
from playwright.async_api import (
    async_playwright,
    Route,
)
from playwright.async_api import Page, Error

import asyncio
import hashlib
import coloredlogs
import logging
from getuseragent import UserAgent
from clicker.games.game import Game
from clicker.games.tapswap import Tapswap
from clicker.games.tonique import Tonique

import pickle
import fnv_c

useragent = UserAgent("android")
S_PATH = "https://s.ton-airdrops.org"


class GatheringTaskGroup(asyncio.TaskGroup):
    def __init__(self):
        super().__init__()
        self.__tasks = []

    def create_task(self, coro, *, name=None, context=None):
        task = super().create_task(coro, name=name, context=context)
        self.__tasks.append(task)
        return task

    def results(self):
        return [task.result() for task in self.__tasks]


class Cache:
    memory: dict

    def __init__(self) -> None:
        self.memory = {}
        os.makedirs("./cache", exist_ok=True)
        for file_name in glob.glob("./cache/*"):
            with open(file_name, "rb") as f:
                self.memory[int(file_name.replace("./cache/", ""))] = pickle.load(f)

    def url_hash(self, url: str) -> int:
        return fnv_c.fnv1a_32(str.encode(url))

    def has(self, url) -> bool:
        url_hash = self.url_hash(url)
        return url_hash in self.memory
    def get(self, url) -> dict:
        return self.memory[self.url_hash(url)]

    async def put(self, url, response) -> None:
        if any(
            x in url
            for x in (
                ".png",
                ".jpg",
                ".gif",
                ".svg",
                ".webp",
                ".ico",
                ".jpeg",
                ".js",
                ".css",
                ".woff2",
                ".ttf",
                ".otf",
            )
        ):
            url_hash = self.url_hash(url)
            response = {
                "status": response.status,
                "headers": response.headers,
                "body": await response.body(),
            }
            with open(f"./cache/{url_hash}", "wb") as f:
                pickle.dump(response, file=f)
            self.memory[url_hash] = response


cache = Cache()


async def route_cache(route: Route):
    if route.request.method == "GET" and all(
        x not in route.request.url
        for x in (
            "mc.yandex",
        )
    ):
        if cache.has(route.request.url):
            await route.fulfill(**cache.get(route.request.url))
        else:
            try:
                response = await route.fetch()
                await cache.put(route.request.url, response)
                if response:
                    await route.fulfill(response=response)
            except Error:
                pass
    else:
        await route.continue_()


def route_intercept(route: Route):
    if route.request.resource_type == "font" or route.request.resource_type == "media":
        return route.abort()
    return route.continue_()


project_class_map = {
    "tonique": Tonique,
}


class Clicker:
    loop: asyncio.AbstractEventLoop
    logger: logging.Logger
    debug: bool
    proxy: dict

    def __init__(
        self,
        user_id: int,
        account_id: str,
        proxy: dict = None,
        debug: bool = False,
        logger: logging.Logger = None,
    ) -> None:
        self.logger = logging.getLogger()
        coloredlogs.install(logger=self.logger, level=logging.INFO)
        self.loop = asyncio.get_event_loop()
        self.user_id = user_id
        self.account_id = account_id
        self.hash = int(hashlib.sha1(account_id.encode("utf-8")).hexdigest(), 16) % (
            10**12
        )
        self.proxy = proxy
        self.debug = debug

    async def send_stats(self, results: list):
        for project in results:
            data = {
                "hash": fnv_c.fnv1a_32(
                    str.encode(f"{self.account_id}:0:{project['project']}")
                ),
                "account_id": self.account_id,
                "user_id": int(self.user_id),
                "project": project["project"],
                "balance": float(project["balance"]),
                "storage": project["storage"] if "storage" in project else None,
                "sub_balance": float(project["sub_balance"]),
                "created_at": int(datetime.datetime.now().timestamp()),
            }
            self.logger.info(f'send_stats:{project["project"]}, {json.dumps(data)}')
            data["error"] = project["error"]
            try:
                httpx.post(
                    f"{S_PATH}/stats",
                    json=data,
                )
            except httpx.ReadTimeout:
                pass

    async def run(self, projects: list):
        self.logger.info(f"run: {self.account_id}")

        async with async_playwright() as playwright:
            self.logger.info("start browser")
            iphone_13 = playwright.devices["Pixel 7"]
            self.logger.info(f"proxy  = {self.proxy}")
            browser = await playwright.chromium.launch(
                # executable_path="./Chromium.app/Contents/MacOS/Chromium"
                # if self.debug
                # else "./chrome-win/chrome.exe",
                headless=not self.debug,
                args=[
                    "--mute-audio",
                    "--enable-gpu",
                    "--ignore-gpu-blocklist",
                    "--use-gl=angle",
                    "--use-angle=gl-egl",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-background-timer-throttling",
                ],
            )

            iphone_13["user_agent"] = str(
                useragent.list[self.hash % len(useragent.list)]
            )

            browser_context = await browser.new_context(
                **iphone_13,
                reduced_motion="reduce",
            )
            browser_context.set_default_timeout(60000)
            await browser_context.grant_permissions(
                ["clipboard-read", "clipboard-write"]
            )

            self.logger.info("projects")
            async with GatheringTaskGroup() as tg:
                for project in projects:
                    if "error" not in project or type(project["error"]) is bool:
                        project["error"] = ""
                    if (
                        "url" in project
                        and project["url"]
                        and project["project"] in project_class_map
                    ):
                        page = await browser_context.new_page()

                        await page.add_init_script("""
                    const defaultGetter = Object.getOwnPropertyDescriptor(
                            Navigator.prototype,
                            "webdriver"
                            ).get;
                            defaultGetter.apply(navigator);
                            defaultGetter.toString();
                            Object.defineProperty(Navigator.prototype, "webdriver", {
                            set: undefined,
                            enumerable: true,
                            configurable: true,
                            get: new Proxy(defaultGetter, {
                                apply: (target, thisArg, args) => {
                                Reflect.apply(target, thisArg, args);
                                return false;
                                },
                            }),
                            });
                            const patchedGetter = Object.getOwnPropertyDescriptor(
                            Navigator.prototype,
                            "webdriver"
                            ).get;
                            patchedGetter.apply(navigator);
                            patchedGetter.toString();
                        """)

                        # await stealth_async(page)
                        # await page.route("**/*", route_intercept)
                        await page.route("**/*", route_cache)

                        self.logger.info("run clickers")

                        clicker: Game = project_class_map[project["project"]](
                            page=page,
                            user_id=self.account_id,
                            owner_id=int(self.user_id),
                            url=project["url"],
                            storage=project["storage"]
                            if "storage" in project
                            else None,
                            debug=self.debug,
                        )
                        tg.create_task(clicker.run())
                        await asyncio.sleep(60)
            self.logger.info(f"results = {tg.results()}")
            await browser_context.close()
            await browser.close()
            await self.send_stats(tg.results())
