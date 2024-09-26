from typing import Tuple
from playwright.async_api import (
    Route,
    TimeoutError,
)
import asyncio
import time
import random
from .game import Game
from .game_utils import gamma25


class Tapswap(Game):
    @property
    def name(self) -> str:
        return "tapswap"

    async def _run(self) -> Tuple[float, float]:
        async def handle_ref(route: Route):
            self.logger.info("handle_ref")
            response = await route.fetch()
            data = await response.json()
            ref = data["player"]['id']
            self.provide_ref_url(f"https://t.me/tapswap_mirror_bot?start=r_{ref}")
            await route.fulfill(response=response)

        await self.page.route("**/api/player/submit_taps", handle_ref)
        await self.goto(self.url, timeout=60000)
        start = time.time()
        boosters_awailable = True

        main_button = self.page.locator('css=[class*="tapContent"]')
        await main_button.wait_for()
        await asyncio.sleep(5)
        for drawer in reversed(await self.page.locator('css=[class*="drowerContainer"]').all()):
            welcome_text = drawer.locator("h2")
            if await welcome_text.is_visible():
                if "Tap Bot" not in await welcome_text.text_content():
                    droewr_header = drawer.locator('css=[class*="droewrHeader"]')
                    if await droewr_header.is_visible():
                        await droewr_header.locator('css=[class*="imageContainer"]').tap()
                else:
                    welcome_bonus = drawer.locator("button", has_text="Get it!")
                    if await welcome_bonus.is_visible():
                        await welcome_bonus.tap()
            await asyncio.sleep(2)

        # Game loop
        while True:
            balance_info = self.page.locator('css=[class*="balanceInfo"]')
            self.balance = float(
                (await balance_info.locator("h1").text_content()).replace(" ", "")
            )

            bottom_content = self.page.locator('css=[class*="bottomContent"]')
            current_energy = float(
                (await bottom_content.locator("h4").text_content())
                .replace(" ", "")
                .replace("/", "")
            )
            total_energy = float(
                (await bottom_content.locator("h6").text_content())
                .replace(" ", "")
                .replace("/", "")
            )
            # self.logger.info(f"[tapswap]:{current_energy}/{total_energy}|{balance}")

            if time.time() - start > 10:
                await asyncio.sleep(random.random() * 10 / 2.0)
                start = time.time()

            await asyncio.sleep(random.choice(gamma25) * 0.1)

            main_button = self.page.locator('css=[class*="tapContent"]')
            if await main_button.is_visible():
                await main_button.tap()

            if current_energy < 50:
                if boosters_awailable:
                    self.logger.info("[tapswap]:boosters check")
                    await self.page.locator("button", has_text="Boost").tap()

                    full_tank = self.page.locator("button", has_text="Full Tank")
                    if await full_tank.is_visible() and not await full_tank.is_disabled():
                        self.logger.info("[tapswap]:boosters:full_tank")
                        await full_tank.tap()
                        await self.page.locator("button", has_text="Get it!").tap()

                        await self.page.locator("button", has_text="Boost").tap()
                        taping_guru = self.page.locator(
                            "button", has_text="Taping Guru"
                        )
                        if not await taping_guru.is_disabled():
                            self.logger.info("[tapswap]:boosters:taping_guru")
                            await taping_guru.tap()
                            await self.page.locator("button", has_text="Get it!").tap()
                        else:
                            await self.page.locator("button", has_text="Tap").tap()

                        continue
                    else:
                        await self.page.get_by_role(
                            "button", name="navigation button Tap"
                        ).tap()
                        boosters_awailable = False
                break
        # Shop loop
        await self.page.locator("button", has_text="Boost").click()
        await asyncio.sleep(5 + random.random() * 5)
        while True:
            self.logger.info("[tapswap]:shop_loop")
            self.balance = float(
                (
                    await self.page.locator(
                        'css=[class*="balanceBoxContainer"]',
                        has_text="Your Share balance",
                    )
                    .locator("h1")
                    .text_content()
                ).replace(" ", "")
            )

            items = await self.page.locator('css=[class*="listItem"]').all()
            item_purchased = False
            for item in reversed(items):
                name = await item.locator('css=[class*="name"]').text_content()
                price_text = await item.locator('css=[class*="balance"]').text_content()
                if "TON" not in price_text:
                    price = int(price_text.replace(" ", ""))
                    self.logger.info(
                        f"[tapswap]:shop_loop:{name}-{price}|{self.balance}"
                    )
                    if price < self.balance and price < 250000 and name=='Tap Bot' and await item.is_enabled():
                        self.logger.info(f"[tapswap]:shop_loop:buy {name}")
                        await asyncio.sleep(2 + random.random())
                        await item.tap()
                        await asyncio.sleep(2 + random.random())
                        await self.page.locator("button", has_text="Get it!").tap()
                        await asyncio.sleep(5 + random.random() * 5)
                        item_purchased = True
                        break
            if item_purchased:
                continue
            break
        # Bonus loop
        await self.page.locator("button", has_text="Task").tap()

        await self.page.locator("button", has_text="Leagues").tap()
        for item in await self.page.locator('css=[class*="listItem"]').all():
            button = item.locator("button", has_text="Claim")
            if await button.is_visible() and not await button.is_disabled():
                name = await item.locator('css=[class*="name"]').text_content()
                self.logger.info(f"[tapswap]:bonus_loop:got bonus {name}")
                await button.tap()
                await asyncio.sleep(2 + random.random())

        await self.page.get_by_role("button", name="Ref", exact=True).tap()
        for item in await self.page.locator('css=[class*="listItemBody"]').all():
            button = item.locator("button", has_text="Claim")
            if await button.is_visible() and not await button.is_disabled():
                name = await item.locator('css=[class*="name"]').text_content()
                self.logger.info(f"[tapswap]:bonus_loop:got bonus {name}")
                await button.tap()
                await asyncio.sleep(2 + random.random())
        # https://t.me/tapswapai
        await self.page.locator("button", has_text="Special").tap()
        await self.page.locator("h5", has_text="Join our socials").tap()

        await self.page.locator("h3", has_text="Join our socials").wait_for()
        await asyncio.sleep(1)

        start = self.page.locator("button", has_text="Start mission")
        if await start.is_visible():
            await start.tap()
        await asyncio.sleep(5)

        # async with self.page.expect_popup(timeout=0) as popup_info:
        for stage in ["Go", "Check"]:
            for item in await self.page.locator('css=[class*="_item_"]').all():
                self.logger.info(f"stage={stage}")
                button = item.locator("button", has_text=stage)
                if await button.is_visible():
                    await button.tap()
                    # if stage == "Go":
                    #     popup = await popup_info.value
                    #     await popup.close()
                await asyncio.sleep(5)
            

        self.logger.info("[tapswap]:finish?")
        finish = self.page.locator("button", has_text="Finish mission")
        if await finish.is_visible() and await finish.is_enabled():
            await finish.tap()
        await asyncio.sleep(5)

        self.logger.info("[tapswap]:claim?")
        claim = self.page.locator("button", has_text="Claim")
        if await claim.is_visible() and await claim.is_enabled():
            await claim.tap()

        self.logger.info("[tapswap]:done")
