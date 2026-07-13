#!/usr/bin/env python3
"""Generate a realistic skincare dataset CSV."""

from __future__ import annotations

import argparse
import csv
import random
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

COLUMNS = [
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
    "Wardah",
    "Somethinc",
    "Skintific",
    "Avoskin",
    "Emina",
    "Azarine",
    "Cetaphil",
    "CeraVe",
    "The Ordinary",
    "La Roche-Posay",
    "Cosrx",
    "Innisfree",
    "Scarlett",
    "Bioderma",
    "Garnier",
    "Olay",
    "Neutrogena",
    "Nivea",
    "L'Oreal Paris",
    "Kiehl's",
    "Clinique",
    "Vaseline",
    "Bioaqua",
    "Pyunkang Yul",
    "Hada Labo",
    "Safi",
    "Erha",
    "Elsheskin",
]

CATEGORIES = [
    "Cleanser",
    "Toner",
    "Serum",
    "Moisturizer",
    "Sunscreen",
    "Face Mask",
    "Exfoliator",
    "Eye Cream",
    "Essence",
    "Facial Oil",
]

SKIN_TYPES = ["Oily", "Dry", "Combination", "Sensitive", "Normal", "All"]

INGREDIENTS = [
    "Niacinamide",
    "Hyaluronic Acid",
    "Salicylic Acid",
    "Retinol",
    "Vitamin C",
    "Centella Asiatica",
    "Ceramide",
    "AHA/BHA",
    "Panthenol",
    "Green Tea",
    "Squalane",
    "Tranexamic Acid",
    "Peptide",
    "Allantoin",
]

BENEFITS = [
    "Hydrating",
    "Brightening",
    "Anti-acne",
    "Anti-aging",
    "Soothing",
    "Oil control",
    "Barrier repair",
    "Pore care",
]

LINE_WORDS = [
    "Daily",
    "Advanced",
    "Hydra",
    "Calm",
    "Pure",
    "Radiance",
    "Balance",
    "Renew",
    "Glow",
    "Ultra",
    "Gentle",
    "Pro",
]

CATEGORY_TERMS = {
    "Cleanser": ["Facial Wash", "Foam Cleanser", "Gel Cleanser", "Cream Cleanser"],
    "Toner": ["Balancing Toner", "Hydrating Toner", "Daily Toner", "Soothing Toner"],
    "Serum": ["Face Serum", "Treatment Serum", "Concentrate Serum", "Booster Serum"],
    "Moisturizer": ["Moisturizing Cream", "Gel Moisturizer", "Barrier Cream", "Hydra Cream"],
    "Sunscreen": ["UV Shield", "Sun Fluid", "Sunscreen Gel", "Sun Protector"],
    "Face Mask": ["Sleeping Mask", "Clay Mask", "Hydro Mask", "Soothing Mask"],
    "Exfoliator": ["Peeling Solution", "Exfoliating Toner", "Resurfacing Serum", "Gentle Exfoliator"],
    "Eye Cream": ["Eye Treatment", "Bright Eye Cream", "Firming Eye Cream", "Revive Eye Balm"],
    "Essence": ["Hydrating Essence", "Brightening Essence", "Skin Essence", "Repair Essence"],
    "Facial Oil": ["Nourishing Oil", "Face Oil", "Repair Oil", "Glow Oil"],
}

SIZE_OPTIONS = {
    "Cleanser": [50, 80, 100, 120, 150, 200],
    "Toner": [60, 80, 100, 120, 150, 200],
    "Serum": [15, 20, 30, 40, 50],
    "Moisturizer": [20, 30, 40, 50, 60, 80],
    "Sunscreen": [30, 35, 40, 50, 60, 70],
    "Face Mask": [30, 50, 75, 80, 100, 120],
    "Exfoliator": [20, 30, 50, 60, 80, 100],
    "Eye Cream": [10, 15, 20, 25, 30],
    "Essence": [30, 50, 60, 80, 100, 120],
    "Facial Oil": [15, 20, 30, 35, 40, 50],
}

BASE_PRICE_RANGE = {
    "Cleanser": (35000, 220000),
    "Toner": (45000, 280000),
    "Serum": (70000, 450000),
    "Moisturizer": (50000, 350000),
    "Sunscreen": (50000, 300000),
    "Face Mask": (30000, 240000),
    "Exfoliator": (60000, 420000),
    "Eye Cream": (70000, 480000),
    "Essence": (70000, 400000),
    "Facial Oil": (80000, 500000),
}

PREMIUM_BRANDS = {
    "La Roche-Posay",
    "Kiehl's",
    "Clinique",
    "The Ordinary",
    "CeraVe",
    "Bioderma",
}

GITHUB_TOPIC_NAMES = [
    "javascript",
    "react",
    "vue",
    "angular",
    "nodejs",
    "python",
    "java",
    "go",
    "ruby",
    "php",
    "swift",
    "kotlin",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "linux",
    "mongodb",
    "postgresql",
]


@dataclass
class Product:
    id: int
    product_name: str
    brand: str
    category: str
    skin_type: str
    key_ingredients: str
    benefits: str
    size_ml: int
    price_idr: int
    rating: str
    review_count: int
    image_url: str
    description: str

    def to_row(self) -> dict[str, str | int]:
        return {
            "id": self.id,
            "product_name": self.product_name,
            "brand": self.brand,
            "category": self.category,
            "skin_type": self.skin_type,
            "key_ingredients": self.key_ingredients,
            "benefits": self.benefits,
            "size_ml": self.size_ml,
            "price_idr": self.price_idr,
            "rating": self.rating,
            "review_count": self.review_count,
            "image_url": self.image_url,
            "description": self.description,
        }


