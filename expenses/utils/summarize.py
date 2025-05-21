from collections import defaultdict

def summarize(expenses, all_root_names):
    amount_dict = defaultdict(float)
    count_dict = defaultdict(int)

    for expense in expenses:
        root = expense.category.get_root_category() if expense.category else None
        root_name = root.name if root and root.name in all_root_names else "미분류"
        amount_dict[root_name] += float(expense.amount)
        count_dict[root_name] += 1

    category_summary = []
    for name in all_root_names:
        category_summary.append({
            "parent": name,
            "amount": round(amount_dict.get(name, 0)),
            "count": count_dict.get(name, 0),
        })

    total_amount = round(sum(amount_dict.values()))
    return total_amount, category_summary
