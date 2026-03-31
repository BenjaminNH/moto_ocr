import pytest
from moto_ocr.settlement import build_group_text, build_total_text


class TestBuildGroupText:
    def test_single_30_commission(self):
        result = build_group_text("群A", count_30=2, count_50=0, total_commission=60)
        assert "群A" in result
        assert "2单30" in result
        assert "2×30 = 60" in result
        assert "付60元" in result

    def test_single_50_commission(self):
        result = build_group_text("群B", count_30=0, count_50=3, total_commission=150)
        assert "群B" in result
        assert "3单50" in result
        assert "3×50 = 150" in result
        assert "付150元" in result

    def test_mixed_commission(self):
        result = build_group_text("群C", count_30=2, count_50=1, total_commission=110)
        assert "群C" in result
        assert "2单30" in result
        assert "1单50" in result
        assert "2×30 + 1×50 = 110" in result
        assert "付110元" in result

    def test_zero_commission(self):
        result = build_group_text("群D", count_30=0, count_50=0, total_commission=0)
        assert "群D" in result
        assert "付0元" in result


class TestBuildTotalText:
    def test_single_type(self):
        result = build_total_text(count_30=5, count_50=0, total_commission=150)
        assert "总共" in result
        assert "5单30" in result
        assert "5×30 = 150" in result
        assert "付150元" in result

    def test_mixed_types(self):
        result = build_total_text(count_30=3, count_50=2, total_commission=190)
        assert "总共" in result
        assert "3单30" in result
        assert "2单50" in result
        assert "3×30 + 2×50 = 190" in result
        assert "付190元" in result

    def test_zero_commission(self):
        result = build_total_text(count_30=0, count_50=0, total_commission=0)
        assert "总共" in result
        assert "付0元" in result
