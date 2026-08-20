from masking import MASK, clear_secrets, mask, register_secret


class TestMasking:
    def test_registered_secret_is_masked(self):
        register_secret("supersecret")
        assert mask("zip -P supersecret -r out.zip .") == f"zip -P {MASK} -r out.zip ."

    def test_multiple_occurrences_are_masked(self):
        register_secret("pw1234")
        assert mask("pw1234 and pw1234") == f"{MASK} and {MASK}"

    def test_unregistered_value_is_untouched(self):
        assert mask("zip -P other -r out.zip .") == "zip -P other -r out.zip ."

    def test_empty_secret_is_not_registered(self):
        register_secret("")
        assert mask("") == ""
        assert mask("anything") == "anything"

    def test_very_short_secret_is_not_registered(self):
        """A 1-2 character secret would mask unrelated substrings everywhere."""
        register_secret("a")
        assert mask("a banana") == "a banana"

    def test_short_secret_refusal_is_logged(self, caplog):
        register_secret("ab")
        assert "cannot be masked" in caplog.text

    def test_clear_secrets(self):
        register_secret("topsecret")
        clear_secrets()
        assert mask("topsecret") == "topsecret"
