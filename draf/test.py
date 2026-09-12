import os

def calculate_statistics(file_path):
    """
    Đọc tệp giao dịch (FIMI/SPMF) và tính toán:
    - Size |D| (Tổng số giao dịch) 
    - Distinct Items DI (D) (Số mục độc nhất)
    - Average Transaction Length (ATL)
    - Density (Một transaction trung bình chứa khoảng 50% tập item khác nhau của dataset. ATL / DI * 100)
    """
    total_transactions = 0
    total_items_count = 0
    distinct_items = set()

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Không tìm thấy file dataset tại: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            items = line.split()
            
            total_transactions += 1
            total_items_count += len(items)
            distinct_items.update(items)

    distinct_items_count = len(distinct_items)
    
    atl = total_items_count / total_transactions if total_transactions > 0 else 0.0
    
    density = (atl / distinct_items_count) * 100 if distinct_items_count > 0 else 0.0

    return {
        "size_D": total_transactions,
        "distinct_I": distinct_items_count,
        "atl": atl,
        "density": density
    }

def print_stats_table(datasets_dict):
    
    header = f" {'Dataset':<22} | {'Size |D|':>12} | {'DI(D)':>8} | {'ATL(D)':>8} | {'Density(D) (%)':>15} "
    separator = "=" * len(header)
    
    print(separator)
    print(header)
    print(separator)
    
    for name, stats in datasets_dict.items():
        print(f" {name:<22} | {stats['size_D']:>12,} | {stats['distinct_I']:>8,} | {stats['atl']:>8.2f} | {stats['density']:>13.2f}% ")
        
    print(separator)

if __name__ == "__main__":

    datasets_to_run = {
        "Requirements": "Datasets/crawling/requirements.txt",
        "Themealdb": "Datasets/crawling/themealdb.txt"
        
    }
    results = {}
    for name, path in datasets_to_run.items():
        if os.path.exists(path):
            results[name] = calculate_statistics(path)

            
    if results:
        print_stats_table(results)
    else:
        print("Errrr'")


