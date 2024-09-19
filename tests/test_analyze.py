import pytest
import os
import json
import tempfile
from src.log_analyzer import (
    find_last_log,
    parse_log_line,
    analyze_log,
    generate_report,
    load_config,
    default_config
)


@pytest.fixture
def temp_log_file():
    # Создание временного файла лога
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(
            b'1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/16852664 HTTP/1.1" 200 19415 "-" "Slotovod" "-" "1498697422-2118016444-4708-9752769" "712e90144abee9" 0.199\n')
        temp_file.flush()
        yield temp_file.name
        os.remove(temp_file.name)


def test_find_last_log(temp_log_file):
    log_dir = tempfile.mkdtemp()
    os.rename(temp_log_file, os.path.join(log_dir, 'test.log'))
    assert find_last_log(log_dir) == os.path.join(log_dir, 'test.log')
    os.rmdir(log_dir)


def test_parse_log_line():
    line = '1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/16852664 HTTP/1.1" 200 19415 "-" "Slotovod" "-" "1498697422-2118016444-4708-9752769" "712e90144abee9" 0.199'
    result = parse_log_line(line)
    assert result is not None
    assert result['url'] == '/api/v2/banner/16852664'
    assert result['response_time'] == '0.199'


def test_analyze_log(temp_log_file):
    log_data = analyze_log(temp_log_file, 10)
    assert log_data['total_requests'] == 1
    assert log_data['total_time'] == 0.199
    assert len(log_data['urls']) == 1


def test_generate_report(temp_log_file):
    report_data = analyze_log(temp_log_file, 10)
    template = '<html><body><pre>{{ table_json }}</pre></body></html>'
    with tempfile.NamedTemporaryFile(delete=False) as template_file, tempfile.NamedTemporaryFile(
            delete=False) as report_file:
        template_file.write(template.encode())
        template_file.flush()
        generate_report(report_data, report_file.name, template_file.name)
        with open(report_file.name) as f:
            content = f.read()
            assert '{"total_requests": 1, "total_time": 0.199, "urls": [["/api/v2/banner/16852664", {"count": 1, "time_sum": 0.199}]]}' in content
        os.remove(template_file.name)
        os.remove(report_file.name)


def test_load_config():
    config_path = tempfile.NamedTemporaryFile(delete=False)
    config_data = {
        "LOG_DIR": "./custom_logs",
        "REPORT_SIZE": 500
    }
    with open(config_path.name, 'w') as f:
        json.dump(config_data, f)
    config = load_config(config_path.name)
    assert config['LOG_DIR'] == './custom_logs'
    assert config['REPORT_SIZE'] == 500
    assert config['REPORT_TEMPLATE'] == default_config['REPORT_TEMPLATE']
    os.remove(config_path.name)


def test_load_default_config():
    config = load_config(None)
    assert config == default_config
