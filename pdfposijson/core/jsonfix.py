# core/jsonfix.py

import json
from core.getpdfcordi import extract_markers
from typing import Optional, Dict, Any
from pathlib import Path
import os

def normalize_fields(raw_fields):
    fields = []
    for f in raw_fields.values():
        fields.append({
            "key": str(f["key"]),
            "placeholderbbox": f["placeholderbbox"]
        })

    return fields

def create_template(pdf_path, output_json):
    doc, raw_fields = extract_markers(pdf_path)
    
    template = {
        "template_name": output_json.replace(".json:", ""),
        "pdf_info": {
            "page_size": list(doc[0].rect)[2:],
            "num_pages": len(doc)
        },
        "fields": normalize_fields(raw_fields)
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)

    print(f"✅ 模板已生成: {output_json}")

    return True

def update_template_with_field(json_file, field_name):
    with open(json_file, "r", encoding="utf-8") as f:
        template = json.load(f)

    if "fields" not in template:
        raise ValueError("模板 JSON 必须包含 'fields' 字段")
    
    for f in template["fields"]:
        if f["key"] == field_name["key"] or f["placeholderbbox"] == field_name["placeholderbbox"]:
            print(f'already exists: {field_name["key"]} or {field_name["placeholderbbox"]}')
            return
    
    template["fields"].append(field_name)

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
def update_template_bbox_with_field(json_file, field_key, new_bbox):
    with open(json_file, "r", encoding="utf-8") as f:
        template = json.load(f)

    if "fields" not in template:
        raise ValueError("模板 JSON 必须包含 'fields' 字段")
    
    for f in template["fields"]:
        if f["key"] == field_key:
            f["placeholderbbox"] = new_bbox
            print(f"updated {field_key} bbox to {new_bbox}")
        else:
            print(f"field_key {field_key} not found in template")
        
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)

def update_template_batch(json_file, fields):

    with open(json_file,"r", encoding="utf-8") as f:
        template = json.load(f)

    if "fields" not in template:
        raise ValueError("模板 JSON 必须包含 'fields' 字段")
    
    existing_keys = {f["key"] for f in template["fields"]}

    for field in fields:
        if field["key"] in existing_keys:
            print(f"already exists: {field['key']}")
            continue
        template["fields"].append(field)
        print(f"added field: {field['key']}")
    
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)

def load_template(name: str) -> Dict[str, any]:
    BASE_DIR = Path(__file__).resolve().parent
    CONFIG_DIR = BASE_DIR.parent / "config"

    path = os.path.join(CONFIG_DIR, f"{name}.json")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_template(name: str, data):
    BASE_DIR = Path(__file__).resolve().parent
    CONFIG_DIR = BASE_DIR.parent / "config"

    path = CONFIG_DIR / f"{name}.json"

    tmp_path = CONFIG_DIR / f"{name}.json.tmp"

    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        os.replace(tmp_path, path)

    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except:
                pass   