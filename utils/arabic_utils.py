"""
arabic_utils.py
---------------
Lightweight Arabic → English translation utility for the rental marketplace.
Used primarily for the /search/live endpoint to translate Arabic keywords
before doing a SQL LIKE search (which only supports English text in the DB).

No external API needed — uses a curated dictionary of common rental terms.
"""

# ─────────────────────────────────────────────────────────────────────────────
# Translation dictionaries
# ─────────────────────────────────────────────────────────────────────────────

PRODUCT_TRANSLATIONS: dict[str, str] = {
    # Electronics
    "لابتوب": "laptop",
    "لاب توب": "laptop",
    "كمبيوتر": "computer",
    "كمبيوتر محمول": "laptop",
    "موبايل": "mobile",
    "تليفون": "phone",
    "هاتف": "phone",
    "تلفزيون": "TV",
    "شاشة": "screen",
    "شاشه": "screen",
    "كاميرا": "camera",
    "كاميرة": "camera",
    "طابعة": "printer",
    "طابعه": "printer",
    "راوتر": "router",
    "سماعات": "headphones",
    "سماعة": "headphone",
    "بروجيكتور": "projector",
    "بروجيكتر": "projector",
    "جهاز عرض": "projector",
    "جيمنج": "gaming",
    "بلايستيشن": "PlayStation",
    "اكس بوكس": "Xbox",
    "جيم ستيك": "joystick",
    # Furniture
    "أثاث": "furniture",
    "اثاث": "furniture",
    "كرسي": "chair",
    "كراسي": "chairs",
    "طاولة": "table",
    "سرير": "bed",
    "كنبة": "sofa",
    "كنبه": "sofa",
    "ديكور": "decor",
    # Home appliances
    "ثلاجة": "refrigerator",
    "ثلاجه": "refrigerator",
    "غسالة": "washing machine",
    "غساله": "washing machine",
    "فرن": "oven",
    "مكيف": "air conditioner",
    "مكيف هواء": "air conditioner",
    "تكييف": "air conditioner",
    "سخان": "water heater",
    "بوتاجاز": "gas stove",
    "بوتاجاز": "stove",
    "مروحة": "fan",
    "خلاط": "blender",
    "مكنسة": "vacuum",
    "مكنسه": "vacuum",
    # Vehicles / Cars
    "سيارة": "car",
    "سياره": "car",
    "دراجة": "bicycle",
    "دراجه": "bicycle",
    "دراجة نارية": "motorcycle",
    "موتوسيكل": "motorcycle",
    "توك توك": "tuk tuk",
    "شاحنة": "truck",
    # Cameras / Photography
    "كاميرا فيديو": "video camera",
    "كاميرا مراقبة": "surveillance camera",
    "درون": "drone",
    "طائرة بدون طيار": "drone",
    "تلسكوب": "telescope",
    # Tools
    "أدوات": "tools",
    "ادوات": "tools",
    "مثقاب": "drill",
    "منشار": "saw",
    "سلم": "ladder",
    "خيمة": "tent",
    "شنطة": "bag",
    "شنطه": "bag",
    # Clothes / Fashion
    "ملابس": "clothes",
    "فستان": "dress",
    "دريس": "dress",
    "بدلة": "suit",
    "عباية": "abaya",
    "حجاب": "hejab",
    "طرحه": "hejab",
    "طرحة": "hejab",
    "تيشرت": "t-shirt",
    "طوق": "necklace",
    "طوق برايد": "necklace",
    "مروحة": "fan",
    "مروحه": "fan",
    "مروحة ورقية": "fan",
    "مروحه ورقيه": "fan",
    # Musical instruments
    "جيتار": "guitar",
    "بيانو": "piano",
    "طبل": "drum",
    "عود": "oud",
    "كيبورد": "keyboard",
}

BRAND_TRANSLATIONS: dict[str, str] = {
    "سامسونج": "Samsung",
    "سامسونق": "Samsung",
    "آبل": "Apple",
    "ابل": "Apple",
    "سوني": "Sony",
    "شاومي": "Xiaomi",
    "هواوي": "Huawei",
    "هواوى": "Huawei",
    "ديل": "Dell",
    "اتش بي": "HP",
    "لينوفو": "Lenovo",
    "نايكي": "Nike",
    "اديداس": "Adidas",
    "كانون": "Canon",
    "نيكون": "Nikon",
    "إل جي": "LG",
    "ال جي": "LG",
    "توشيبا": "Toshiba",
    "فيليبس": "Philips",
    "بوش": "Bosch",
}

