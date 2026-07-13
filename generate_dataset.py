#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import csv
import random
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


ROW_COUNT = 2000
REQUIRED_COLUMNS = [
    "id",
    "product_name",
    "brand",
    "category",
    "skin_type",
    "key_ingredients",
    "benefits",
    "size_ml",
    "price_idr",
    "rating",
    "review_count",
    "image_url",
    "description",
]

BRANDS = [
    {"name": "Wardah", "price_multiplier": 0.85, "review_multiplier": 1.25},
    {"name": "Somethinc", "price_multiplier": 1.0, "review_multiplier": 1.2},
    {"name": "Skintific", "price_multiplier": 1.0, "review_multiplier": 1.15},
    {"name": "Avoskin", "price_multiplier": 1.05, "review_multiplier": 1.1},
    {"name": "Emina", "price_multiplier": 0.72, "review_multiplier": 1.1},
    {"name": "Azarine", "price_multiplier": 0.88, "review_multiplier": 1.15},
    {"name": "Cetaphil", "price_multiplier": 1.1, "review_multiplier": 1.05},
    {"name": "CeraVe", "price_multiplier": 1.15, "review_multiplier": 1.05},
    {"name": "The Ordinary", "price_multiplier": 1.05, "review_multiplier": 1.0},
    {"name": "La Roche-Posay", "price_multiplier": 1.3, "review_multiplier": 0.95},
    {"name": "Cosrx", "price_multiplier": 1.05, "review_multiplier": 1.0},
    {"name": "Innisfree", "price_multiplier": 1.08, "review_multiplier": 0.92},
    {"name": "Bioderma", "price_multiplier": 1.18, "review_multiplier": 0.9},
    {"name": "Safi", "price_multiplier": 0.78, "review_multiplier": 0.85},
    {"name": "Garnier", "price_multiplier": 0.82, "review_multiplier": 1.25},
    {"name": "L'Oreal Paris", "price_multiplier": 0.98, "review_multiplier": 1.08},
    {"name": "Nivea", "price_multiplier": 0.8, "review_multiplier": 1.15},
    {"name": "Kiehl's", "price_multiplier": 1.55, "review_multiplier": 0.78},
    {"name": "Clinique", "price_multiplier": 1.48, "review_multiplier": 0.82},
    {"name": "Hada Labo", "price_multiplier": 0.87, "review_multiplier": 1.1},
    {"name": "Pyunkang Yul", "price_multiplier": 1.06, "review_multiplier": 0.72},
    {"name": "Neutrogena", "price_multiplier": 0.95, "review_multiplier": 1.0},
    {"name": "Nature Republic", "price_multiplier": 0.92, "review_multiplier": 0.76},
    {"name": "Bio Beauty Lab", "price_multiplier": 0.9, "review_multiplier": 0.66},
    {"name": "Sukin", "price_multiplier": 1.1, "review_multiplier": 0.68},
]

