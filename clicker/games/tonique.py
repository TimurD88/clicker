import copy
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


class Tonique(Game):
    @property
    def name(self) -> str:
        return "tonique"

    async def wait_for_app_ready(self):
        await self.page.wait_for_selector('css=main._main')
        self.logger.info("Game appeared")

    async def handle_ref(self, route: Route):
        self.logger.info("Handle_ref")
        response = await route.fetch()
        data = await response.json()
        url = data[0]['result']['data']['json']['result']
        self.provide_ref_url(url)
        await route.fulfill(response=response)

    async def handle_tonique_game(self, route: Route):
        self.logger.info(f"[{self.name}]handle_game")
        data = copy.deepcopy(route.request.post_data_json)
        data["points"] = random.randint(50, 100)
        self.logger.info(data)
        await asyncio.sleep(0.5 + random.choice(gamma25) * 10)
        response = await route.fetch(post_data=data)
        await route.fulfill(response=response)

    async def check_in(self):
        check_in_button = self.page.locator('css=button[class*="button_button"]:has-text("Check in")')
        if await check_in_button.is_visible():
            await check_in_button.tap()
            await asyncio.sleep(2)

    async def start_farming(self):
        self.logger.info(f"Stage: Farming")
        await asyncio.sleep(1)
        earn_button = self.page.locator('css=button[class*=button_button_yellow]:has-text("Start farming")')
        if await earn_button.is_visible():
            await earn_button.tap()
            await asyncio.sleep(1)
            claim_button = self.page.locator('css=button[class*=button_button_yellow]:has-text("Claim")')
            if await claim_button.is_visible():
                await claim_button.tap()
                await asyncio.sleep(1)
                await self.page.locator('css=button[class*=button_button_yellow]:has-text("Start farming")').tap()

    async def get_ref_url(self):
        self.logger.info("Stage: Getting refUrl")
        await asyncio.sleep(1)
        friends_element = self.page.locator('css=a[class*="navigationLink"]:has-text("Friends")')
        await friends_element.is_visible()
        await friends_element.tap()
        await asyncio.sleep(1)
        invite_button = self.page.locator('css=button[class*="button_button_yellow"]:has-text("Invite a Friend")')
        await invite_button.wait_for()
        await invite_button.tap()
        await asyncio.sleep(1)
        close_button = self.page.locator('css=button[class*="button_button"]:has-text("Close")')
        await close_button.wait_for()
        await close_button.tap()
        await asyncio.sleep(1)
        home_element = self.page.locator('css=a[class*="navigationLink"]:has-text("Home")')
        await home_element.tap()

    async def do_tasks(self):
        self.logger.info("Stage: Tasks")
        await asyncio.sleep(1)
        tasks = await self.page.locator('div[class*="badge_badge_light"]').text_content()
        tasks_num = int(tasks.strip())
        self.logger.info(f"[{self.name}]Tasks available: {tasks_num}")
        if tasks_num > 0:
            self.logger.info("Doing tasks")
            tasks_element = self.page.locator('css=a[class*="navigationLink"]:has-text("Tasks")')
            await tasks_element.wait_for()
            await tasks_element.tap()
            await self.page.wait_for_selector('css=div[class*="availableList_availableList__list"]')
            await asyncio.sleep(4)
            for button in reversed(await self.page.locator('button:has(span:text("Start"))').all()):
                await button.tap()
                await asyncio.sleep(0.5 + random.choice(gamma25) * 10)
            await asyncio.sleep(2)
            for button in reversed(await self.page.locator('button:has(span:text("Claim")):not([disabled])').all()):
                await button.tap()
                await asyncio.sleep(0.5 + random.choice(gamma25) * 10)
            await asyncio.sleep(1)
            home_element = self.page.locator('css=a[class*="navigationLink"]:has-text("Home")')
            await home_element.tap()

    async def count_tickets(self):
        self.logger.info("Stage: Counting tickets")
        ticket_element = self.page.locator('css=div[class*="badge_badge_dark"]')
        ticket_count = await ticket_element.text_content()
        ticket_count = int(ticket_count.strip())
        self.logger.info(f"Ticket count {ticket_count}")
        return ticket_count

    async def play_main_game(self, ticket_count):
        self.logger.info(f"[{self.name}]Stage: Main_game")
        await asyncio.sleep(1)
        while ticket_count > 0:
            self.logger.info(f"[{self.name}]Main_game start")
            main_button = self.page.locator('css=button[class*="button_button"]:has-text("Play")')
            await main_button.tap()
            await self.page.wait_for_selector('css=div[class*="pageCard_pageCard"]:has-text("Tap on a screen to jump")')
            await self.page.tap('body')
            home_button = self.page.locator('css=button[class*="button_button"]:has-text("Go to home page")')
            await home_button.wait_for()
            await home_button.tap()

    async def handle_insufficient_tickets(self):
        not_enough_text = self.page.locator('css=div[class*="dontHaveTickets_dontHaveTickets__main"]')
        if await not_enough_text.is_visible():
            await self.page.locator('css=button[class*="button_button_grey__"]:has-text("Close")').tap()
            await asyncio.sleep(1)

    async def check_balance(self):
        self.logger.info(f"[{self.name}]Stage: Balance checking")
        balance_element = await self.page.locator('css=div[class*="pageCard_pageCard__description"]').text_content()
        balance = int(balance_element.replace(",", "").strip())
        self.balance = balance
        self.logger.info("done")

    async def _run(self) -> Tuple[float, float]:
        await self.goto(self.url, timeout=60000)
        self.logger.info(f"Starting")

        await self.wait_for_app_ready()
        await self.check_in()
        await self.start_farming()

        await self.page.route("**/api/trpc/referralProgram.getUrl*", self.handle_ref)
        await self.get_ref_url()

        await self.page.route("**/api/trpc/balance.gameReward*", self.handle_tonique_game)

        await self.do_tasks()
        ticket_count = await self.count_tickets()
        await self.play_main_game(ticket_count)

        await self.handle_insufficient_tickets()
        await self.check_balance()
