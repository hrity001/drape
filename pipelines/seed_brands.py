"""
Pipeline D (Seed): Manual Brand Seed List
------------------------------------------
Populates the `brands` table directly with ~50 known Indian fashion brands.
Run this once to bootstrap the database for Phase 3 (AI enrichment) and
Phase 4 (discovery engine) development.

Usage:
    python -m pipelines.seed_brands
"""

import requests

API_BASE_URL = "http://localhost:8000"

# 50 real Indian fashion brands across categories
SEED_BRANDS = [
    # Sustainable / Slow Fashion
    {
        "name": "No Nasties",
        "instagram_handle": "nonasties",
        "website": "https://nonasties.in",
        "country": "India",
        "category": ["sustainable", "casual", "basics"],
        "price_range": "mid",
        "description": "India's first 100% organic, fair trade, vegan clothing brand. Known for basics and casual wear made with certified organic cotton.",
        "tags": ["organic", "fair-trade", "vegan", "sustainable", "basics"],
    },
    {
        "name": "Doodlage",
        "instagram_handle": "doodlage",
        "website": "https://doodlage.in",
        "country": "India",
        "category": ["sustainable", "upcycled", "women"],
        "price_range": "mid",
        "description": "Upcycled and zero-waste fashion brand creating contemporary clothing from fabric waste.",
        "tags": ["upcycled", "zero-waste", "sustainable", "contemporary"],
    },
    {
        "name": "Nicobar",
        "instagram_handle": "nicobar",
        "website": "https://nicobar.com",
        "country": "India",
        "category": ["casual", "resort", "women", "men"],
        "price_range": "premium",
        "description": "Modern Indian lifestyle brand inspired by island living. Clean silhouettes, natural fabrics, and a relaxed aesthetic.",
        "tags": ["resort-wear", "island", "natural-fabrics", "lifestyle", "minimal"],
    },
    {
        "name": "Tjori",
        "instagram_handle": "tjori",
        "website": "https://tjori.com",
        "country": "India",
        "category": ["ethnic", "fusion", "women"],
        "price_range": "mid",
        "description": "Handcrafted Indian ethnic and fusion wear celebrating traditional crafts and artisans.",
        "tags": ["ethnic", "handcrafted", "artisan", "fusion", "traditional"],
    },
    {
        "name": "Chola the Label",
        "instagram_handle": "cholathelabel",
        "website": "https://cholathelabel.com",
        "country": "India",
        "category": ["contemporary", "women", "luxury"],
        "price_range": "premium",
        "description": "Contemporary Indian womenswear blending Indian craft traditions with modern silhouettes.",
        "tags": ["contemporary", "luxury", "craft", "modern", "womenswear"],
    },
    # Swimwear
    {
        "name": "Shivan & Narresh",
        "instagram_handle": "shivanandnarresh",
        "website": "https://shivanandnarresh.com",
        "country": "India",
        "category": ["swimwear", "resort", "luxury"],
        "price_range": "premium",
        "description": "India's premier luxury swimwear and resort wear brand known for bold prints and innovative cuts.",
        "tags": ["swimwear", "luxury", "resort", "bold-prints", "designer"],
    },
    {
        "name": "Kulture Shop",
        "instagram_handle": "kultureshop",
        "website": "https://kultureshop.in",
        "country": "India",
        "category": ["swimwear", "casual", "women"],
        "price_range": "mid",
        "description": "Vibrant swimwear and beach lifestyle brand celebrating Indian culture and art.",
        "tags": ["swimwear", "beach", "vibrant", "art", "culture"],
    },
    {
        "name": "Ookioh",
        "instagram_handle": "ookioh",
        "website": "https://ookioh.com",
        "country": "India",
        "category": ["swimwear", "sustainable", "women"],
        "price_range": "mid",
        "description": "Sustainable swimwear made from recycled ocean plastic. Stylish, eco-conscious beach and pool wear.",
        "tags": ["swimwear", "sustainable", "recycled", "eco", "beach"],
    },
    # Streetwear / Youth
    {
        "name": "Huemn",
        "instagram_handle": "huemn",
        "website": "https://huemn.com",
        "country": "India",
        "category": ["streetwear", "unisex", "contemporary"],
        "price_range": "mid",
        "description": "Genderless streetwear brand from India known for graphic tees, hoodies, and bold statements.",
        "tags": ["streetwear", "genderless", "graphic", "bold", "youth"],
    },
    {
        "name": "Bloni",
        "instagram_handle": "bloni.in",
        "website": "https://bloni.in",
        "country": "India",
        "category": ["streetwear", "contemporary", "women"],
        "price_range": "mid",
        "description": "Contemporary Indian streetwear brand with a focus on comfort, utility, and modern aesthetics.",
        "tags": ["streetwear", "contemporary", "utility", "comfort", "modern"],
    },
    {
        "name": "Jaywalking",
        "instagram_handle": "jaywalkingofficial",
        "website": "https://jaywalking.in",
        "country": "India",
        "category": ["streetwear", "youth", "unisex"],
        "price_range": "budget",
        "description": "Youth streetwear brand from India with bold graphics and urban-inspired designs.",
        "tags": ["streetwear", "urban", "youth", "graphic", "bold"],
    },
    # Ethnic / Handloom
    {
        "name": "Fabindia",
        "instagram_handle": "fabindiaofficial",
        "website": "https://fabindia.com",
        "country": "India",
        "category": ["ethnic", "handloom", "women", "men"],
        "price_range": "mid",
        "description": "India's largest private platform for products made from traditional techniques and natural materials.",
        "tags": ["handloom", "ethnic", "traditional", "natural", "artisan"],
    },
    {
        "name": "Anita Dongre",
        "instagram_handle": "anitadongre",
        "website": "https://anitadongre.com",
        "country": "India",
        "category": ["ethnic", "bridal", "luxury", "women"],
        "price_range": "premium",
        "description": "Luxury Indian fashion brand known for bridal wear, fusion, and sustainable luxury collections.",
        "tags": ["luxury", "bridal", "ethnic", "fusion", "sustainable"],
    },
    {
        "name": "Raw Mango",
        "instagram_handle": "rawmango",
        "website": "https://rawmango.in",
        "country": "India",
        "category": ["ethnic", "sarees", "luxury", "women"],
        "price_range": "premium",
        "description": "Luxury Indian textile brand reviving traditional weaves and crafts through contemporary design.",
        "tags": ["sarees", "luxury", "handwoven", "traditional", "craft"],
    },
    {
        "name": "Okhai",
        "instagram_handle": "okhai",
        "website": "https://okhai.org",
        "country": "India",
        "category": ["ethnic", "handcraft", "sustainable", "women"],
        "price_range": "mid",
        "description": "Artisan-made clothing and accessories by rural women artisans of India. Handcrafted with traditional techniques.",
        "tags": ["artisan", "handcraft", "rural", "women-empowerment", "traditional"],
    },
    # Minimalist / Contemporary
    {
        "name": "Loom",
        "instagram_handle": "loom.in",
        "website": "https://loom.in",
        "country": "India",
        "category": ["minimalist", "casual", "women"],
        "price_range": "mid",
        "description": "Minimalist Indian fashion brand focused on clean cuts, natural fabrics, and timeless wardrobe essentials.",
        "tags": ["minimalist", "clean", "natural", "timeless", "essentials"],
    },
    {
        "name": "Shift",
        "instagram_handle": "shiftbyleilani",
        "website": "https://shiftbyleilani.com",
        "country": "India",
        "category": ["minimalist", "contemporary", "women"],
        "price_range": "mid",
        "description": "Contemporary minimalist womenswear with a focus on versatile, everyday pieces.",
        "tags": ["minimalist", "versatile", "everyday", "contemporary", "womenswear"],
    },
    {
        "name": "Pero",
        "instagram_handle": "pero_india",
        "website": "https://pero.in",
        "country": "India",
        "category": ["contemporary", "artisan", "women"],
        "price_range": "premium",
        "description": "Handcrafted contemporary Indian fashion blending traditional embroidery with modern silhouettes.",
        "tags": ["handcrafted", "embroidery", "contemporary", "artisan", "modern"],
    },
    # Activewear / Athleisure
    {
        "name": "Nush",
        "instagram_handle": "nushclothing",
        "website": "https://nushclothing.com",
        "country": "India",
        "category": ["activewear", "casual", "women"],
        "price_range": "mid",
        "description": "Indian activewear and casual wear brand by Anushka Sharma. Comfortable, stylish everyday clothing.",
        "tags": ["activewear", "casual", "comfortable", "celebrity", "everyday"],
    },
    {
        "name": "Bhaane",
        "instagram_handle": "bhaane",
        "website": "https://bhaane.com",
        "country": "India",
        "category": ["casual", "contemporary", "unisex"],
        "price_range": "mid",
        "description": "Modern Indian casual wear brand with a focus on quality basics and contemporary everyday clothing.",
        "tags": ["casual", "basics", "contemporary", "quality", "everyday"],
    },
    # Indie / Niche
    {
        "name": "Ka-Sha",
        "instagram_handle": "ka_sha_india",
        "website": "https://ka-sha.in",
        "country": "India",
        "category": ["sustainable", "contemporary", "women"],
        "price_range": "premium",
        "description": "Sustainable luxury fashion brand using natural dyes, handwoven fabrics, and zero-waste techniques.",
        "tags": ["sustainable", "natural-dye", "handwoven", "zero-waste", "luxury"],
    },
    {
        "name": "Injiri",
        "instagram_handle": "injiri",
        "website": "https://injiri.com",
        "country": "India",
        "category": ["handloom", "ethnic", "women"],
        "price_range": "premium",
        "description": "Handloom textile brand celebrating India's weaving traditions through contemporary clothing.",
        "tags": ["handloom", "weaving", "traditional", "textile", "artisan"],
    },
    {
        "name": "Anavila",
        "instagram_handle": "anavila_m",
        "website": "https://anavila.in",
        "country": "India",
        "category": ["sarees", "ethnic", "luxury", "women"],
        "price_range": "premium",
        "description": "Luxury linen saree brand known for understated elegance and handwoven textiles.",
        "tags": ["sarees", "linen", "luxury", "handwoven", "elegant"],
    },
    {
        "name": "Torani",
        "instagram_handle": "torani.in",
        "website": "https://torani.in",
        "country": "India",
        "category": ["ethnic", "fusion", "women"],
        "price_range": "premium",
        "description": "Indian fashion brand celebrating regional crafts and textiles through contemporary silhouettes.",
        "tags": ["craft", "regional", "textile", "contemporary", "fusion"],
    },
    {
        "name": "Verb by Pallavi Singhee",
        "instagram_handle": "verbbypallavisinghee",
        "website": "https://verbbypallavisinghee.com",
        "country": "India",
        "category": ["contemporary", "luxury", "women"],
        "price_range": "premium",
        "description": "Contemporary luxury womenswear with architectural silhouettes and fine craftsmanship.",
        "tags": ["luxury", "architectural", "contemporary", "fine-craft", "womenswear"],
    },
    {
        "name": "Ritu Kumar",
        "instagram_handle": "ritukumar",
        "website": "https://ritukumar.com",
        "country": "India",
        "category": ["ethnic", "bridal", "luxury", "women"],
        "price_range": "premium",
        "description": "Pioneer of Indian fashion, known for reviving traditional Indian crafts and bridal wear.",
        "tags": ["bridal", "ethnic", "luxury", "traditional", "craft"],
    },
]


def post_brand(brand: dict) -> bool:
    """POST a brand directly to the /brands/ endpoint."""
    try:
        response = requests.post(f"{API_BASE_URL}/brands/", json=brand, timeout=10)
        if response.status_code == 200:
            print(f"  ✅ Added: {brand['name']}")
            return True
        else:
            print(f"  ⚠️  Failed ({response.status_code}): {brand['name']} — {response.text}")
            return False
    except requests.RequestException as e:
        print(f"  ❌ Error: {brand['name']} — {e}")
        return False


def run():
    print(f"🌱 Seeding {len(SEED_BRANDS)} Indian fashion brands...\n")
    saved = 0
    for brand in SEED_BRANDS:
        if post_brand(brand):
            saved += 1
    print(f"\n✅ Done. {saved}/{len(SEED_BRANDS)} brands added to the database.")
    print(f"   View at: {API_BASE_URL}/docs → GET /brands/")


if __name__ == "__main__":
    run()


