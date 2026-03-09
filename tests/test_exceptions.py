from exceptions import CompressError, ValidationError, CommandError


class TestExceptionHierarchy:
    def test_validation_error_is_compress_error(self):
        assert issubclass(ValidationError, CompressError)

    def test_command_error_is_compress_error(self):
        assert issubclass(CommandError, CompressError)

    def test_compress_error_is_exception(self):
        assert issubclass(CompressError, Exception)

    def test_catch_all_with_compress_error(self):
        """CompressError should catch both ValidationError and CommandError"""
        with pytest.raises(CompressError):
            raise ValidationError("test")

        with pytest.raises(CompressError):
            raise CommandError("test")


import pytest
