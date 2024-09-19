import json
import re
from typing import Iterable

import scrapy
from scrapy import Request

from InterviewTest.items import SteamCommunityItem, SteamCommunityItemLoader
from InterviewTest.settings import RETRY_TIMES


class SteamcommunitySpider(scrapy.Spider):
    name = "steamcommunity"
    allowed_domains = ["steamcommunity.com"]

    app_data_regex = re.compile(r"var g_rgAssets\s*=\s*(.*);", flags=re.MULTILINE)

    RESULTS_PER_PAGE = 10

    def start_requests(self) -> Iterable[Request]:
        if getattr(self, "game_url", None):
            yield Request(self.game_url, callback=self.parse_game)
        else:
            yield self.get_search_request(1)

    def get_search_request(self, page=1):
        URL = "https://steamcommunity.com/market/search/render/"
        start = (page - 1) * self.RESULTS_PER_PAGE
        return scrapy.FormRequest(
            URL,
            method="GET",
            formdata={
                "query": "",
                "start": str(start),
                "count": str(self.RESULTS_PER_PAGE),
                "search_descriptions": "",
                "sort_column": "popular",
                "sort_dir": "desc",
            },
            callback=self.parse_search,
            cb_kwargs={"page": page},
        )

    def parse_search(self, response, page: int):
        data = json.loads(response.text)
        html = data["results_html"]
        html_selector = scrapy.Selector(text=html)
        for item in html_selector.xpath(
            './/a[@class="market_listing_row_link"]/@href'
        ).extract():
            yield scrapy.Request(item, callback=self.parse_game)

        if page < 50:
            yield self.get_search_request(page + 1)

    def parse_game(self, response) -> Request:
        if (
            "There was an error getting listings for this item. Please try again later."
            in response.text
        ):
            retry_time = response.meta.get("retry_time", 0)
            if retry_time > RETRY_TIMES:
                self.logger.error(f"Max retry reached for {response.url}")
                return
            return scrapy.Request(
                response.url,
                meta={"dont_cache": True, "retry_time": retry_time + 1},
                dont_filter=True,
                callback=self.parse_game,
            )
        item_loader = SteamCommunityItemLoader(selector=response)

        # all the related data about the item is in javascript tag.
        javascript_data = response.xpath(
            './/script[contains(.,"var g_rgAssets")]//text()'
        )

        # these 3 ids are used to reach the app data from the javascript object.
        rgAppItemsId = javascript_data.re_first(r"rgAppItems = g_rgAssets\[(\d+)\]")
        rgContextItemsId = javascript_data.re_first(
            r"rgContextItems = rgAppItems\[\'(\w+)\'\]"
        )
        rgItemId = javascript_data.re_first(r"rgItem = rgContextItems\[\'(\w+)\'\]")
        # the data is in dict type object within a dict within a dict within a dict
        app_info_data = json.loads(javascript_data.re_first(self.app_data_regex))[
            rgAppItemsId
        ][rgContextItemsId][rgItemId]

        item_loader.add_value("url", response.url)
        item_loader.add_value("name", app_info_data["name"])
        item_loader.add_value("type", app_info_data["type"])
        item_loader.add_value(
            "description", [d["value"] for d in app_info_data["descriptions"]]
        )

        item_loader.add_xpath(
            "image", ".//div[@class='market_listing_largeimage']/img/@src"
        )

        item_loader.add_xpath(
            "game_name", './/span[@class="market_listing_game_name"]/text()'
        )

        # the historical price data is in a list of lists in format [date and time, price, count]

        historical_price_data = json.loads(javascript_data.re_first(r"var line1=(.*);"))

        for line in historical_price_data:
            historical_price = {
                "data": line[0],
                "price": line[1],
                "quantity_sold": line[2],
            }
            item_loader.add_value("historical_price", historical_price)

        item_name_id = javascript_data.re_first(r"Market_LoadOrderSpread\(\s*(\d+)")

        # request the current sell and buy orders for the item
        return scrapy.Request(
            f"https://steamcommunity.com/market/itemordershistogram?country=PK&language=english&currency=1&item_nameid={item_name_id}",
            callback=self.parse_orders,
            cb_kwargs={"item": item_loader.load_item()},
        )

    def parse_orders(self, response, item: SteamCommunityItem):
        # the data is in JSON format contain HTML objects, we need to construct a selector for it
        json_data = json.loads(response.text)
        html = "\n".join(x for x in json_data.values() if isinstance(x, str))
        html_selector = scrapy.Selector(text=html)

        item_loader = SteamCommunityItemLoader(item, html_selector)

        item_loader.add_xpath(
            "buy_price", ".//table[2]/following-sibling::span[2]/text()"
        )
        item_loader.add_xpath(
            "buy_offers_count", ".//table[2]/following-sibling::span[1]/text()"
        )
        # the sell orders from the first table
        for row in html_selector.xpath(".//table[1]//tr[td]"):
            offer = {
                "price": row.xpath(".//td[1]/text()").get(),
                "quantity": row.xpath(".//td[2]/text()").get(),
            }
            item_loader.add_value("sell_orders", offer)

        # the buy orders from second table
        for row in html_selector.xpath(".//table[2]//tr[td]"):
            offer = {
                "price": row.xpath(".//td[1]/text()").get(),
                "quantity": row.xpath(".//td[2]/text()").get(),
            }
            item_loader.add_value("buy_orders", offer)

        item_loader.add_xpath(
            "sell_price", ".//table[1]/following-sibling::span[2]/text()"
        )
        item_loader.add_xpath(
            "sell_offers_count", ".//table[1]/following-sibling::span[1]/text()"
        )

        return item_loader.load_item()
