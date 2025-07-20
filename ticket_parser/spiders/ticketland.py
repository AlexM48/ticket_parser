import scrapy
import json
import re
from ticket_parser.items import TicketlandItem


class TicketlandSpider(scrapy.Spider):
    name = "ticketland"
    allowed_domains = ["ticketland.ru"]

    def __init__(self, event_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_url = event_url

    def start_requests(self):
        if not self.event_url:
            self.logger.error("Не передан event_url")
            return

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/125.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",  # что хоти получить json, а не html
            "Accept-Language": "ru,en;q=0.9",  # предпочтения языка q=0.9 приоритет
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.ticketland.ru/"  # имитируем переход с данного сайта
        }

        # Если сразу ссылка на JSON с картой
        if "/hallview/map/" in self.event_url and "json=1" in self.event_url:
            self.logger.info("Прямая ссылка на JSON")
            match = re.search(r'/hallview/map/(\d+)(?:/|$)', self.event_url)
            if match:
                self.event_id = match.group(1)
            else:
                self.event_id = "unknown"
            yield scrapy.Request(url=self.event_url, callback=self.parse, headers=headers, dont_filter=True)
        else:
            self.logger.info("HTML-страница мероприятия")
            yield scrapy.Request(url=self.event_url, callback=self.parse_event_page, headers=headers, dont_filter=True)

    def parse_event_page(self, response):
        # Ищем mapDataUrl в JS на странице
        map_match = re.search(r"mapDataUrl:\s*['\"]([^'\"]+)['\"]", response.text)
        # Получаем csrf-token из meta
        csrf_token = response.css('meta[name="csrf-token"]::attr(content)').get()

        if not map_match:
            self.logger.error("Не найден mapDataUrl")
            return
        if not csrf_token:
            self.logger.error("Не найден CSRF токен")
            return

        map_url_path = map_match.group(1)
        event_id_match = re.search(r'/(\d+)/$', map_url_path)

        if event_id_match:
            self.event_id = event_id_match.group(1)
        else:
            self.event_id = "unknown"


        map_url = f"https://www.ticketland.ru{map_url_path}?json=1&all=1&isSpecialSale=0&tl-csrf={csrf_token}"

        self.logger.info(f"Запрашиваю JSON карту по адресу: {map_url}")
        yield scrapy.Request(url=map_url, callback=self.parse, headers=response.request.headers, dont_filter=True)

    def parse(self, response):
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as e:
            self.logger.error(f"Ошибка парсинга JSON: {e}")
            return

        for seat in data.get("places", []):
            item = TicketlandItem()
            item["sector"] = seat.get("section", {}).get("name")
            item["row"] = seat.get("row")
            item["seat"] = seat.get("place")
            item["price"] = seat.get("price")
            item["count"] = 1
            yield item

