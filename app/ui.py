BULLET = "•"
HEADER_ARROW = "▶️"
SECTION_ICON = "\U0001f4cb"
SUCCESS_ICON = "✅"
ERROR_ICON = "❌"
GEAR_ICON = "⚙️"


class UI:
    """Standardized output formatting for the application"""

    @staticmethod
    def print_header(title: str):
        print("\n" + "=" * 50)
        print(f"{HEADER_ARROW} {title}")
        print("=" * 50 + "\n")

    @staticmethod
    def print_section(title: str):
        print(f"\n{SECTION_ICON} {title}:")

    @staticmethod
    def print_success(message: str):
        print(f"{SUCCESS_ICON} {message}")

    @staticmethod
    def print_error(message: str):
        print(f"{ERROR_ICON} {message}")

    @staticmethod
    def print_kv(key: str, value):
        print(f"  {BULLET} {key}: {value}")

    @staticmethod
    def print_bullet(message: str):
        print(f"  {BULLET} {message}")
