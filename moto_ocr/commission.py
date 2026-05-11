import json
from functools import lru_cache
from pathlib import Path


RULES_FILE = Path(__file__).resolve().parent.parent / "settlement_rules.json"


def _validate_rules(rules):
    if not isinstance(rules, dict):
        raise ValueError("settlement_rules.json 顶层必须是 JSON 对象")

    compulsory_amounts = rules.get("compulsory_amounts")
    if not isinstance(compulsory_amounts, list) or not compulsory_amounts:
        raise ValueError("settlement_rules.json: compulsory_amounts 必须是非空数组")
    for amount in compulsory_amounts:
        if not isinstance(amount, int) or amount <= 0:
            raise ValueError(
                f"settlement_rules.json: compulsory_amounts 中存在无效金额 {amount!r}，必须为正整数"
            )

    taxable_compulsory_amounts = rules.get("taxable_compulsory_amounts", [])
    if not isinstance(taxable_compulsory_amounts, list):
        raise ValueError("settlement_rules.json: taxable_compulsory_amounts 必须是数组")
    invalid_taxable_amounts = [
        amount for amount in taxable_compulsory_amounts if amount not in compulsory_amounts
    ]
    if invalid_taxable_amounts:
        raise ValueError(
            "settlement_rules.json: taxable_compulsory_amounts 中的金额必须已存在于 "
            f"compulsory_amounts，发现无效值 {invalid_taxable_amounts!r}"
        )

    monthly_tax = rules.get("monthly_tax", {})
    if not isinstance(monthly_tax, dict):
        raise ValueError("settlement_rules.json: monthly_tax 必须是对象，键为 1-12 月份")
    for month, tax_amount in monthly_tax.items():
        try:
            month_int = int(month)
        except (TypeError, ValueError):
            raise ValueError(
                f"settlement_rules.json: monthly_tax 中的月份键 {month!r} 无效，必须为 1-12"
            ) from None
        if month_int < 1 or month_int > 12:
            raise ValueError(
                f"settlement_rules.json: monthly_tax 中的月份键 {month!r} 超出范围，必须为 1-12"
            )
        if not isinstance(tax_amount, int) or tax_amount < 0:
            raise ValueError(
                f"settlement_rules.json: monthly_tax[{month!r}]={tax_amount!r} 无效，税额必须为非负整数"
            )

    accident_plans = rules.get("accident_plans")
    if not isinstance(accident_plans, list) or not accident_plans:
        raise ValueError("settlement_rules.json: accident_plans 必须是非空数组")

    seen_accident_amounts = set()
    for idx, plan in enumerate(accident_plans, 1):
        if not isinstance(plan, dict):
            raise ValueError(
                f"settlement_rules.json: accident_plans 第 {idx} 项必须是对象"
            )
        if "amount" not in plan:
            raise ValueError(
                f"settlement_rules.json: accident_plans 第 {idx} 项缺少 amount 字段"
            )
        if "commission" not in plan:
            raise ValueError(
                f"settlement_rules.json: accident_plans 第 {idx} 项缺少 commission 字段"
            )

        amount = plan["amount"]
        commission = plan["commission"]
        if not isinstance(amount, int) or amount <= 0:
            raise ValueError(
                f"settlement_rules.json: accident_plans 第 {idx} 项 amount={amount!r} 无效，必须为正整数"
            )
        if not isinstance(commission, int) or commission < 0:
            raise ValueError(
                "settlement_rules.json: accident_plans "
                f"第 {idx} 项 commission={commission!r} 无效，必须为非负整数"
            )
        if amount in seen_accident_amounts:
            raise ValueError(
                f"settlement_rules.json: accident_plans 中存在重复的 amount={amount}"
            )
        seen_accident_amounts.add(amount)


@lru_cache(maxsize=1)
def load_rules():
    """加载结算规则配置。"""
    try:
        with RULES_FILE.open("r", encoding="utf-8") as f:
            rules = json.load(f)
    except FileNotFoundError as exc:
        raise ValueError(f"未找到结算规则配置文件：{RULES_FILE}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"settlement_rules.json 格式错误：第 {exc.lineno} 行第 {exc.colno} 列附近不是合法 JSON"
        ) from exc

    _validate_rules(rules)

    compulsory_amounts = rules.get("compulsory_amounts", [])
    accident_plans = rules.get("accident_plans", [])
    monthly_tax = rules.get("monthly_tax", {})
    taxable_compulsory_amounts = set(rules.get("taxable_compulsory_amounts", []))

    if not compulsory_amounts:
        raise ValueError("settlement_rules.json 中缺少 compulsory_amounts 配置")
    if not accident_plans:
        raise ValueError("settlement_rules.json 中缺少 accident_plans 配置")

    accident_commission_map = {}
    for plan in accident_plans:
        amount = int(plan["amount"])
        accident_commission_map[amount] = int(plan["commission"])

    normalized_monthly_tax = {
        int(month): int(tax_amount)
        for month, tax_amount in monthly_tax.items()
    }

    return {
        "compulsory_amounts": [int(amount) for amount in compulsory_amounts],
        "taxable_compulsory_amounts": taxable_compulsory_amounts,
        "monthly_tax": normalized_monthly_tax,
        "accident_commission_map": accident_commission_map,
        "accident_amounts": list(accident_commission_map.keys()),
    }


def _tax_candidates(compulsory_amount, month=None):
    rules = load_rules()
    if compulsory_amount not in rules["taxable_compulsory_amounts"]:
        return [0]

    all_tax_amounts = list(rules["monthly_tax"].values())

    if month is not None:
        preferred_tax = rules["monthly_tax"].get(month, 0)
        ordered_candidates = [0, preferred_tax]
        ordered_candidates.extend(
            tax_amount for tax_amount in all_tax_amounts
            if tax_amount not in ordered_candidates
        )
        return ordered_candidates

    return [0, *all_tax_amounts]


def match_premium(total_amount, month=None):
    """匹配保费金额组合，返回对应的交强险、意外险、税额信息。

    Args:
        total_amount: 总金额（已含税）
        month: 当前月份（1-12），用于优先匹配对应月份税额

    Returns:
        dict: {"compulsory": int, "accident": int, "tax": int} 或 None
    """
    rules = load_rules()

    for compulsory_amount in rules["compulsory_amounts"]:
        for accident_amount in rules["accident_amounts"]:
            for tax_amount in _tax_candidates(compulsory_amount, month=month):
                if total_amount == compulsory_amount + accident_amount + tax_amount:
                    return {
                        "compulsory": compulsory_amount,
                        "accident": accident_amount,
                        "tax": tax_amount,
                    }
    return None


def calculate_commission(accident_amount):
    """根据意外险金额计算佣金。"""
    rules = load_rules()
    return rules["accident_commission_map"].get(accident_amount, 0)
