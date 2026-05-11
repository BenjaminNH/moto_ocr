import pytest
from moto_ocr import commission
from moto_ocr.commission import match_premium, calculate_commission


class TestMatchPremium:
    def test_match_356(self):
        result = match_premium(356)
        assert result == {"compulsory": 156, "accident": 200, "tax": 0}

    def test_match_458_no_tax(self):
        result = match_premium(458)
        assert result == {"compulsory": 156, "accident": 302, "tax": 0}

    def test_match_304(self):
        result = match_premium(304)
        assert result == {"compulsory": 104, "accident": 200, "tax": 0}

    def test_match_406(self):
        result = match_premium(406)
        assert result == {"compulsory": 104, "accident": 302, "tax": 0}

    def test_match_556_no_tax(self):
        result = match_premium(556)
        assert result == {"compulsory": 156, "accident": 400, "tax": 0}

    def test_match_380_with_tax_on_200_plan(self):
        result = match_premium(380, month=5)
        assert result == {"compulsory": 156, "accident": 200, "tax": 24}

    def test_match_482_with_tax_on_302_plan(self):
        result = match_premium(482, month=5)
        assert result == {"compulsory": 156, "accident": 302, "tax": 24}

    def test_match_494_with_historical_tax_on_302_plan(self):
        result = match_premium(494, month=5)
        assert result == {"compulsory": 156, "accident": 302, "tax": 36}

    def test_match_580_with_tax_on_400_plan(self):
        result = match_premium(580, month=5)
        assert result == {"compulsory": 156, "accident": 400, "tax": 24}

    def test_no_match(self):
        result = match_premium(999)
        assert result is None

    def test_match_taxed_amount_without_month(self):
        result = match_premium(482)
        assert result == {"compulsory": 156, "accident": 302, "tax": 24}


class TestCalculateCommission:
    def test_accident_200_commission_0(self):
        assert calculate_commission(200) == 0

    def test_accident_302_commission_30(self):
        assert calculate_commission(302) == 30

    def test_accident_400_commission_50(self):
        assert calculate_commission(400) == 50

    def test_no_accident_no_commission(self):
        assert calculate_commission(0) == 0

    def test_unknown_amount_no_commission(self):
        assert calculate_commission(150) == 0


class TestLoadRulesValidation:
    def setup_method(self):
        commission.load_rules.cache_clear()

    def teardown_method(self):
        commission.load_rules.cache_clear()

    def test_duplicate_accident_amount_raises_clear_error(self, monkeypatch):
        monkeypatch.setattr(
            commission,
            "RULES_FILE",
            None,
        )
        monkeypatch.setattr(
            commission.json,
            "load",
            lambda _: {
                "accident_plans": [
                    {"amount": 302, "commission": 30},
                    {"amount": 302, "commission": 50},
                ],
                "compulsory_amounts": [104, 156],
                "taxable_compulsory_amounts": [156],
                "monthly_tax": {"1": 36},
            },
        )

        class DummyFile:
            def __enter__(self):
                return object()

            def __exit__(self, exc_type, exc, tb):
                return False

        class DummyPath:
            def open(self, *args, **kwargs):
                return DummyFile()

        monkeypatch.setattr(commission, "RULES_FILE", DummyPath())

        with pytest.raises(ValueError, match="重复的 amount=302"):
            commission.load_rules()

    def test_missing_commission_field_raises_clear_error(self, monkeypatch):
        monkeypatch.setattr(
            commission.json,
            "load",
            lambda _: {
                "accident_plans": [{"amount": 302}],
                "compulsory_amounts": [104, 156],
                "taxable_compulsory_amounts": [156],
                "monthly_tax": {"1": 36},
            },
        )

        class DummyFile:
            def __enter__(self):
                return object()

            def __exit__(self, exc_type, exc, tb):
                return False

        class DummyPath:
            def open(self, *args, **kwargs):
                return DummyFile()

        monkeypatch.setattr(commission, "RULES_FILE", DummyPath())

        with pytest.raises(ValueError, match="缺少 commission 字段"):
            commission.load_rules()
