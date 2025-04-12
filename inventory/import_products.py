import pandas as pd
from inventory.models import Product

# 엑셀 파일 경로
file_path = 'products.xlsx'

# pandas를 사용하여 엑셀 파일 읽기
df = pd.read_excel(file_path)

# 데이터를 순회하면서 처리
for index, row in df.iterrows():
    product_name, warehouse, shelf_number, column, level = row

    # 저장 (같은 제품명이 여러 위치에 존재할 수 있으므로 unique 제약 없음)
    Product.objects.create(
        product_name=str(product_name).strip(),
        warehouse=str(warehouse).strip(),
        shelf_number=str(shelf_number).strip().zfill(2),  # 선반 번호 두자리로 맞춤
        column=str(column).strip(),
        level=int(level)
    )

print("✅ 데이터 임포트 완료!")
