def build_group_text(group_name, count_30, count_50, total_commission):
    """生成单个群组的结算文本。
    
    Args:
        group_name: 群组名称
        count_30: 30元佣金单数
        count_50: 50元佣金单数
        total_commission: 总佣金
        
    Returns:
        str: 结算文本
    """
    group_detail = []
    commission_parts = []
    
    if count_30 > 0:
        group_detail.append(f"{count_30}单30")
        commission_parts.append(f"{count_30}×30")
    if count_50 > 0:
        group_detail.append(f"{count_50}单50")
        commission_parts.append(f"{count_50}×50")
    
    group_text = f"{group_name} {', '.join(group_detail)}"
    if len(commission_parts) > 0:
        group_text += f"，{' + '.join(commission_parts)} = {total_commission}"
    group_text += f"，付{total_commission}元"
    
    return group_text


def build_total_text(count_30, count_50, total_commission):
    """生成总结算文本。
    
    Args:
        count_30: 30元佣金总单数
        count_50: 50元佣金总单数
        total_commission: 总佣金
        
    Returns:
        str: 总结算文本
    """
    total_parts = []
    commission_parts = []
    
    if count_30 > 0:
        total_parts.append(f"{count_30}单30")
        commission_parts.append(f"{count_30}×30")
    if count_50 > 0:
        total_parts.append(f"{count_50}单50")
        commission_parts.append(f"{count_50}×50")
    
    total_text = f"总共 {', '.join(total_parts)}"
    if len(commission_parts) > 0:
        total_text += f"，{' + '.join(commission_parts)} = {total_commission}"
    total_text += f"，付{total_commission}元"
    
    return total_text
