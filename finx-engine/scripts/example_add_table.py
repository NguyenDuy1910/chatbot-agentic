#!/usr/bin/env python3
"""
Example script to add a new WAY4 table to mdls.json
"""

import json
from datetime import datetime

def add_way4_table_example():
    """Example: Add way4_appl_product table"""
    
    # Load existing mdls.json
    with open('finx-engine/data/mdls.json', 'r', encoding='utf-8') as f:
        mdls_data = json.load(f)
    
    datasource_id = "c23f11de-0ffb-40cb-a8f2-a173bf8450a7"
    
    # Define new table
    way4_appl_product = {
        "name": "way4_appl_product",
        "description": "Bảng lưu thông tin Sản phẩm - Sản phẩm là một đối tượng dùng để định nghĩa các dịch vụ tài chính được cung cấp.",
        "type": "table",
        "business_domain": "Product Management",
        "source_table": "way4_appl_product",
        "source_database": "non_prod_uat_bronze_zone",
        "columns": [
            {
                "name": "id",
                "type": "DECIMAL",
                "description": "Mã định danh duy nhất của sản phẩm",
                "business_meaning": "Mã sản phẩm",
                "example": "1",
                "nullable": False,
                "primary_key": True
            },
            {
                "name": "name",
                "type": "STRING",
                "description": "Tên sản phẩm",
                "business_meaning": "Tên sản phẩm",
                "example": "VISA DEBIT",
                "nullable": True
            },
            {
                "name": "code",
                "type": "STRING",
                "description": "Mã sản phẩm",
                "business_meaning": "Mã sản phẩm",
                "example": "VD001",
                "nullable": True
            },
            {
                "name": "product_group",
                "type": "STRING",
                "description": "Nhóm sản phẩm",
                "business_meaning": "Nhóm sản phẩm",
                "example": "CARD",
                "nullable": True
            },
            {
                "name": "is_active",
                "type": "STRING",
                "description": "Trạng thái hoạt động",
                "business_meaning": "Hoạt động (Y/N)",
                "example": "Y",
                "nullable": True
            }
        ],
        "primary_key": "id",
        "indexes": [],
        "constraints": []
    }
    
    # Add to models
    mdls_data[datasource_id]["models"].append(way4_appl_product)
    
    # Update metadata
    mdls_data[datasource_id]["metadata"]["total_models"] = len(
        mdls_data[datasource_id]["models"]
    )
    mdls_data[datasource_id]["generated_at"] = datetime.now().isoformat() + "Z"
    mdls_data[datasource_id]["metadata"]["generated_at"] = datetime.now().isoformat() + "Z"
    
    # Save back
    with open('finx-engine/data/mdls.json', 'w', encoding='utf-8') as f:
        json.dump(mdls_data, f, indent=2, ensure_ascii=False)
    
    print("✓ Table way4_appl_product added successfully!")
    print(f"  Total models: {mdls_data[datasource_id]['metadata']['total_models']}")

if __name__ == "__main__":
    add_way4_table_example()

