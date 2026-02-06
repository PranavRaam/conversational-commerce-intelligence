import json
import sys

# -----------------------------
# Controlled vocabularies
# -----------------------------

ALLOWED_FITS = {"slim", "regular", "relaxed", "oversized", "one_size"}

ALLOWED_CATEGORIES = {
    "hoodies",
    "jackets",
    "t_shirts",
    "pants",
    "accessories"
}

ALLOWED_USE_CASES = {
    "winter_wear",
    "rain_protection",
    "daily_casual",
    "outdoor",
    "travel",
    "wind_protection"
}

RAIN_FEATURES = {"waterproof", "water resistant", "sealed seams"}
WINTER_FEATURES = {"fleece", "thermal", "down", "warm"}

REQUIRED_FIELDS = {
    "product_id",
    "name",
    "category",
    "price",
    "description",
    "fit",
    "sizes",
    "use_case",
    "key_features",
    "material"
}


# -----------------------------
# Validation helpers
# -----------------------------

def error(msg):
    return f"❌ {msg}"


def validate_product(product, index):
    errors = []

    # ---- Required fields ----
    missing = REQUIRED_FIELDS - product.keys()
    if missing:
        errors.append(error(f"Product {index}: missing fields {missing}"))

    # ---- Type checks ----
    if not isinstance(product.get("price"), int):
        errors.append(error(f"{product.get('product_id')}: price must be integer"))

    if not isinstance(product.get("sizes"), list) or not product["sizes"]:
        errors.append(error(f"{product.get('product_id')}: sizes must be non-empty list"))

    if not isinstance(product.get("use_case"), list) or not product["use_case"]:
        errors.append(error(f"{product.get('product_id')}: use_case must be non-empty list"))

    if not isinstance(product.get("key_features"), list) or not product["key_features"]:
        errors.append(error(f"{product.get('product_id')}: key_features must be non-empty list"))

    # ---- Controlled vocabularies ----
    if product.get("fit") not in ALLOWED_FITS:
        errors.append(error(f"{product.get('product_id')}: invalid fit '{product.get('fit')}'"))

    if product.get("category") not in ALLOWED_CATEGORIES:
        errors.append(error(f"{product.get('product_id')}: invalid category '{product.get('category')}'"))

    for uc in product.get("use_case", []):
        if uc not in ALLOWED_USE_CASES:
            errors.append(error(f"{product.get('product_id')}: invalid use_case '{uc}'"))

    # ---- Fit ↔ size logic ----
    if product.get("fit") == "one_size":
        if product.get("sizes") != ["one_size"]:
            errors.append(error(f"{product.get('product_id')}: one_size fit must have sizes ['one_size']"))

    if product.get("category") == "accessories":
        if product.get("fit") != "one_size":
            errors.append(error(f"{product.get('product_id')}: accessories must have fit='one_size'"))

    # ---- Use case ↔ feature consistency ----
    features = set(f.lower() for f in product.get("key_features", []))

    if "rain_protection" in product.get("use_case", []):
        if not features & RAIN_FEATURES:
            errors.append(error(f"{product.get('product_id')}: rain_protection without waterproof features"))

    if "winter_wear" in product.get("use_case", []):
        if not any(w in " ".join(features) for w in WINTER_FEATURES):
            errors.append(error(f"{product.get('product_id')}: winter_wear without insulation features"))

    # ---- Description sanity ----
    if len(product.get("description", "").split()) < 5:
        errors.append(error(f"{product.get('product_id')}: description too short"))

    return errors


def validate_price_logic(products):
    errors = []
    by_category = {}

    for p in products:
        by_category.setdefault(p["category"], []).append(p)

    for category, items in by_category.items():
        sorted_items = sorted(items, key=lambda x: x["price"])
        for i in range(1, len(sorted_items)):
            cheaper = sorted_items[i - 1]
            expensive = sorted_items[i]

            if len(expensive["key_features"]) < len(cheaper["key_features"]):
                errors.append(
                    error(
                        f"{expensive['product_id']} priced higher than "
                        f"{cheaper['product_id']} but has fewer features"
                    )
                )

    return errors


# -----------------------------
# Main runner
# -----------------------------

def main(path):
    with open(path, "r") as f:
        data = json.load(f)

    products = data.get("products", [])
    all_errors = []

    for idx, product in enumerate(products, start=1):
        all_errors.extend(validate_product(product, idx))

    all_errors.extend(validate_price_logic(products))

    if all_errors:
        print("\n".join(all_errors))
        print("\n❌ Catalog validation FAILED")
        sys.exit(1)
    else:
        print("✅ Catalog validation PASSED")
        print("Catalog is safe to use as grounding data.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_catalog.py path/to/products.json")
        sys.exit(1)

    main(sys.argv[1])
