from enum import Enum


class Colors:
    GREEN = '\033[92m'  # Цвет для открытых портов
    YELLOW = '\033[93m'  # Цвет для фильтруемых портов
    RED = '\033[91m'  # Цвет для ошибок
    END = '\033[0m'  # Сброс цвета


class Protocol(Enum):
    HTTP = "HTTP"
    HTTPS = "HTTPS"
    SMTP = "SMTP"
    POP3 = "POP3"
    DNS = "DNS"
    NTP = "NTP"
    SSH = "SSH"
    FTP = "FTP"
    MYSQL = "MySQL"
    DHCP = "DHCP"
    SNMP = "SNMP"
    RDP = "RDP"
    UNKNOWN = "Unknown"


class PortStatus(Enum):
    OPEN = "Open"
    CLOSED = "Closed"
    FILTERED = "Filtered"
    ERROR = "Error"
