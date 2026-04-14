#!/usr/bin/env python3
"""
Convert Clash classical rules to domain/ipcidr format for iOS memory efficiency.

Sources:
  - blackmatrix7/ios_rule_script: per-service rulesets (classical format)
  - logicrw/RuleGo: AI, Gemini, Crypto rulesets (Surge list format)

Output (in rules/):
  - {name}.yaml       behavior: domain   (DOMAIN + DOMAIN-SUFFIX)
  - {name}-ip.yaml    behavior: ipcidr   (IP-CIDR + IP-CIDR6)
  - {name}-kw.yaml    behavior: classical (DOMAIN-KEYWORD only)

User-editable files (proxy-extra.yaml, direct-extra.yaml) are NOT touched.
"""

import os
import sys
import urllib.request

RULES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rules")

# --- Sources ---

BLACKMATRIX7 = "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash"
BM7_SERVICES = {
    "wechat":    "WeChat/WeChat.yaml",
    "bytedance": "ByteDance/ByteDance.yaml",
    "bilibili":  "BiliBili/BiliBili.yaml",
    "youtube":   "YouTube/YouTube.yaml",
    "netflix":   "Netflix/Netflix.yaml",
    "disney":    "Disney/Disney.yaml",
    "tiktok":    "TikTok/TikTok.yaml",
    "telegram":  "Telegram/Telegram.yaml",
    "twitter":   "Twitter/Twitter.yaml",
    "paypal":    "PayPal/PayPal.yaml",
    "apple":     "Apple/Apple_Classical.yaml",
    "google":    "Google/Google.yaml",
}

RULEGO = "https://raw.githubusercontent.com/logicrw/RuleGo/patch-1/Surge/Ruleset"
RULEGO_SERVICES = {
    "ai-extra": "Extra/AI.list",
    "gemini":   "Extra/GenAI/Google.list",
    "crypto":   "Extra/Crypto.list",
}


# --- Download ---

def download(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "clash-rules-converter"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except Exception as e:
        print(f"  WARN: {url}: {e}", file=sys.stderr)
        return None


# --- Parsers ---

def parse_classical(content):
    """Parse Clash classical payload."""
    r = {"domains": [], "suffixes": [], "keywords": [], "ipv4": [], "ipv6": []}
    in_payload = False
    for line in content.splitlines():
        s = line.strip()
        if s == "payload:":
            in_payload = True
            continue
        if not in_payload or not s.startswith("- "):
            continue
        rule = s[2:].strip().strip("'\"")
        if rule.startswith("DOMAIN-SUFFIX,"):
            r["suffixes"].append(rule.split(",", 1)[1])
        elif rule.startswith("DOMAIN-KEYWORD,"):
            r["keywords"].append(rule.split(",", 1)[1])
        elif rule.startswith("DOMAIN,"):
            r["domains"].append(rule.split(",", 1)[1])
        elif rule.startswith("IP-CIDR6,"):
            r["ipv6"].append(rule.split(",", 1)[1].split(",")[0])
        elif rule.startswith("IP-CIDR,"):
            r["ipv4"].append(rule.split(",", 1)[1].split(",")[0])
        # PROCESS-NAME, IP-ASN, USER-AGENT → skip (not useful on iOS)
    return r


def parse_surge_list(content):
    """Parse Surge list format (one rule per line)."""
    r = {"domains": [], "suffixes": [], "keywords": [], "ipv4": [], "ipv6": []}
    for line in content.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        rule = s.split(",extended-matching")[0].strip()
        if rule.startswith("DOMAIN-SUFFIX,"):
            r["suffixes"].append(rule.split(",", 1)[1])
        elif rule.startswith("DOMAIN-KEYWORD,"):
            r["keywords"].append(rule.split(",", 1)[1])
        elif rule.startswith("DOMAIN,"):
            r["domains"].append(rule.split(",", 1)[1])
        elif rule.startswith("IP-CIDR6,"):
            r["ipv6"].append(rule.split(",", 1)[1].split(",")[0])
        elif rule.startswith("IP-CIDR,"):
            r["ipv4"].append(rule.split(",", 1)[1].split(",")[0])
    return r


# --- Writers ---

def write_domain(filepath, domains, suffixes):
    entries = sorted(set(f"'{d}'" for d in domains)) + sorted(set(f"'+.{s}'" for s in suffixes))
    if not entries:
        return 0
    with open(filepath, "w") as f:
        f.write("payload:\n")
        for e in entries:
            f.write(f"  - {e}\n")
    return len(entries)


def write_ipcidr(filepath, ipv4, ipv6):
    entries = sorted(set(ipv4)) + sorted(set(ipv6))
    if not entries:
        return 0
    with open(filepath, "w") as f:
        f.write("payload:\n")
        for e in entries:
            f.write(f"  - '{e}'\n")
    return len(entries)


def write_keywords(filepath, keywords):
    kws = sorted(set(keywords))
    if not kws:
        return 0
    with open(filepath, "w") as f:
        f.write("payload:\n")
        for kw in kws:
            f.write(f"  - DOMAIN-KEYWORD,{kw}\n")
    return len(kws)


# --- Main ---

def process(name, parsed):
    gen = {}
    n = write_domain(os.path.join(RULES_DIR, f"{name}.yaml"), parsed["domains"], parsed["suffixes"])
    if n:
        gen["domain"] = n
    n = write_ipcidr(os.path.join(RULES_DIR, f"{name}-ip.yaml"), parsed["ipv4"], parsed["ipv6"])
    if n:
        gen["ipcidr"] = n
    n = write_keywords(os.path.join(RULES_DIR, f"{name}-kw.yaml"), parsed["keywords"])
    if n:
        gen["keywords"] = n
    return gen


def main():
    os.makedirs(RULES_DIR, exist_ok=True)

    print("=== blackmatrix7 ===")
    for name, path in BM7_SERVICES.items():
        url = f"{BLACKMATRIX7}/{path}"
        print(f"  {name} ...", end=" ", flush=True)
        content = download(url)
        if content:
            gen = process(name, parse_classical(content))
            print(", ".join(f"{v} {k}" for k, v in gen.items()) or "empty")
        else:
            print("FAILED")

    print("\n=== RuleGo ===")
    for name, path in RULEGO_SERVICES.items():
        url = f"{RULEGO}/{path}"
        print(f"  {name} ...", end=" ", flush=True)
        content = download(url)
        if content:
            gen = process(name, parse_surge_list(content))
            print(", ".join(f"{v} {k}" for k, v in gen.items()) or "empty")
        else:
            print("FAILED")

    # Summary
    print("\n=== Generated files ===")
    for f in sorted(os.listdir(RULES_DIR)):
        if f in ("proxy-extra.yaml", "direct-extra.yaml"):
            continue
        path = os.path.join(RULES_DIR, f)
        size = os.path.getsize(path)
        print(f"  {f:30s} {size:>6d} bytes")


if __name__ == "__main__":
    main()