CATEGORIES = {
    "Cleanser": {
        "sizes": [50, 80, 100, 120, 150, 200],
        "base_price": 70000,
        "terms": ["Foaming Cleanser", "Gentle Wash", "Gel Cleanser", "Cream Cleanser"],
        "description": "cleanses daily buildup without leaving skin tight",
    },
    "Toner": {
        "sizes": [50, 100, 120, 150, 180, 200],
        "base_price": 90000,
        "terms": ["Hydrating Toner", "Balancing Toner", "Prep Toner", "Soothing Toner"],
        "description": "refreshes skin and helps the next steps absorb comfortably",
    },
    "Serum": {
        "sizes": [15, 20, 30, 40, 50],
        "base_price": 130000,
        "terms": ["Daily Serum", "Booster Serum", "Concentrate", "Ampoule Serum"],
        "description": "delivers targeted care with a lightweight fast-absorbing texture",
    },
    "Moisturizer": {
        "sizes": [15, 20, 30, 50, 75, 100],
        "base_price": 120000,
        "terms": ["Gel Moisturizer", "Barrier Cream", "Daily Moisturizer", "Water Cream"],
        "description": "locks in hydration while keeping skin comfortable throughout the day",
    },
    "Sunscreen": {
        "sizes": [15, 30, 40, 50, 60, 80],
        "base_price": 110000,
        "terms": ["UV Shield", "Sun Fluid", "Daily Sunscreen", "Protection Gel"],
        "description": "helps protect skin from UV exposure with a wearable finish",
    },
    "Face Mask": {
        "sizes": [20, 25, 50, 75, 100, 120, 150],
        "base_price": 85000,
        "terms": ["Sleeping Mask", "Clay Mask", "Recovery Mask", "Glow Mask"],
        "description": "gives skin an intensive treatment boost when it feels tired",
    },
    "Exfoliator": {
        "sizes": [20, 30, 50, 75, 100, 120],
        "base_price": 125000,
        "terms": ["Resurfacing Exfoliator", "Peeling Solution", "Daily Peel", "Exfoliating Essence"],
        "description": "smooths rough texture and helps refine the look of pores",
    },
    "Eye Cream": {
        "sizes": [10, 15, 20, 25, 30],
        "base_price": 145000,
        "terms": ["Eye Cream", "Eye Gel", "Bright Eye Treatment", "Eye Recovery Balm"],
        "description": "nourishes the delicate eye area with a comfortable finish",
    },
    "Essence": {
        "sizes": [30, 50, 80, 100, 120, 150],
        "base_price": 115000,
        "terms": ["Treatment Essence", "Hydra Essence", "Ferment Essence", "Glow Essence"],
        "description": "adds a soft layer of hydration while improving skin balance",
    },
    "Facial Oil": {
        "sizes": [15, 20, 30, 40, 50],
        "base_price": 150000,
        "terms": ["Facial Oil", "Nourishing Oil", "Recovery Oil", "Glow Oil"],
        "description": "seals in moisture and leaves skin looking supple and smooth",
    },
}

BENEFIT_PROFILES = [
    {
        "name": "Hydrating",
        "ingredients": ["Hyaluronic Acid", "Ceramide", "Squalane", "Panthenol", "Glycerin", "Betaine"],
        "lines": ["Hydra", "Aqua", "Moist", "Dew", "Water", "Plump"],
        "adjectives": ["Fresh", "Deep", "Daily", "Soft", "Cloud", "Pure"],
    },
    {
        "name": "Brightening",
        "ingredients": ["Vitamin C", "Niacinamide", "Alpha Arbutin", "Tranexamic Acid", "Licorice Root", "Glutathione"],
        "lines": ["Glow", "Radiance", "Lumi", "Bright", "Aura", "Tone"],
        "adjectives": ["Clear", "Daily", "Even", "Dewy", "Crystal", "Vital"],
    },
    {
        "name": "Anti-acne",
        "ingredients": ["Salicylic Acid", "Niacinamide", "Centella Asiatica", "Tea Tree", "Sulfur", "AHA/BHA"],
        "lines": ["Clear", "Acne", "Pore", "Blemish", "Pure", "Balance"],
        "adjectives": ["Rapid", "Fresh", "Targeted", "Oil-Free", "Gentle", "Active"],
    },
    {
        "name": "Anti-aging",
        "ingredients": ["Retinol", "Peptides", "Ceramide", "Bakuchiol", "Coenzyme Q10", "Collagen"],
        "lines": ["Renew", "Lift", "Age", "Youth", "Firm", "Revive"],
        "adjectives": ["Overnight", "Advanced", "Smooth", "Elastic", "Repair", "Pro"],
    },
    {
        "name": "Soothing",
        "ingredients": ["Centella Asiatica", "Aloe Vera", "Panthenol", "Allantoin", "Madecassoside", "Mugwort"],
        "lines": ["Cica", "Calm", "Relief", "Derma", "Rescue", "Comfort"],
        "adjectives": ["Soft", "Cool", "Gentle", "Daily", "Barrier", "Comfort"],
    },
    {
        "name": "Oil control",
        "ingredients": ["Niacinamide", "Zinc PCA", "Green Tea", "Salicylic Acid", "Charcoal", "Witch Hazel"],
        "lines": ["Balance", "Matte", "Sebum", "Fresh", "Pore", "Control"],
        "adjectives": ["Light", "Fresh", "Daily", "Zero Shine", "Refining", "Stay-Matte"],
    },
]

