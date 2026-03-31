# 保费组合配置
PREMIUM_CASES = [
    {"total": 356, "compulsory": 156, "accident": 200, "tax": 0},
    {"total": 456, "compulsory": 156, "accident": 300, "tax": 0},
    {"total": 304, "compulsory": 104, "accident": 200, "tax": 0},
    {"total": 404, "compulsory": 104, "accident": 300, "tax": 0},
    {"total": 492, "compulsory": 156, "accident": 300, "tax": 36},
]


def match_premium(total_amount, month=None):
    """匹配保费金额组合，返回对应的交强险、意外险、税额信息。
    
    Args:
        total_amount: 总金额（已含税）
        month: 当前月份（1-12），用于计算动态税额
        
    Returns:
        dict: {"compulsory": int, "accident": int, "tax": int} 或 None
    """
    # 动态计算含税组合
    cases = list(PREMIUM_CASES)
    if month is not None and 1 <= month <= 12:
        tax_amount = 3 * (13 - month)
        cases.append({
            "total": 456 + tax_amount,
            "compulsory": 156,
            "accident": 300,
            "tax": tax_amount,
        })
    
    for case in cases:
        if total_amount == case["total"]:
            return {
                "compulsory": case["compulsory"],
                "accident": case["accident"],
                "tax": case["tax"],
            }
    return None


def calculate_commission(accident_amount):
    """根据意外险金额计算佣金。
    
    Args:
        accident_amount: 意外险金额
        
    Returns:
        int: 佣金金额
    """
    if accident_amount == 200:
        return 30
    elif accident_amount == 300:
        return 50
    return 0
