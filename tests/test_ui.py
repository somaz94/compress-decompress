from ui import UI


class TestUI:
    def test_print_header(self, capsys):
        UI.print_header("Test Header")
        output = capsys.readouterr().out
        assert "Test Header" in output
        assert "=" in output

    def test_print_section(self, capsys):
        UI.print_section("Test Section")
        output = capsys.readouterr().out
        assert "Test Section" in output

    def test_print_success(self, capsys):
        UI.print_success("Operation done")
        output = capsys.readouterr().out
        assert "Operation done" in output

    def test_print_error(self, capsys):
        UI.print_error("Something failed")
        output = capsys.readouterr().out
        assert "Something failed" in output
