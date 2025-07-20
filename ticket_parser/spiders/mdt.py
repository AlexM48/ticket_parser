import scrapy
import json
import re
from ticket_parser.items import TicketlandItem


class MdtSpider(scrapy.Spider):
    name = "mdt"
    allowed_domains = ["mdt-dodin.ru", "mdtdodin.core.ubsystem.ru"]

    def __init__(self, event_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_url = event_url

    def start_requests(self):
        if not self.event_url:
            self.logger.error("Нет event_url")
            return

        if "uiapi/event/scheme?id=" in self.event_url:
            match = re.search(r'id=(\d+)', self.event_url)
            if match:
                self.event_id = match.group(1)
            yield scrapy.Request(url=self.event_url, callback=self.parse, dont_filter=True)
        else:
            yield scrapy.Request(url=self.event_url, callback=self.parse_event_page, dont_filter=True)

    def parse_event_page(self, response):
        match = re.search(r'/event/(\d+)', self.event_url)
        if match:
            self.event_id = match.group(1)
            api_url = f"https://mdtdodin.core.ubsystem.ru/uiapi/event/scheme?id={self.event_id}"
            yield scrapy.Request(url=api_url, callback=self.parse, dont_filter=True)
        else:
            self.logger.error("ID не найден")

    def parse(self, response):
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON Error: {e}")
            return

        for seat in data.get("seats", []):
            if seat.get("unavailable") == 1:
                continue
            item = TicketlandItem()
            item["sector"] = seat.get("areaTitle", "")
            item["row"] = seat.get("row")
            item["seat"] = seat.get("seat")
            item["price"] = seat.get("price")
            item["count"] = 1
            yield item
