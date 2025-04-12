import pandas as pd
from inventory.models import Product
import re

df = pd.read_csv('products.csv', encoding='utf-8-sig')

for index, row in df.iterrows():
    product_name = str(row['product_name']).strip()
    warehouse = str(row['warehouse']).strip()
    shelf_number = str(row['shelf_number']).strip().zfill(2)
    column = str(row['column']).strip()

    # level에서 숫자만 추출
    level_str = str(row['level']).strip()
    level_digits = re.findall(r'\d+', level_str)
    level = int(level_digits[0]) if level_digits else 0  # 숫자 없으면 0

    Product.objects.create(
        product_name=product_name,
        warehouse=warehouse,
        shelf_number=shelf_number,
        column=column,
        level=level
    )

print("✅ 데이터 임포트 완료!")
