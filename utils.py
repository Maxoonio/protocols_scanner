def get_user_input(prompt: str, default: str, validator=None) -> str:
    while True:
        try:
            value = input(f"{prompt} (default {default}): ") or default
            if validator:
                validator(value)
            return value
        except ValueError as e:
            print(f"Error: {e}")


def validate_port(port: str) -> int:
    port_int = int(port)
    if not 1 <= port_int <= 65535:
        raise ValueError("Port must be 1-65535")
    return port_int


def validate_threads(threads: str) -> int:
    from constants import MAX_THREADS
    threads_int = int(threads)
    if not 1 <= threads_int <= MAX_THREADS:
        raise ValueError(f"Threads must be 1-{MAX_THREADS}")
    return threads_int
