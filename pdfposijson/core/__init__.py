# core/__init__.py
from .jsonfix import normalize_fields, create_template, update_template_with_field, update_template_bbox_with_field, update_template_batch
from .getpdfcordi import extract_markers


__all__ = [
    "normalize_fields",
    "create_template",
    "update_template_with_field",
    "update_template_bbox_with_field",
    "update_template_batch",
    "extract_markers",
]