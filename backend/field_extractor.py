import re
from difflib import SequenceMatcher


def normalize_ocr(text: str) -> str:
    t = re.sub(r"\s+", " ", text)
    t = re.sub(r"M\s*\.?\s*R\s*\.?\s*P\.?", "MRP", t, flags=re.IGNORECASE)
    t = re.sub(r"N\s*[eoa]?t\s*\.?\s*W\s*t", "Net Wt", t, flags=re.IGNORECASE)
    return t.strip()


def clean_token(tok: str) -> str:
    return re.sub(r"[^a-z0-9]", "", tok.lower())


FIELD_KEYWORDS = {
    "mrp": ["mrp", "maximumretailprice", "retailprice"],
    "net_quantity": [
        "netwt", "netweight", "netqty", "netquantity",
        "nettwt", "nettweight", "netcontent",
    ],
    "mfg_date": ["manufactured", "mfgdate", "manufacturing", "manufacturedon", "mfg"],
    "best_before": ["bestbefore", "useby", "expirydate", "expiryon", "expiry"],
    "consumer_care": [
        "consumercare", "customercare", "tollfree", "helpline",
        "feedback", "callus", "emailus", "levercare",
    ],
    "manufacturer": ["manufacturedby", "marketedby", "packedby", "mfdby",
                     "mktdby", "mktby", "mktd"],
    "country_of_origin": ["countryoforigin", "madein"],
}


def token_similar(token: str, keywords, threshold=0.9) -> bool:
    t = clean_token(token)
    if not t or len(t) < 3:
        return False
    for kw in keywords:
        if t == kw:
            return True
        if len(kw) >= 6 and len(t) >= 0.6 * len(kw):
            if kw.startswith(t) or t.startswith(kw):
                return True
        if SequenceMatcher(None, t, kw).ratio() >= threshold:
            return True
    return False


VALUE_PATTERNS = {
    "mrp": [
        r"(?:MRP|M\.R\.P)[^\d₹Rs]{0,20}(?:Rs\.?|₹|INR)?\s*(\d{1,5}(?:\.\d{1,2})?)",
        r"(?:Rs\.?|₹)\s*(\d{1,5}(?:\.\d{1,2})?)",
    ],
    "net_quantity": [
        r"(\d+(?:\.\d+)?)\s*(g|gm|gms|grams?|kg|ml|mL|litres?|liters?|l|pcs|pieces?)\b",
    ],
    "mfg_date": [
        r"\b(0?[1-9]|[12]\d|3[01])[\/\-\.](0?[1-9]|1[0-2])[\/\-\.](\d{2}|\d{4})\b",
        r"\b(0?[1-9]|[12]\d|3[01])[\/\-\.](0?[1-9]|1[0-2])[\/\-\.](\d{2})\b",
        r"\b((?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[\s\-]?\d{2,4})\b",
    ],
    "best_before": [
        r"\b(0?[1-9]|[12]\d|3[01])[\/\-\.](0?[1-9]|1[0-2])[\/\-\.](\d{2}|\d{4})\b",
        r"(\d+\s*(?:months?|years?|days?))",
    ],
    "consumer_care": [
        r"(1800[\s\-]?\d{2,4}[\s\-]?\d{2,4}[\s\-]?\d{0,4})",
        r"(\+91[\s\-]?\d{10})",
        r"\b([6-9]\d{9})\b",
        r"\b(0\d{2,4}[\s\-]?\d{6,8})\b",
        r"([\w\.\-]{3,}\s*@\s*[\w\.\-]{3,}\s*\.\s*[\w]{2,6})",
        r"(lever\.?\s*care\s*@?\s*unilever\s*\.?\s*com)",
    ],
    "manufacturer": [
        r"\bby[:\s]+([A-Z][A-Za-z]{2,25}(?:\s+[A-Z][A-Za-z0-9&\.]{1,25}){0,4}\s+(?:PVT|LTD|LIMITED|LLP|INC|CORP|COMPANY|HOLDINGS))",
        r"\b([A-Z][A-Za-z]{2,25}(?:\s+[A-Z][A-Za-z0-9&\.]{1,25}){0,4}\s+(?:PVT|LTD|LIMITED|LLP|INC|CORP|HOLDINGS))",
    ],
    "country_of_origin": [
        r"(?:origin|made\s+in)[:\s\-]+(India|China|USA|UK|Vietnam|Nepal|Bangladesh|Sri\s*Lanka|Germany|Japan|Korea)",
    ],
}


