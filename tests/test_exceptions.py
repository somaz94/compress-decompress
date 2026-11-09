import pytest
from exceptions import CommandError, CompressError, IntegrityError, ValidationError


class TestExceptionHierarchy:
    def test_validation_error_is_compress_error(self):
        assert issubclass(ValidationError, CompressError)

    def test_integrity_error_is_validation_error(self):
        assert issubclass(IntegrityError, ValidationError)

    def test_command_error_is_compress_error(self):
        assert issubclass(CommandError, CompressError)

    def test_compress_error_is_exception(self):
        assert issubclass(CompressError, Exception)

    def test_catch_all_with_compress_error(self):
        with pytest.raises(CompressError):
            raise ValidationError("test")

        with pytest.raises(CompressError):
            raise CommandError("test")
