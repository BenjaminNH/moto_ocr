import pytest
from moto_ocr.commission import match_premium, calculate_commission


class TestMatchPremium:
    def test_match_356(self):
        result = match_premium(356)
        assert result == {"compulsory": 156, "accident": 200, "tax": 0}

    def test_match_456_no_tax(self):
        result = match_premium(456)
        assert result == {"compulsory": 156, "accident": 300, "tax": 0}

    def test_match_304(self):
        result = match_premium(304)
        assert result == {"compulsory": 104, "accident": 200, "tax": 0}

    def test_match_404(self):
        result = match_premium(404)
        assert result == {"compulsory": 104, "accident": 300, "tax": 0}

    def test_match_492_with_tax(self):
        result = match_premium(492)
        assert result == {"compulsory": 156, "accident": 300, "tax": 36}

    def test_no_match(self):
        result = match_premium(999)
        assert result is None

    def test_match_456_with_monthly_tax(self):
        # 5月: tax = 3 * (13 - 5) = 24, total = 456 + 24 = 480
        result = match_premium(480, month=5)
        assert result == {"compulsory": 156, "accident": 300, "tax": 24}


class TestCalculateCommission:
    def test_accident_200_commission_30(self):
        assert calculate_commission(200) == 30

    def test_accident_300_commission_50(self):
        assert calculate_commission(300) == 50

    def test_no_accident_no_commission(self):
        assert calculate_commission(0) == 0

    def test_unknown_amount_no_commission(self):
        assert calculate_commission(150) == 0