def search_value_in_text(text: str, field: str):
    for pattern in VALUE_PATTERNS.get(field, []):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) > 1 and all(g is not None for g in groups):
                value = "".join(groups) if field == "net_quantity" else "/".join(groups)
            else:
                value = groups[0] if groups[0] is not None else match.group(0)
            return value, match.group(0)
    return None, None


def find_keyword_blocks(ocr_results, keywords, min_conf=0.35):
    """Match keyword patterns against whole-block text AND individual tokens."""
    matches = []
    for r in ocr_results:
        if r["confidence"] < min_conf:
            continue
        whole = re.sub(r"[^a-z0-9]", "", r["text"].lower())
        hit = False
        for kw in keywords:
            if len(kw) >= 4 and kw in whole:
                hit = True
                break
        if not hit:
            tokens = re.split(r"[\s;,\.\:\-]+", r["text"])
            for tok in tokens:
                if token_similar(tok, keywords):
                    hit = True
                    break
        if hit:
            matches.append(r)
    return matches


def find_nearby_value(keyword_block, ocr_results, field):
    kb = keyword_block["bbox"]
    kx = (kb[0][0] + kb[2][0]) / 2
    ky = (kb[0][1] + kb[2][1]) / 2

    candidates = []
    for r in ocr_results:
        if r is keyword_block:
            continue
        b = r["bbox"]
        rx = (b[0][0] + b[2][0]) / 2
        ry = (b[0][1] + b[2][1]) / 2
        dx = rx - kx
        dy = ry - ky

        if -20 < dy < 40 and 0 < dx < 400:
            candidates.append((abs(dy) * 0.5 + dx * 0.1, r))
        elif 0 < dy < 200 and -50 < dx < 250:
            candidates.append((dy + abs(dx) * 0.2, r))

    candidates.sort(key=lambda x: x[0])
    for _, r in candidates:
        val, matched = search_value_in_text(r["text"], field)
        if val:
            return {
                "value": val,
                "matched": matched,
                "bbox": r["bbox"],
                "confidence": r["confidence"],
            }
    return None


def extract_fields(ocr_results):
    full_text = normalize_ocr(" ".join(r["text"] for r in ocr_results))
    found = {}

    for field, keywords in FIELD_KEYWORDS.items():
        keyword_blocks = find_keyword_blocks(ocr_results, keywords)

        value = None
        bbox = None
        confidence = 0.0
        matched_text = ""
        source = "none"

        if keyword_blocks:
            best_kb = max(keyword_blocks, key=lambda r: r["confidence"])
            bbox = best_kb["bbox"]
            confidence = best_kb["confidence"]
            matched_text = best_kb["text"]

            v, _ = search_value_in_text(best_kb["text"], field)
            if v:
                value = v
                source = "keyword_and_value"

            if value is None:
                nearby = find_nearby_value(best_kb, ocr_results, field)
                if nearby:
                    value = nearby["value"]
                    bbox = nearby["bbox"]
                    confidence = nearby["confidence"]
                    source = "keyword_and_value"

            if value is None:
                v, _ = search_value_in_text(full_text, field)
                if v:
                    value = v
                    source = "keyword_and_value"

        if value is None and not keyword_blocks:
            if field in ("mrp", "consumer_care", "country_of_origin", "net_quantity"):
                v, matched = search_value_in_text(full_text, field)
                if v:
                    for r in ocr_results:
                        if (matched and matched[:8] in r["text"]) or (v in r["text"]):
                            value = v
                            bbox = r["bbox"]
                            confidence = r["confidence"]
                            matched_text = r["text"]
                            source = "value_only"
                            break

        if value:
            found[field] = {
                "value": value,
                "bbox": bbox,
                "confidence": confidence,
                "matched_text": matched_text,
                "uncertain": source == "value_only",
                "source": source,
            }
        elif keyword_blocks:
            found[field] = {
                "value": None,
                "bbox": bbox,
                "confidence": confidence,
                "matched_text": matched_text,
                "uncertain": True,
                "source": "keyword_only",
            }

    return found