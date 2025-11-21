# WAY4 Confluence to mdls.json Conversion Guide

## Overview
Scripts để convert dữ liệu từ Confluence WAY4 documentation sang `mdls.json` format cho Qdrant embedding.

## Files

### 1. `convert_confluence_to_mdls.py`
Thư viện cơ bản với các hàm helper:
- `ConfluenceTableParser`: Parse HTML table từ Confluence
- `create_column_from_row()`: Convert hàng thành column definition
- `create_table_model()`: Tạo table model
- `load_mdls_json()` / `save_mdls_json()`: Load/save JSON

### 2. `fetch_and_convert_way4.py`
Script tự động fetch từ Confluence API:
- Kết nối Confluence API
- Parse HTML tables
- Extract column information
- Cần `CONFLUENCE_TOKEN` environment variable

### 3. `example_add_table.py`
Ví dụ cụ thể thêm bảng `way4_appl_product`

## Usage

### Method 1: Manual Addition (Recommended)
```python
import json
from datetime import datetime

# Load
with open('finx-engine/data/mdls.json', 'r') as f:
    mdls = json.load(f)

# Add table
table = {
    "name": "way4_table",
    "description": "Description",
    "type": "table",
    "columns": [...]
}

mdls["datasource-id"]["models"].append(table)

# Save
with open('finx-engine/data/mdls.json', 'w') as f:
    json.dump(mdls, f, indent=2, ensure_ascii=False)
```

### Method 2: Using Helper Functions
```python
from convert_confluence_to_mdls import *

mdls = load_mdls_json('finx-engine/data/mdls.json')
table = create_table_model('way4_table', 'Description', columns)
mdls = add_table_to_mdls(mdls, 'datasource-id', table)
save_mdls_json('finx-engine/data/mdls.json', mdls)
```

## mdls.json Format

```json
{
  "datasource-id": {
    "datasource_id": "...",
    "version": "1.0",
    "database": "...",
    "models": [
      {
        "name": "table_name",
        "description": "...",
        "type": "table",
        "business_domain": "...",
        "columns": [
          {
            "name": "column_name",
            "type": "STRING|DECIMAL|TIMESTAMP",
            "description": "...",
            "business_meaning": "...",
            "example": "...",
            "nullable": true,
            "primary_key": false,
            "foreign_key": false,
            "foreign_key_reference": null
          }
        ]
      }
    ],
    "relationships": [...]
  }
}
```

## Column Definition Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | ✓ | Column name (lowercase, underscore) |
| type | string | ✓ | Data type (STRING, DECIMAL, TIMESTAMP) |
| description | string | ✓ | Technical description |
| business_meaning | string | | Business meaning in Vietnamese |
| example | string | | Example value |
| nullable | boolean | | Can be null |
| primary_key | boolean | | Is primary key |
| foreign_key | boolean | | Is foreign key |
| foreign_key_reference | string | | Reference table.column |

## Confluence Page IDs

- way4_client: 739278868
- way4_acnt_contract: 740687936
- way4_appl_product: 748060673
- way4_card_info: 749535233
- way4_account: 749961217
- way4_doc: 749961284
- way4_m_transaction: 753565697

