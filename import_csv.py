import pandas as pd
from inventory.models import Product

def import_data():
    # 엑셀 파일 경로 (파일 이름에 따라 경로 수정)
    file_path = 'products.csv'

    # pandas로 CSV 파일 읽기
    df = pd.read_csv(file_path)

    # 데이터 순차 처리 후 저장
    for index, row in df.iterrows():
        product_name, warehouse, shelf_number, column, level = row

        # Product 데이터베이스에 저장
        Product.objects.create(
            product_name=str(product_name).strip(),
            warehouse=str(warehouse).strip(),
            shelf_number=str(shelf_number).strip().zfill(2),  # 두자리로 맞추기
            column=str(column).strip(),
            level=int(level)
        )

    print("✅ CSV 데이터 임포트 완료!")

# 실제로 스크립트 실행
import_data()
