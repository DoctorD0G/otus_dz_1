import unittest
from src.log_analyzer import parse_logs


class TestLogParser(unittest.TestCase):
    def setUp(self):
        """Создаем тестовые данные."""
        self.logs = [
            '127.0.0.1 - - [10/Sep/2024:14:55:45 +0000] "GET / HTTP/1.1" 200 612 "-" "Mozilla/5.0" 0.005',
            '192.168.1.1 - - [10/Sep/2024:14:55:46 +0000] "POST /login HTTP/1.1" 302 512 "-" "Mozilla/5.0" 0.015',
            '127.0.0.1 - - [10/Sep/2024:14:56:00 +0000] "GET /dashboard HTTP/1.1" 200 1248 "-" "Mozilla/5.0" 0.025'
        ]

    def test_parse_logs(self):
        """Проверяем парсинг логов."""
        result = parse_logs(self.logs)

        # Проверка количества обработанных логов
        self.assertEqual(len(result['parsed_logs']), 3)

        # Проверка данных первого лога
        first_log = result['parsed_logs'][0]
        self.assertEqual(first_log['ip'], '127.0.0.1')
        self.assertEqual(first_log['method'], 'GET')
        self.assertEqual(first_log['response_time'], 0.005)

        # Проверка статистики
        stats = result['stats']
        self.assertEqual(stats['total_requests'], 3)
        self.assertAlmostEqual(stats['mean_response_time'], 0.015)
        self.assertAlmostEqual(stats['median_response_time'], 0.015)
        self.assertEqual(stats['min_response_time'], 0.005)
        self.assertEqual(stats['max_response_time'], 0.025)
        self.assertEqual(stats['status_distribution'], {200: 2, 302: 1})

        # Проверка статистики по IP
        ip_stats = result['ip_stats']
        self.assertAlmostEqual(ip_stats['127.0.0.1'], 0.015)
        self.assertAlmostEqual(ip_stats['192.168.1.1'], 0.015)


if __name__ == '__main__':
    unittest.main()
