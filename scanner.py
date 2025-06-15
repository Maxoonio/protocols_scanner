import socket
import concurrent.futures
import time
import ipaddress
import sys
from typing import Tuple, List
from collections import defaultdict

from common import Protocol, PortStatus, Colors
from constants import MAX_THREADS, BASE_TIMEOUT, BANNER_TIMEOUT, KNOWN_PORTS


class PortScanner:
    def __init__(self, target='localhost', timeout=BASE_TIMEOUT):
        self.target = target
        self.target_ip = ""
        self.timeout = timeout
        self.icmp_blocked = False
        self.scan_stats = defaultdict(int, {
            'start_time': 0, 'end_time': 0
        })

    def validate_target(self) -> bool:
        try:
            ipaddress.ip_address(self.target)
            self.target_ip = self.target
            return True
        except ValueError:
            try:
                self.target_ip = socket.gethostbyname(self.target)
                return True
            except socket.gaierror:
                return False

    def validate_port_range(self, start: int, end: int) -> bool:
        return 1 <= start <= end <= 65535

    def create_socket(self, is_tcp: bool, timeout=None) -> socket.socket:
        sock_type = socket.SOCK_STREAM if is_tcp else socket.SOCK_DGRAM
        sock = socket.socket(socket.AF_INET, sock_type)
        sock.settimeout(timeout or self.timeout)
        return sock

    def detect_protocol(self, port: int, is_tcp: bool = True) -> Protocol:
        if port in KNOWN_PORTS:
            return KNOWN_PORTS[port]
        return Protocol.UNKNOWN

    def scan_tcp_port(self, port: int) -> Tuple[int, str, PortStatus, str]:
        try:
            with self.create_socket(True, self.timeout) as sock:
                if sock.connect_ex((self.target_ip, port)) == 0:
                    protocol = self.detect_protocol(port, is_tcp=True)
                    self.scan_stats['tcp_open'] += 1
                    return port, "TCP", PortStatus.OPEN, protocol.value
                return port, "TCP", PortStatus.CLOSED, ""
        except Exception as e:
            self.scan_stats['errors'] += 1
            return port, "TCP", PortStatus.ERROR, str(e)

    def scan_udp_port(self, port: int) -> Tuple[int, str, PortStatus, str]:
        try:
            with self.create_socket(False, BANNER_TIMEOUT) as sock:
                sock.sendto(b'', (self.target_ip, port))  #\xaa\xbb\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00
                sock.recvfrom(1024)

                protocol = self.detect_protocol(port, is_tcp=False)
                self.scan_stats['udp_open'] += 1
                return port, "UDP", PortStatus.OPEN, protocol.value

        except socket.timeout:
            self.scan_stats['udp_filtered'] += 1
            return (port, "UDP", PortStatus.FILTERED, Protocol.UNKNOWN.value)

        except ConnectionResetError:
            return (port, "UDP", PortStatus.CLOSED, "")

        except Exception as e:
            self.scan_stats['errors'] += 1
            return (port, "UDP", PortStatus.ERROR, str(e))

    def scan_ports(self, start: int, end: int, workers: int) -> List[Tuple[int, str, PortStatus, str]]:
        if not self.validate_target():
            raise ValueError(f"Неверная цель: {self.target}")
        if not self.validate_port_range(start, end):
            raise ValueError("Неверный диапазон портов")

        workers = min(workers, MAX_THREADS)
        port_count = end - start + 1
        self.scan_stats.update({
            'total_tcp': port_count, 'total_udp': port_count, 'start_time': time.time()
        })

        results = []
        ports_to_scan = range(start, end + 1)

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures_tcp = {executor.submit(self.scan_tcp_port, port) for port in ports_to_scan}
            futures_udp = {executor.submit(self.scan_udp_port, port) for port in ports_to_scan}
            all_futures = futures_tcp.union(futures_udp)

            total_tasks = len(all_futures)
            for i, future in enumerate(concurrent.futures.as_completed(all_futures), 1):
                results.append(future.result())
                self.print_progress(i, total_tasks)

        if not any(res[2] == PortStatus.CLOSED and res[1] == "UDP" for res in results):
            self.icmp_blocked = True

        return sorted(results, key=lambda x: (x[0], x[1]))

    def print_progress(self, completed: int, total: int):
        progress = (completed / total) * 100
        sys.stdout.write(f"\rПрогресс сканирования: {completed}/{total} ({progress:.1f}%)")
        sys.stdout.flush()

    def print_stats(self):
        if self.scan_stats['end_time'] == 0:
            self.scan_stats['end_time'] = time.time()
        duration = self.scan_stats['end_time'] - self.scan_stats['start_time']

        total_scans = self.scan_stats['total_tcp'] + self.scan_stats['total_udp']
        pps = total_scans / duration if duration > 0 else 0

        print(f"\n\n{'=' * 50}")
        print("Статистика сканирования".center(50))
        print(f"{'=' * 50}")
        print(f"{'Цель хоста:':<25}{self.target} ({self.target_ip})")
        print(f"{'Длительность:':<25}{duration:.2f} сек.")
        print(f"{'Скорость:':<25}{pps:.1f} сканирований/сек")
        print(f"{'Ошибок при сканировании:':<25}{self.scan_stats['errors']}")
        print("-" * 50)

        print(f"{'Просканировано TCP портов:':<25}{self.scan_stats['total_tcp']}")
        print(f"{'Открыто TCP портов:':<25}{self.scan_stats['tcp_open']}")
        print("-" * 50)

        print(f"{'Просканировано UDP портов:':<25}{self.scan_stats['total_udp']}")
        print(f"{'Открыто/Фильтруются UDP:':<25}{self.scan_stats['udp_open'] + self.scan_stats['udp_filtered']}")

        if self.icmp_blocked:
            print(f"\n{Colors.YELLOW}[ПРЕДУПРЕЖДЕНИЕ]{Colors.END}")
            print("ICMP-ответы ('порт недоступен') не были получены.")
            print("Результаты UDP-сканирования могут быть неточными, так как")
            print("брандмауэр может блокировать ICMP-сообщения.")

        print(f"{'=' * 50}")