import json
import os
from datetime import datetime


def load_demo_data():
    path = os.path.join(os.path.dirname(__file__), "demo_data.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate(product_id: str):
    """
    Loads pre-verified compliance data for the given demo product.
    Returns a full report with checks, violations, and score.
    """
    data = load_demo_data()
    product = next((p for p in data["products"] if p["id"] == product_id), None)

    if not product:
        return {"error": "Product not found in demo set"}

    return {
        "product_id": product["id"],
        "product_name": product["name"],
        "score": product["score"],
        "overall": product["expected_verdict"],
        "verified_fields": product.get("verified_fields", {}),
        "checks": product.get("checks", []),
        "violations": product.get("violations", []),
        "notes": product.get("notes", ""),
        "image_url": product["image_url"],
    }