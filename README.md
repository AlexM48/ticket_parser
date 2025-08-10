# Ticket Parser

Проект на **Scrapy** для парсинга схем залов и доступных мест с сайтов:

- [ticketland.ru](https://www.ticketland.ru)
- [mdt-dodin.ru](https://mdt-dodin.ru)

## Установка

```bash
git clone https://github.com/AlexM48/ticket_parser.git
cd ticket_parser
pip install -r requirements.txt
```

## Запуск

### Ticketland Spider
```bash
scrapy crawl ticketland -a event_url="https://www.ticketland.ru/hallview/map/123456?json=1"
```

или, если передаётся HTML-страница мероприятия:
```bash
scrapy crawl ticketland -a event_url="https://www.ticketland.ru/some_event_page"
```

### MDT Spider
```bash
scrapy crawl mdt -a event_url="https://mdt-dodin.ru/event/12345"
```

или прямая ссылка на JSON:
```bash
scrapy crawl mdt -a event_url="https://mdtdodin.core.ubsystem.ru/uiapi/event/scheme?id=12345"
```

## Результаты

После завершения работы спайдера результат сохраняется в JSON-файл:

```
<event_id>_<count>.json
```

где:
- `event_id` — ID мероприятия
- `count` — количество собранных мест

Пример:
```
123456_120.json
```

