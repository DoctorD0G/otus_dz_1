import re
from collections import defaultdict
from statistics import mean, median

LOG_PATTERN = r'(?P<ip>\S+) - - \[(?P<time>[^\]]+)\] "(?P<method>\S+) (?P<url>\S+) \S+" (?P<status>\d{3}) (?P<size>\d+) "(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)" (?P<response_time>\d+\.\d+)'


def parse_logs(logs: list):
    parsed_logs = []
    ip_stats = defaultdict(list)
    response_times = []
    status_counts = defaultdict(int)

    for log in logs:
        match = re.match(LOG_PATTERN, log.strip())
        if match:
            log_data = match.groupdict()
            log_data['status'] = int(log_data['status'])
            log_data['response_time'] = float(log_data['response_time'])
            ip_stats[log_data['ip']].append(log_data['response_time'])
            response_times.append(log_data['response_time'])
            status_counts[log_data['status']] += 1
            parsed_logs.append(log_data)

    stats = {
        'total_requests': len(parsed_logs),
        'mean_response_time': mean(response_times) if response_times else 0,
        'median_response_time': median(response_times) if response_times else 0,
        'min_response_time': min(response_times) if response_times else 0,
        'max_response_time': max(response_times) if response_times else 0,
        'status_distribution': dict(status_counts)
    }

    return {
        'parsed_logs': parsed_logs,
        'stats': stats,
        'ip_stats': {ip: mean(times) for ip, times in ip_stats.items()}
    }
