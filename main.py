from scanner import PortScanner
from common import Colors, PortStatus
from utils import get_user_input, validate_port, validate_threads


def main():
    print("\n--- Многопоточный TCP/UDP сканер портов ---")
    print("=" * 45)

    try:
        target = get_user_input("Введите цель (IP или домен)", "localhost")
        start_port_str = get_user_input("Начальный порт", "1", validate_port)
        end_port_str = get_user_input("Конечный порт", "1024", validate_port)
        threads_str = get_user_input("Количество потоков", "100", validate_threads)

        start_port = int(start_port_str)
        end_port = int(end_port_str)
        threads = int(threads_str)

        if start_port > end_port:
            start_port, end_port = end_port, start_port
            print(f"Диапазон портов скорректирован на {start_port}-{end_port}")

        scanner = PortScanner(target=target)

        if not scanner.validate_target():
            print(f"\n{Colors.RED}Ошибка: не удалось определить IP-адрес для цели '{target}'{Colors.END}")
            return

        print(f"\nЗапуск сканирования {target} (порты {start_port}-{end_port}) в {threads} потоков...")

        scanner.scan_stats['start_time'] = scanner.scan_stats.get('start_time', __import__('time').time())
        results = scanner.scan_ports(start_port, end_port, workers=threads)
        scanner.scan_stats['end_time'] = __import__('time').time()

        print("\n\nРезультаты сканирования (открытые/фильтруемые порты):")
        header = f"{'Порт':<8} {'Тип':<6} {'Статус':<18} {'Протокол'}"
        print(header)
        print("-" * len(header))

        found_any = False
        for port, p_type, status, protocol in results:
            if status in (PortStatus.OPEN, PortStatus.FILTERED):
                found_any = True
                status_str = status.value
                if status == PortStatus.OPEN:
                    status_colored = f"{Colors.GREEN}{status_str:<10}{Colors.END}"
                else:  # Filtered
                    status_colored = f"{Colors.YELLOW}{status_str:<10}{Colors.END}"

                print(f"{port:<8} {p_type:<6} {status_colored:<18} {protocol}")

        if not found_any:
            print("Открытые или фильтруемые порты не найдены.")

        scanner.print_stats()

    except (KeyboardInterrupt, EOFError):
        print("\n\nСканирование прервано пользователем.")
    except Exception as e:
        print(f"\n{Colors.RED}Произошла критическая ошибка: {e}{Colors.END}")
    finally:
        print("\nРабота сканера завершена.")


if __name__ == "__main__":
    main()
