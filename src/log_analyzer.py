import os
import re
import json
import logging
import argparse
import structlog
from datetime import datetime
from jinja2 import Template


default_config = {
    "LOG_DIR": "./logs",
    "REPORT_DIR": "./reports",
    "REPORT_SIZE": 1000,
    "LOG_FILE": 'nginx-access-ui.log-20170630',
    "REPORT_TEMPLATE": "./report.html"
}

LOG_PATTERN = re.compile(r'(?:GET|POST|PUT|PATCH|DELETE) (.*?) HTTP/\d\.\d.+ (\d+\.\d+)')

def configure_logging(log_file=None):
    if log_file:
        logging.basicConfig(filename=log_file, level=logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO)
    )


def find_last_log(log_dir):
    log_files = [f for f in os.listdir(log_dir)]
    if not log_files:
        return None

    log_files.sort(reverse=True)
    return os.path.join(log_dir, log_files[0])


def parse_log_line(line):
    match = LOG_PATTERN.match(line)
    if match:
        return match.groupdict()
    return None


def analyze_log(log_file, report_size):
    urls_data = {}
    total_requests = 0
    total_time = 0.0

    with open(log_file, 'r') as f:
        for line in f:
            log_entry = parse_log_line(line)
            if log_entry:
                url = log_entry['url']
                response_time = float(log_entry['response_time'])
                total_requests += 1
                total_time += response_time

                # Инициализация данных для URL, если его еще нет
                if url not in urls_data:
                    urls_data[url] = {'count': 0, 'time_sum': 0.0}

                # Увеличиваем счетчики для URL
                urls_data[url]['count'] += 1
                urls_data[url]['time_sum'] += response_time

    # Сортировка URL по времени выполнения (time_sum) и ограничение по report_size
    sorted_urls = sorted(urls_data.items(), key=lambda x: x[1]['time_sum'], reverse=True)[:report_size]

    # Формирование отчета
    report = {
        "total_requests": total_requests,
        "total_time": total_time,
        "urls": sorted_urls
    }

    return report


def generate_report(data, report_file, template_file):
    with open(template_file) as template_f:
        template = Template(template_f.read())

    table_json = json.dumps(data)
    report_content = template.render(table_json=table_json)

    with open(report_file, 'w') as report_f:
        report_f.write(report_content)


def load_config(config_path):
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as config_f:
            config_data = json.load(config_f)
            return {**default_config, **config_data}
    return default_config


def main():
    parser = argparse.ArgumentParser(description="Log analyzer")
    parser.add_argument('--config', default='./config.json', help="Path to config file")
    args = parser.parse_args()

    config = load_config(args.config)
    configure_logging(config.get("LOG_FILE"))
    structlog.get_logger().info("Starting log analysis")

    log_file = find_last_log(config['LOG_DIR'])
    if not log_file:
        structlog.get_logger().info("No logs to process")
        return

    structlog.get_logger().info(f"Analyzing log: {log_file}")
    report_data = analyze_log(log_file, config["REPORT_SIZE"])

    report_name = f"report-{datetime.now().strftime('%Y.%m.%d')}.html"
    report_path = os.path.join(config['REPORT_DIR'], report_name)
    generate_report(report_data, report_path, config['REPORT_TEMPLATE'])

    structlog.get_logger().info(f"Report generated: {report_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        structlog.get_logger().exception("Unexpected error occurred", exc_info=True)
