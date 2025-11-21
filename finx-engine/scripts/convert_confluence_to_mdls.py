#!/usr/bin/env python3
"""
Script to convert Confluence WAY4 table documentation to mdls.json format
"""

import json
import re
from typing import Dict, List, Any
from html.parser import HTMLParser

class ConfluenceTableParser(HTMLParser):
    """Parse Confluence HTML table format"""
    
    def __init__(self):
        super().__init__()
        self.rows = []
        self.current_row = []
        self.in_table = False
        self.in_cell = False
        self.cell_content = ""
    
    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.in_table = True
        elif tag == "tr" and self.in_table:
            self.current_row = []
        elif tag in ["td", "th"] and self.in_table:
            self.in_cell = True
            self.cell_content = ""
    
    def handle_endtag(self, tag):
        if tag in ["td", "th"] and self.in_cell:
            self.in_cell = False
            self.current_row.append(self.cell_content.strip())
        elif tag == "tr" and self.in_table and self.current_row:
            self.rows.append(self.current_row)
        elif tag == "table":
            self.in_table = False
    
    def handle_data(self, data):
        if self.in_cell:
            self.cell_content += data

def create_column_from_row(row: List[str], table_name: str) -> Dict[str, Any]:
    """Convert a table row to column definition"""
    if len(row) < 3:
        return None
    
    column = {
        "name": row[0].lower().replace(" ", "_"),
        "type": row[1].upper() if len(row) > 1 else "STRING",
        "description": row[2] if len(row) > 2 else "",
        "business_meaning": row[3] if len(row) > 3 else "",
        "example": row[4] if len(row) > 4 else None,
        "nullable": True,
        "primary_key": False,
        "foreign_key": False,
        "foreign_key_reference": None
    }
    
    # Remove None values
    return {k: v for k, v in column.items() if v is not None}

def create_table_model(table_name: str, description: str, 
                       columns: List[Dict], business_domain: str = "") -> Dict[str, Any]:
    """Create a table model for mdls.json"""
    return {
        "name": table_name,
        "description": description,
        "type": "table",
        "business_domain": business_domain,
        "source_table": table_name,
        "source_database": "non_prod_uat_bronze_zone",
        "columns": columns,
        "primary_key": None,
        "indexes": [],
        "constraints": []
    }

def load_mdls_json(filepath: str) -> Dict[str, Any]:
    """Load existing mdls.json file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_mdls_json(filepath: str, data: Dict[str, Any]):
    """Save mdls.json file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def add_table_to_mdls(mdls_data: Dict, datasource_id: str, 
                      table_model: Dict[str, Any]) -> Dict:
    """Add a new table model to mdls.json"""
    if datasource_id not in mdls_data:
        mdls_data[datasource_id] = {
            "datasource_id": datasource_id,
            "version": "1.0",
            "database": "non_prod_uat_bronze_zone",
            "models": [],
            "relationships": [],
            "metadata": {}
        }
    
    mdls_data[datasource_id]["models"].append(table_model)
    mdls_data[datasource_id]["metadata"]["total_models"] = len(
        mdls_data[datasource_id]["models"]
    )
    
    return mdls_data

if __name__ == "__main__":
    print("WAY4 Confluence to mdls.json Converter")
    print("=" * 50)
    print("\nUsage example:")
    print("  from convert_confluence_to_mdls import *")
    print("  mdls = load_mdls_json('finx-engine/data/mdls.json')")
    print("  table = create_table_model('way4_table', 'Description', [])")
    print("  mdls = add_table_to_mdls(mdls, 'datasource-id', table)")
    print("  save_mdls_json('finx-engine/data/mdls.json', mdls)")

