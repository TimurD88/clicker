import asyncio
import json
import os
from clicker.clicker import Clicker


def run_clicker(
    user_id: int, account_id: str = "", airdrops: list = [], debug: bool = False
):
    clicker = Clicker(
        user_id=user_id,
        account_id=account_id,
        debug=debug,
    )

    print("start")
    asyncio.run(clicker.run(projects=airdrops))
    print("done")


if __name__ == "__main__":
    user_id = int(os.environ.get("user_id", 0))
    account_id = os.environ.get("account_id", "83cd7630-2331-4af2-aa27-e89c3841650a")
    airdrops = json.loads(os.environ.get("airdrops", "[]"))
    debug = True
    airdrops = [
        {
            #"url": "https://app.tapswap.club/?bot=app_bot_1#tgWebAppData=query_id%3DAAG-miovAwAAAL6aKi-DFc5p%26user%3D%257B%2522id%2522%253A7233772222%252C%2522first_name%2522%253A%2522%25D0%25A0%25D0%25BE%25D0%25BC%25D0%25B0%25D0%25BD%2522%252C%2522last_name%2522%253A%2522%2522%252C%2522language_code%2522%253A%2522en%2522%252C%2522allows_write_to_pm%2522%253Atrue%257D%26auth_date%3D1722607541%26hash%3De5a4af9b7f9da402804550c564fc6a40ad440b8f240a73b7122b443735e1c78d&tgWebAppVersion=7.6&tgWebAppPlatform=android&tgWebAppThemeParams=%7B%22bg_color%22%3A%22%23ffffff%22%2C%22section_bg_color%22%3A%22%23ffffff%22%2C%22secondary_bg_color%22%3A%22%23f0f0f0%22%2C%22text_color%22%3A%22%23222222%22%2C%22hint_color%22%3A%22%23a8a8a8%22%2C%22link_color%22%3A%22%232678b6%22%2C%22button_color%22%3A%22%2350a8eb%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22header_bg_color%22%3A%22%23527da3%22%2C%22accent_text_color%22%3A%22%231c93e3%22%2C%22section_header_text_color%22%3A%22%233a95d5%22%2C%22subtitle_text_color%22%3A%22%2382868a%22%2C%22destructive_text_color%22%3A%22%23cc2929%22%2C%22section_separator_color%22%3A%22%23d9d9d9%22%7D",
            "url": "https://game.tonique.app/signup?event=bot_hello_Open#tgWebAppData=query_id%3DAAH9PKplAgAAAP08qmUvhNKm%26user%3D%257B%2522id%2522%253A6000622845%252C%2522first_name%2522%253A%2522%25D0%2592%25D0%25B8%25D0%25BA%25D0%25B0%2522%252C%2522last_name%2522%253A%2522%2522%252C%2522username%2522%253A%2522infreach_ai%2522%252C%2522language_code%2522%253A%2522en%2522%252C%2522allows_write_to_pm%2522%253Atrue%257D%26auth_date%3D1722853537%26hash%3D3fcc2de47e3e444aa589aacafbd589437557b1e945eb12893c13a00f34c6bffa&tgWebAppVersion=7.6&tgWebAppPlatform=weba&tgWebAppThemeParams=%7B%22bg_color%22%3A%22%23ffffff%22%2C%22text_color%22%3A%22%23000000%22%2C%22hint_color%22%3A%22%23707579%22%2C%22link_color%22%3A%22%233390ec%22%2C%22button_color%22%3A%22%233390ec%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22secondary_bg_color%22%3A%22%23f4f4f5%22%2C%22header_bg_color%22%3A%22%23ffffff%22%2C%22accent_text_color%22%3A%22%233390ec%22%2C%22section_bg_color%22%3A%22%23ffffff%22%2C%22section_header_text_color%22%3A%22%23707579%22%2C%22subtitle_text_color%22%3A%22%23707579%22%2C%22destructive_text_color%22%3A%22%23e53935%22%7D",
            "active": True,
            "project": "tonique",
            #"ref_url": "https://t.me/tapswap_mirror_bot?start=r_7233772222",
            "ref_url": "https://t.me/tonique_bot?start=clz70m55e000sx8sm6pv74zpv",
            #"join_url": "e4ee5d29-5602-48e6-a39a-28bff037e6f7",
            "updated_at": "2024-08-02T14:04:22.652033+00:00",
        }
    ]

    run_clicker(user_id, account_id, airdrops, debug)
    exit(0)
   