SKIN_TYPES = ["Oily", "Dry", "Combination", "Sensitive", "Normal", "All"]
EXTRA_INGREDIENTS = ["Ceramide", "Hyaluronic Acid", "Centella Asiatica", "Niacinamide", "Peptides", "Vitamin E"]
DESCRIPTORS = ["Essentials", "Lab", "Daily", "Expert", "Skin", "Solution", "Care", "Repair", "Boost", "Shield"]


def weighted_choice(items: list[dict], rng: random.Random) -> dict:
    index = rng.randrange(len(items))
    return items[index]


def choose_category(row_index: int) -> str:
    category_names = list(CATEGORIES)
    category_index = (row_index + 2 * (row_index // len(BRANDS))) % len(category_names)
    return category_names[category_index]


def create_product_name(
    category: str,
    primary_profile: dict,
    secondary_profile: dict | None,
    rng: random.Random,
) -> str:
    line = rng.choice(primary_profile["lines"])
    adjective = rng.choice(primary_profile["adjectives"])
    descriptor = rng.choice(DESCRIPTORS)
    term = rng.choice(CATEGORIES[category]["terms"])
    if secondary_profile and rng.random() < 0.45:
        secondary_line = rng.choice(secondary_profile["lines"])
        return f"{line} {secondary_line} {adjective} {term}"
    if rng.random() < 0.35:
        return f"{line} {adjective} {descriptor} {term}"
    return f"{line} {adjective} {term}"


def choose_secondary_profile(primary_profile: dict, rng: random.Random) -> dict | None:
    if rng.random() < 0.52:
        candidates = [profile for profile in BENEFIT_PROFILES if profile["name"] != primary_profile["name"]]
        return rng.choice(candidates)
    return None


def choose_skin_type(primary_benefit: str, category: str, rng: random.Random) -> str:
    if category == "Sunscreen":
        return rng.choice(["All", "Combination", "Sensitive", "Normal"])
    if primary_benefit == "Anti-acne" or primary_benefit == "Oil control":
        return rng.choice(["Oily", "Combination", "All"])
    if primary_benefit == "Hydrating":
        return rng.choice(["Dry", "Normal", "Combination", "All"])
    if primary_benefit == "Soothing":
        return rng.choice(["Sensitive", "All", "Dry"])
    if primary_benefit == "Anti-aging":
        return rng.choice(["Dry", "Normal", "Combination", "All"])
    return rng.choice(SKIN_TYPES)


def choose_ingredients(
    primary_profile: dict,
    secondary_profile: dict | None,
    category: str,
    rng: random.Random,
) -> str:
    pool = list(primary_profile["ingredients"])
    if secondary_profile:
        pool.extend(secondary_profile["ingredients"][:3])
    if category in {"Moisturizer", "Essence", "Eye Cream"}:
        pool.extend(["Ceramide", "Hyaluronic Acid", "Panthenol"])
    if category == "Sunscreen":
        pool.extend(["Niacinamide", "Centella Asiatica", "Vitamin E"])
    if category == "Exfoliator":
        pool.extend(["AHA/BHA", "Lactic Acid", "Mandelic Acid"])
    if category == "Facial Oil":
        pool.extend(["Squalane", "Jojoba Oil", "Rosehip Oil"])
    unique_pool = list(dict.fromkeys(pool))
    selected = rng.sample(unique_pool, k=4 if len(unique_pool) >= 4 else len(unique_pool))
    return ", ".join(selected)


def choose_benefits(primary_profile: dict, secondary_profile: dict | None, rng: random.Random) -> str:
    names = [primary_profile["name"]]
    if secondary_profile and secondary_profile["name"] not in names:
        names.append(secondary_profile["name"])
    if len(names) == 1 and rng.random() < 0.3:
        extra = rng.choice([profile["name"] for profile in BENEFIT_PROFILES if profile["name"] not in names])
        names.append(extra)
    return ", ".join(names)


def choose_size(category: str, rng: random.Random) -> int:
    return rng.choice(CATEGORIES[category]["sizes"])


def calculate_price(category: str, brand: dict, size_ml: int, rng: random.Random) -> int:
    base = CATEGORIES[category]["base_price"]
    size_factor = 0.82 + (size_ml / max(CATEGORIES[category]["sizes"])) * 0.45
    raw_price = base * brand["price_multiplier"] * size_factor * rng.uniform(0.9, 1.12)
    rounded = int(round(raw_price / 1000) * 1000)
    return max(25000, rounded)


def calculate_rating(brand: dict, primary_benefit: str, rng: random.Random) -> float:
    benefit_bonus = {
        "Hydrating": 0.15,
        "Brightening": 0.1,
        "Anti-acne": 0.05,
        "Anti-aging": 0.08,
        "Soothing": 0.16,
        "Oil control": 0.06,
    }
    rating = 3.7 + brand["price_multiplier"] * 0.35 + benefit_bonus[primary_benefit] + rng.uniform(-0.35, 0.38)
    return round(min(5.0, max(1.0, rating)), 1)


def calculate_review_count(brand: dict, category: str, rating: float, row_id: int, rng: random.Random) -> int:
    category_factor = {
        "Cleanser": 1.25,
        "Toner": 0.9,
        "Serum": 1.2,
        "Moisturizer": 1.05,
        "Sunscreen": 1.35,
        "Face Mask": 0.7,
        "Exfoliator": 0.66,
        "Eye Cream": 0.45,
        "Essence": 0.58,
        "Facial Oil": 0.4,
    }[category]
    base = 55 + int(row_id * 1.7 * brand["review_multiplier"] * category_factor)
    adjustment = int((rating - 3.5) * 180 + rng.uniform(0, 420))
    return max(8, base + adjustment)


def create_description(
    skin_type: str,
    primary_profile: dict,
    secondary_profile: dict | None,
    category: str,
) -> str:
    skin_label = "all skin types" if skin_type == "All" else f"{skin_type.lower()} skin"
    benefit_text = primary_profile["name"].lower()
    follow_up = f" and {secondary_profile['name'].lower()}" if secondary_profile else ""
    return (
        f"A {category.lower()} for {skin_label} that supports {benefit_text}"
        f"{follow_up} care and {CATEGORIES[category]['description']}."
    )


def create_image_url(row_id: int) -> str:
    color_a = f"{(row_id * 37) % 256:02x}{(row_id * 53) % 256:02x}{(row_id * 71) % 256:02x}"
    color_b = f"{(row_id * 19) % 256:02x}{(row_id * 29) % 256:02x}{(row_id * 41) % 256:02x}"
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='400' height='400' viewBox='0 0 400 400'>"
        f"<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'><stop offset='0%' stop-color='#{color_a}'/>"
        f"<stop offset='100%' stop-color='#{color_b}'/></linearGradient></defs>"
        "<rect width='400' height='400' rx='36' fill='url(#g)'/>"
        "<text x='200' y='185' text-anchor='middle' font-family='Arial, sans-serif' font-size='34' fill='white'>Skincare</text>"
        f"<text x='200' y='230' text-anchor='middle' font-family='Arial, sans-serif' font-size='28' fill='white'>#{row_id:04d}</text>"
        "</svg>"
    )
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def build_rows() -> list[dict[str, object]]:
    rng = random.Random(20260713)
    rows: list[dict[str, object]] = []
    used_names: dict[tuple[str, str], int] = {}

    for row_id in range(1, ROW_COUNT + 1):
        brand = BRANDS[(row_id - 1) % len(BRANDS)]
        category = choose_category(row_id - 1)
        primary_profile = BENEFIT_PROFILES[(row_id - 1) % len(BENEFIT_PROFILES)]
        secondary_profile = choose_secondary_profile(primary_profile, rng)
        skin_type = choose_skin_type(primary_profile["name"], category, rng)
        product_name = create_product_name(category, primary_profile, secondary_profile, rng)
        key = (brand["name"], product_name)
        used_names[key] = used_names.get(key, 0) + 1
        if used_names[key] > 1:
            product_name = f"{product_name} {used_names[key]}"

        size_ml = choose_size(category, rng)
        price_idr = calculate_price(category, brand, size_ml, rng)
        rating = calculate_rating(brand, primary_profile["name"], rng)
        review_count = calculate_review_count(brand, category, rating, row_id, rng)

        rows.append(
            {
                "id": row_id,
                "product_name": product_name,
                "brand": brand["name"],
                "category": category,
                "skin_type": skin_type,
                "key_ingredients": choose_ingredients(primary_profile, secondary_profile, category, rng),
                "benefits": choose_benefits(primary_profile, secondary_profile, rng),
                "size_ml": size_ml,
                "price_idr": price_idr,
                "rating": f"{rating:.1f}",
                "review_count": review_count,
                "image_url": create_image_url(row_id),
                "description": create_description(skin_type, primary_profile, secondary_profile, category),
            }
        )
    return rows


def validate_rows(rows: list[dict[str, object]]) -> None:
    if len(rows) != ROW_COUNT:
        raise ValueError(f"Expected {ROW_COUNT} rows, found {len(rows)}")

    ids = [row["id"] for row in rows]
    if ids != list(range(1, ROW_COUNT + 1)):
        raise ValueError("IDs must be unique integers from 1 to 2000")

    for row in rows:
        for column in REQUIRED_COLUMNS:
            value = row[column]
            if value is None or str(value).strip() == "":
                raise ValueError(f"Required column '{column}' is empty for id={row['id']}")


def write_csv(rows: list[dict[str, object]], output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=REQUIRED_COLUMNS, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)


def validate_csv_with_stdlib(output_path: Path) -> None:
    with output_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        parsed_rows = list(reader)

    if len(parsed_rows) != ROW_COUNT:
        raise ValueError(f"CSV must contain {ROW_COUNT} data rows, found {len(parsed_rows)}")

    ids = [int(row["id"]) for row in parsed_rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate IDs found in CSV")

    for row in parsed_rows:
        for column in REQUIRED_COLUMNS:
            if row[column].strip() == "":
                raise ValueError(f"CSV contains empty required field '{column}' for id={row['id']}")


def validate_csv_with_pandas(output_path: Path) -> None:
    try:
        import pandas as pd
    except ModuleNotFoundError:
        print("pandas is not installed; skipping pandas validation.")
        return

    dataframe = pd.read_csv(output_path)
    if len(dataframe.index) != ROW_COUNT:
        raise ValueError(f"pandas parsed {len(dataframe.index)} rows instead of {ROW_COUNT}")
    if dataframe["id"].nunique() != ROW_COUNT:
        raise ValueError("pandas detected duplicate IDs")
    if dataframe[REQUIRED_COLUMNS].isnull().any().any():
        raise ValueError("pandas detected empty required fields")


def check_image_url(url: str, timeout: int = 10) -> tuple[str, bool, str]:
    if url.startswith("data:image/"):
        try:
            header, payload = url.split(",", 1)
            if ";base64" in header:
                decoded = base64.b64decode(payload, validate=True)
            else:
                decoded = urllib.parse.unquote_to_bytes(payload)
            if not decoded.strip():
                return url, False, "empty data URL payload"
            return url, True, header
        except (ValueError, base64.binascii.Error) as error:
            return url, False, str(error)

    request = urllib.request.Request(url, headers={"User-Agent": "DatasetSkincare2000/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            content_type = response.headers.get("Content-Type", "")
            response.read(1)
            if response.status != 200 or not content_type.startswith("image/"):
                return url, False, f"status={response.status}, content_type={content_type}"
            return url, True, content_type
    except urllib.error.URLError as error:
        return url, False, str(error)


def validate_image_urls(rows: list[dict[str, object]], max_workers: int) -> None:
    urls = [row["image_url"] for row in rows]
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(check_image_url, urls))

    failures = [result for result in results if not result[1]]
    if failures:
        sample = "; ".join(f"{url} -> {message}" for url, _, message in failures[:5])
        raise ValueError(f"{len(failures)} image URLs failed validation: {sample}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a 2000-row skincare product dataset.")
    parser.add_argument(
        "--output",
        default="skincare_dataset_2000.csv",
        help="Path to the output CSV file.",
    )
    parser.add_argument(
        "--validate-urls",
        action="store_true",
        help="Validate that each image URL resolves to an image response.",
    )
    parser.add_argument(
        "--url-workers",
        type=int,
        default=24,
        help="Number of worker threads used for image URL validation.",
    )
    args = parser.parse_args()

    output_path = Path(args.output).resolve()
    rows = build_rows()
    validate_rows(rows)
    write_csv(rows, output_path)
    validate_csv_with_stdlib(output_path)
    validate_csv_with_pandas(output_path)

    if args.validate_urls:
        validate_image_urls(rows, max_workers=max(1, args.url_workers))

    print(f"Generated {ROW_COUNT} skincare product rows at {output_path}")


if __name__ == "__main__":
    main()
