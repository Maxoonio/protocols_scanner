from common import Protocol

MAX_THREADS = 500
BASE_TIMEOUT = 1.0   # Базовый таймаут для соединения
BANNER_TIMEOUT = 0.3  # Таймаут для чтения баннеров сервисов


KNOWN_PORTS = {
    21: Protocol.FTP,
    22: Protocol.SSH,
    23: Protocol.SSH,
    25: Protocol.SMTP,
    53: Protocol.DNS,
    80: Protocol.HTTP,
    110: Protocol.POP3,
    143: Protocol.POP3,
    443: Protocol.HTTPS,
    465: Protocol.SMTP,
    993: Protocol.POP3,
    3306: Protocol.MYSQL,
    3389: Protocol.RDP,
    67: Protocol.DHCP,
    68: Protocol.DHCP,
    161: Protocol.SNMP
}