def build_product_name(brand: str, category: str, ingredients: list[str], randomizer: random.Random) -> str:
    line = randomizer.choice(LINE_WORDS)
    term = randomizer.choice(CATEGORY_TERMS[category])
    hero = ingredients[0]
    return f"{brand} {line} {hero} {term}"


def pick_skin_type(category: str, randomizer: random.Random) -> str:
    if category in {"Cleanser", "Sunscreen", "Moisturizer"} and randomizer.random() < 0.3:
        return "All"
    return randomizer.choice(SKIN_TYPES)


def pick_price(category: str, brand: str, randomizer: random.Random) -> int:
    low, high = BASE_PRICE_RANGE[category]
    if brand in PREMIUM_BRANDS:
        low = int(low * 1.25)
        high = int(high * 1.45)
    raw = randomizer.randint(low, high)
    return int(round(raw / 1000) * 1000)


def pick_review_count(randomizer: random.Random) -> int:
    return randomizer.randint(25, 50000)


def pick_rating(randomizer: random.Random) -> str:
    rating = randomizer.uniform(3.6, 5.0)
    return f"{round(rating, 1):.1f}"


def create_description(category: str, skin_type: str, ingredients: list[str], benefits: list[str]) -> str:
    joined_ingredients = ", ".join(ingredients[:2])
    joined_benefits = " & ".join(benefits[:2])
    return (
        f"{category} for {skin_type.lower()} skin with {joined_ingredients} to support "
        f"{joined_benefits.lower()}."
    )


def generate_products(total_rows: int, seed: int = 2503) -> list[Product]:
    randomizer = random.Random(seed)
    products: list[Product] = []

    for product_id in range(1, total_rows + 1):
        brand = randomizer.choice(BRANDS)
        category = randomizer.choice(CATEGORIES)
        ingredients = randomizer.sample(INGREDIENTS, k=randomizer.randint(2, 4))
        benefits = randomizer.sample(BENEFITS, k=randomizer.randint(2, 3))
        skin_type = pick_skin_type(category, randomizer)
        size_ml = randomizer.choice(SIZE_OPTIONS[category])
        price_idr = pick_price(category, brand, randomizer)
        rating = pick_rating(randomizer)
        review_count = pick_review_count(randomizer)

        topic = GITHUB_TOPIC_NAMES[(product_id - 1) % len(GITHUB_TOPIC_NAMES)]
        image_url = f"https://raw.githubusercontent.com/github/explore/main/topics/{topic}/{topic}.png"
        product_name = build_product_name(brand, category, ingredients, randomizer)
        description = create_description(category, skin_type, ingredients, benefits)

        products.append(
            Product(
                id=product_id,
                product_name=product_name,
                brand=brand,
                category=category,
                skin_type=skin_type,
                key_ingredients="; ".join(ingredients),
                benefits="; ".join(benefits),
                size_ml=size_ml,
                price_idr=price_idr,
                rating=rating,
                review_count=review_count,
                image_url=image_url,
                description=description,
            )
        )

    return products


def write_csv(products: list[Product], output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for product in products:
            writer.writerow(product.to_row())


def verify_with_pandas(path: Path, expected_rows: int) -> None:
    df = pd.read_csv(path)

    if len(df) != expected_rows:
        raise ValueError(f"Expected {expected_rows} rows, found {len(df)}")
    if df["id"].nunique() != expected_rows:
        raise ValueError("Duplicate IDs detected")
    if sorted(df["id"].tolist()) != list(range(1, expected_rows + 1)):
        raise ValueError("IDs are not a complete sequence from 1 to expected rows")

    required_columns = [
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

    missing_values = df[required_columns].isna().any().any()
    if missing_values:
        raise ValueError("CSV contains empty required fields")

    empty_strings = any(str(value).strip() == "" for value in df[required_columns].to_numpy().ravel())
    if empty_strings:
        raise ValueError("CSV contains blank required fields")


def _validate_single_image_url(image_url: str, timeout: float, retries: int) -> None:
    request = urllib.request.Request(
        image_url,
        method="GET",
        headers={"User-Agent": "DatasetSkincare2000/1.0"},
    )
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                content_type = response.headers.get("Content-Type", "")
                if response.status != 200 or not content_type.startswith("image/"):
                    raise ValueError(
                        f"Image URL validation failed for {image_url}: "
                        f"status={response.status}, content_type={content_type}"
                    )
            return
        except Exception as err:
            if attempt == retries:
                raise ValueError(f"Image URL validation failed for {image_url}: {err}") from err
            time.sleep(0.5)


def validate_image_urls(products: list[Product], timeout: float = 10.0, retries: int = 2) -> None:
    # URLs are intentionally cycled from GITHUB_TOPIC_NAMES, so deduplication keeps validation fast.
    unique_urls = sorted({product.image_url for product in products})
    with ThreadPoolExecutor(max_workers=min(8, len(unique_urls))) as executor:
        list(executor.map(lambda url: _validate_single_image_url(url, timeout, retries), unique_urls))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate skincare dataset CSV")
    parser.add_argument("--output", default="skincare_dataset_2000.csv", help="Output CSV path")
    parser.add_argument("--rows", type=int, default=2000, help="Number of rows to generate")
    parser.add_argument(
        "--validate-urls",
        action="store_true",
        help="Validate that generated image URLs resolve to real images",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)

    products = generate_products(total_rows=args.rows)
    write_csv(products, output_path)
    verify_with_pandas(output_path, expected_rows=args.rows)

    if args.validate_urls:
        validate_image_urls(products)

    print(f"Generated {args.rows} rows at {output_path.resolve()}")


if __name__ == "__main__":
    main()
