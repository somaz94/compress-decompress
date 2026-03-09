class UI:
    """Standardized output formatting for the application"""

    @staticmethod
    def print_header(title: str):
        print("\n" + "=" * 50)
        print(f"\u25b6\ufe0f {title}")
        print("=" * 50 + "\n")

    @staticmethod
    def print_section(title: str):
        print(f"\n\U0001f4cb {title}:")

    @staticmethod
    def print_success(message: str):
        print(f"\u2705 {message}")

    @staticmethod
    def print_error(message: str):
        print(f"\u274c {message}")
