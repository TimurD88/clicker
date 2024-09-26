from typing import Tuple
from playwright.async_api import (
    Route,
    TimeoutError,
)
import asyncio
import time
import random
from .game import Game
from .game_utils import gamma25, touch_emulator_script, walnut_script


class Testcoin(Game):
    @property
    def name(self) -> str:
        return "testcoin"

    async def shop_loop(self):
        pass

    async def bonus_loop(self):
        pass

    async def _run(self) -> Tuple[float, float]:        
        await self.goto(self.url, timeout=60000)            
        self.logger.info(f"going to - {self.url}")
        #await self.bonus_loop()
        #await self.shop_loop()
        await asyncio.sleep(1)
        
        #ticket counting
        ticket_element = self.page.locator('css=div[class*="badge_badge"][class*="badge_large"]')
        ticket_count = await ticket_element.text_content()
        ticket_count = int(ticket_count.strip())
        self.logger.info(f"[{self.name}]Ticket coint {ticket_count}")
        # all_buttons = self.page.locator('css=button[class*="button_button"]')
        # target_button = all_buttons.filter(has_text="Play")
        # await target_button.wait_for()
        # await asyncio.sleep(5)
        # if await target_button.is_visible():
        #     await target_button.tap()
        #     await asyncio.sleep(2)
        #     await self.page.tap('body')
        #     await asyncio.sleep(50)
        self.logger.info("done")
