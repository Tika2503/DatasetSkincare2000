# DatasetSkincare2000

Dataset skincare berisi 2000 produk dalam format CSV, lengkap dengan URL gambar, untuk digunakan pada website.

## Files

- `skincare_dataset_2000.csv` — dataset utama dengan tepat 2000 baris data skincare.
- `generate_dataset.py` — skrip Python untuk menghasilkan dataset secara deterministik.

## Dataset columns

| Column | Type | Description |
| --- | --- | --- |
| `id` | integer | ID unik dari 1 sampai 2000. |
| `product_name` | string | Nama produk skincare yang realistis. |
| `brand` | string | Brand skincare populer Indonesia dan internasional. |
| `category` | string | Kategori produk: Cleanser, Toner, Serum, Moisturizer, Sunscreen, Face Mask, Exfoliator, Eye Cream, Essence, Facial Oil. |
| `skin_type` | string | Target jenis kulit: Oily, Dry, Combination, Sensitive, Normal, All. |
| `key_ingredients` | string | Bahan aktif utama, dipisahkan dengan koma. |
| `benefits` | string | Manfaat utama produk, dipisahkan dengan koma. |
| `size_ml` | integer | Ukuran produk dalam mililiter. |
| `price_idr` | integer | Harga realistis dalam Rupiah. |
| `rating` | float | Rating 1.0–5.0 dengan satu angka desimal. |
| `review_count` | integer | Jumlah ulasan realistis. |
| `image_url` | string | URL gambar produk yang dapat dimuat oleh website (inline SVG data URL). |
| `description` | string | Deskripsi singkat produk. |

## Generate the dataset

Jalankan perintah berikut dari root repository:

```bash
python generate_dataset.py --output skincare_dataset_2000.csv
```

Untuk sekaligus memverifikasi bahwa semua URL gambar valid dan dapat dibaca sebagai image:

```bash
python generate_dataset.py --output skincare_dataset_2000.csv --validate-urls
```

## CSV usage example in a website

```html
<script type="module">
  function parseCsvLine(line) {
    const values = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i += 1) {
      const char = line[i];
      const nextChar = line[i + 1];

      if (char === '"' && inQuotes && nextChar === '"') {
        current += '"';
        i += 1;
      } else if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === ',' && !inQuotes) {
        values.push(current);
        current = '';
      } else {
        current += char;
      }
    }

    values.push(current);
    return values;
  }

  async function loadSkincareProducts() {
    const response = await fetch('./skincare_dataset_2000.csv');
    const csvText = await response.text();

    const rows = csvText.trim().split('\n');
    const headers = parseCsvLine(rows[0]);

    const products = rows.slice(1).map((row) => {
      const values = parseCsvLine(row);
      return Object.fromEntries(
        headers.map((header, index) => [header, values[index] ?? '']),
      );
    });

    console.log(products[0]);
    return products;
  }

  loadSkincareProducts();
</script>
```

## Validation notes

Dataset ini dibuat dalam encoding UTF-8 dan ditulis menggunakan `csv.DictWriter` agar tetap aman untuk field yang mengandung koma. Kolom `image_url` memakai SVG `data:` URL agar dataset tetap self-contained dan dapat langsung dipakai pada website tanpa bergantung pada host gambar eksternal. Skrip generator juga memvalidasi:

- jumlah baris tepat 2000,
- tidak ada duplicate `id`,
- tidak ada field wajib yang kosong,
- file CSV dapat diparse ulang,
- dan dapat diverifikasi dengan `pandas` bila package tersebut tersedia.
