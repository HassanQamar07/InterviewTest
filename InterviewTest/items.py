# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import itemloaders
import scrapy


class SteamCommunityItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    game_name = scrapy.Field()
    description = scrapy.Field()
    type = scrapy.Field()
    url = scrapy.Field()
    buy_price = scrapy.Field()
    sell_price = scrapy.Field()
    historical_price = scrapy.Field()
    buy_orders = scrapy.Field()
    sell_orders = scrapy.Field()
    buy_offers_count = scrapy.Field()
    sell_offers_count = scrapy.Field()
    image = scrapy.Field()


class SteamCommunityItemLoader(itemloaders.ItemLoader):
    default_item_class = SteamCommunityItem

    default_input_processor = itemloaders.processors.MapCompose(str.strip)
    default_output_processor = itemloaders.processors.TakeFirst()

    buy_orders_in = itemloaders.processors.Identity()
    buy_orders_out = itemloaders.processors.Identity()

    sell_orders_in = itemloaders.processors.Identity()
    sell_orders_out = itemloaders.processors.Identity()

    historical_price_in = itemloaders.processors.Identity()
    historical_price_out = itemloaders.processors.Identity()

    description_out = itemloaders.processors.Join("\n")
