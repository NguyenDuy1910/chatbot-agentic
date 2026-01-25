#!/usr/bin/env python3
"""
Fetch WAY4 table documentation from Confluence and convert to mdls.json
"""

import json
import os
from typing import Dict, List, Any
from bs4 import BeautifulSoup
import requests
from datetime import datetime

# Confluence API configuration
CONFLUENCE_BASE_URL = "https://galaxyfinx.atlassian.net"
CONFLUENCE_API_URL = f"{CONFLUENCE_BASE_URL}/wiki/api/v2/pages"

# WAY4 table page IDs from Confluence
WAY4_PAGES = {
    "way4_client": {
        "page_id": "739278868",
        "business_domain": "Customer Management",
        "description": "Bảng lưu thông tin khách hàng (Client)"
    },
    "way4_acnt_contract": {
        "page_id": "740687936",
        "business_domain": "Contract Management",
        "description": "Bảng lưu thông tin Hợp đồng (Contract)"
    },
    "way4_appl_product": {
        "page_id": "748060673",
        "business_domain": "Product Management",
        "description": "Bảng lưu thông tin Sản phẩm (Product)"
    },
    "way4_card_info": {
        "page_id": "749535233",
        "business_domain": "Card Management",
        "description": "Bảng lưu thông tin Thẻ (Card)"
    },
    "way4_account": {
        "page_id": "749961217",
        "business_domain": "Account Management",
        "description": "Bảng lưu thông tin Tài khoản (Account)"
    },
    "way4_doc": {
        "page_id": "749961284",
        "business_domain": "Transaction Management",
        "description": "Bảng lưu thông tin Chứng từ (Document)"
    },
    "way4_m_transaction": {
        "page_id": "753565697",
        "business_domain": "Transaction Management",
        "description": "Bảng lưu thông tin Giao dịch vĩ mô (Macro Transaction)"
    }
}

def fetch_confluence_page(page_id: str, token: str) -> str:
    """Fetch page content from Confluence API"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    params = {
        "body-format": "storage"
    }
    
    url = f"{CONFLUENCE_API_URL}/{page_id}"
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    data = response.json()
    return data.get("body", {}).get("storage", {}).get("value", "")

def parse_table_from_html(html_content: str) -> List[List[str]]:
    """Parse HTML table and extract rows"""
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')
    
    rows = []
    for table in tables:
        for tr in table.find_all('tr'):
            cells = []
            for td in tr.find_all(['td', 'th']):
                # Extract text and clean up
                text = td.get_text(strip=True)
                cells.append(text)
            if cells:
                rows.append(cells)
    
    return rows

def create_column_from_row(row: List[str]) -> Dict[str, Any]:
    """Convert table row to column definition"""
    if len(row) < 2:
        return None
    
    column = {
        "name": row[0].lower().replace(" ", "_"),
        "type": row[1].upper() if len(row) > 1 else "STRING",
        "description": row[2] if len(row) > 2 else "",
        "nullable": True,
        "primary_key": False,
        "foreign_key": False,
        "foreign_key_reference": None
    }
    
    if len(row) > 3:
        column["business_meaning"] = row[3]
    if len(row) > 4:
        column["example"] = row[4]
    
    return {k: v for k, v in column.items() if v}

def main():
    """Main execution"""
    token = os.getenv("CONFLUENCE_TOKEN")
    if not token:
        print("Error: CONFLUENCE_TOKEN environment variable not set")
        return
    
    print("Fetching WAY4 tables from Confluence...")
    print("=" * 60)
    
    for table_name, config in WAY4_PAGES.items():
        print(f"\nProcessing: {table_name}")
        try:
            html = fetch_confluence_page(config["page_id"], token)
            rows = parse_table_from_html(html)
            print(f"  ✓ Found {len(rows)} rows")
        except Exception as e:
            print(f"  ✗ Error: {e}")

if __name__ == "__main__":
    main()

