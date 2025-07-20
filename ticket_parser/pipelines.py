# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json

class TicketlandPipeline:
    def open_spider(self, spider):
        self.items = []


    def close_spider(self, spider):
        event_id = getattr(spider, "event_id", "unknown")
        count = len(self.items)
        filename = f"{event_id}_{count}.json"
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=4)

    def process_item(self, item, spider):
        try:
            item["sector"] = str(item.get("sector", "")).strip()
            item["row"] = int(item.get("row") or 1)
            item["seat"] = int(item.get("seat"))
            item["price"] = int(float(item.get("price")))
            item["count"] = int(item.get("count", 1))
        except (ValueError, TypeError) as e:
            spider.logger.error(f"Ошибка данных: {e}")
            return None

        self.items.append(dict(item))
        return item

