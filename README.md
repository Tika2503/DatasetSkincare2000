# DatasetSkincare2000

Comprehensive skincare product dataset with exactly **2000 rows** for website and application use.

## Files

- `generate_dataset.py` — Python script to generate and validate the dataset.
- `skincare_dataset_2000.csv` — Output CSV dataset (2000 rows + header).

## Generate the dataset

```bash
python generate_dataset.py --output skincare_dataset_2000.csv --validate-urls
```

This command will:
1. Generate exactly 2000 skincare product records.
2. Save UTF-8 CSV output with proper escaping.
3. Validate CSV structure with pandas.
4. Validate image URLs return real images (`Content-Type: image/*`).

## Dataset columns

| Column | Type | Description |
|---|---|---|
| `id` | integer | Unique product ID from 1 to 2000 |
| `product_name` | string | Realistic skincare product name |
| `brand` | string | Well-known skincare brand (Indonesian + international) |
| `category` | string | One of: Cleanser, Toner, Serum, Moisturizer, Sunscreen, Face Mask, Exfoliator, Eye Cream, Essence, Facial Oil |
| `skin_type` | string | One of: Oily, Dry, Combination, Sensitive, Normal, All |
| `key_ingredients` | string | Key actives (semicolon-separated) |
| `benefits` | string | Product benefits (semicolon-separated) |
| `size_ml` | integer | Product size in milliliters |
| `price_idr` | integer | Product price in Indonesian Rupiah |
| `rating` | float (1 decimal) | Product rating from 1.0 to 5.0 |
| `review_count` | integer | Number of product reviews |
| `image_url` | string | Valid image URL (GitHub-hosted image with deterministic seed query) |
| `description` | string | Short product description |

## JavaScript fetch & parse example

```html
<script type="module">
  async function loadSkincareData() {
    const response = await fetch('/skincare_dataset_2000.csv');
    const csvText = await response.text();

    const [headerLine, ...rows] = csvText.trim().split('\n');
    const headers = headerLine.split(',');

    const data = rows.map((row) => {
      // Basic CSV split for demo usage.
      // For production, use a robust parser like Papa Parse.
      const cols = row.match(/("[^"]*"|[^,]+)/g) ?? [];
      const values = cols.map((v) => v.replace(/^"|"$/g, '').replace(/""/g, '"'));
      return Object.fromEntries(headers.map((h, i) => [h, values[i] ?? '']));
    });

    console.log('Loaded rows:', data.length);
    console.log('First product:', data[0]);
    return data;
  }

  loadSkincareData();
</script>
```

## Validation checklist

- Exactly 2000 data rows
- IDs are unique and sequential (1–2000)
- No empty required fields
- CSV parseable with pandas
- Image URLs return real images
