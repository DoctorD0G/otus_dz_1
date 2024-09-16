# nginx-log-analyzer

Сервис для парсинга логов Nginx и формирования статистических отчетов.

## Установка

1. Убедитесь, что у вас установлен [Poetry](https://python-poetry.org/) и [Docker](https://www.docker.com/).


2. Установите зависимости с помощью Poetry:

    ```bash
    poetry install
    ```

## Запуск

### С помощью Poetry

Для запуска проекта используйте следующую команду:

```bash
poetry run analyze-logs ./access.log
