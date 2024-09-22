import sys

from src.log_analyzer import parse_logs


def main() -> None:
    if len(sys.argv) != 2:
        print('Usage: analyze-logs <path_to_log_file>')
        sys.exit(1)

    log_file = sys.argv[1]

    try:
        with open(log_file, 'r') as f:
            logs = f.readlines()
            result = parse_logs(logs=logs)
            print(result)
    except FileNotFoundError:
        print(f'Log file {log_file} not found.')
        sys.exit(1)


if __name__ == '__main__':
    main()