LOCATION_TRANSLATIONS: dict[str, str] = {
    "المعادي": "Maadi",
    "معادي": "Maadi",
    "مدينة نصر": "Nasr City",
    "مدينه نصر": "Nasr City",
    "نصر سيتي": "Nasr City",
    "الزمالك": "Zamalek",
    "زمالك": "Zamalek",
    "الدقي": "Dokki",
    "دقي": "Dokki",
    "الجيزة": "Giza",
    "الجيزه": "Giza",
    "جيزة": "Giza",
    "الإسكندرية": "Alexandria",
    "اسكندرية": "Alexandria",
    "اسكندريه": "Alexandria",
    "القاهرة": "Cairo",
    "القاهره": "Cairo",
    "مصر الجديدة": "Heliopolis",
    "هليوبوليس": "Heliopolis",
    "المنصورة": "Mansoura",
    "المنصوره": "Mansoura",
    "الإسماعيلية": "Ismailia",
    "السويس": "Suez",
    "طنطا": "Tanta",
    "أسيوط": "Assiut",
    "أسوان": "Aswan",
    "الأقصر": "Luxor",
    "المهندسين": "Mohandessin",
    "مهندسين": "Mohandessin",
    "شبرا": "Shubra",
    "الشيخ زايد": "Sheikh Zayed",
    "التجمع": "New Cairo",
    "التجمع الخامس": "New Cairo",
    "القطامية": "Katameya",
    "مصر الجديده": "Heliopolis",
    "البساتين": "El Basatin",
    "حلوان": "Helwan",
    "فيصل": "Faisal",
    "امبابة": "Imbaba",
    "عين شمس": "Ain Shams",
    "بولاق": "Boulaq",
}

CATEGORY_TRANSLATIONS: dict[str, str] = {
    "إلكترونيات": "Electronics",
    "الكترونيات": "Electronics",
    "الكترونيكس": "Electronics",
    "أثاث": "Furniture",
    "اثاث": "Furniture",
    "سيارات": "Cars",
    "عربيات": "Cars",
    "ملابس": "Clothes",
    "أدوات": "Tools",
    "ادوات": "Tools",
    "عدد": "Tools",
    "كاميرات": "Cameras",
    "تصوير": "Cameras",
    "أجهزة منزلية": "Home Appliances",
    "اجهزة منزلية": "Home Appliances",
    "أجهزة كهربائية": "Home Appliances",
    "موسيقى": "Music",
    "آلات موسيقية": "Music",
    "دراجات": "Bicycles",
    "موتوسيكلات": "Motorcycles",
    "رياضة": "Sports",
    "رياضه": "Sports",
    "أثاث مكتبي": "Office Furniture",
    "مكتبي": "Office",
}

# ─────────────────────────────────────────────────────────────────────────────
# Public function
# ─────────────────────────────────────────────────────────────────────────────

def translate_arabic_to_english(text: str) -> str:
    """
    Translate an Arabic search query to English using the curated dictionaries.
    If the text is already English (no Arabic characters), return it unchanged.
    Falls back to the original text if no translation is found.

    Priority: Product terms → Brands → Locations → Categories
    """
    if not text:
        return text

    # Detect if text has Arabic characters
    has_arabic = any("\u0600" <= c <= "\u06ff" for c in text)
    if not has_arabic:
        return text  # already English, no translation needed

    text_stripped = text.strip()

    # Try full match first (longest → shortest for greedy matching)
    all_dicts = [PRODUCT_TRANSLATIONS, BRAND_TRANSLATIONS, LOCATION_TRANSLATIONS, CATEGORY_TRANSLATIONS]
    for d in all_dicts:
        if text_stripped in d:
            return d[text_stripped]

    # Try partial match: replace known Arabic substrings
    result = text_stripped
    # Merge all dicts (product terms first for priority)
    merged = {}
    for d in reversed(all_dicts):  # reverse so product terms win
        merged.update(d)

    # Sort by length descending to match longer phrases first
    for ar_term, en_term in sorted(merged.items(), key=lambda x: -len(x[0])):
        if ar_term in result:
            result = result.replace(ar_term, en_term)

    return result.strip()
