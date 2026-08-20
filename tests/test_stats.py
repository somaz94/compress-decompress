from stats import OperationStats


class TestOperationStats:
    def test_defaults_are_falsy(self):
        stats = OperationStats()
        assert not stats
        assert stats.compression_ratio == 0.0

    def test_success_is_truthy(self):
        assert OperationStats(success=True)

    def test_compression_ratio(self):
        stats = OperationStats(original_size=1000, compressed_size=250)
        assert stats.compression_ratio == 75.0

    def test_ratio_zero_when_original_unknown(self):
        assert OperationStats(original_size=0, compressed_size=100).compression_ratio == 0.0

    def test_ratio_zero_when_compressed_unknown(self):
        assert OperationStats(original_size=100, compressed_size=0).compression_ratio == 0.0

    def test_ratio_negative_when_archive_grew(self):
        stats = OperationStats(original_size=100, compressed_size=150)
        assert stats.compression_ratio == -50.0
