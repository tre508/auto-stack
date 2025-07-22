import json
import pandas as pd
from urllib.parse import urlparse

# ─── 𝗣𝗮𝘁𝗵 𝘁𝗼 𝗬𝗼𝘂𝗿 𝗙𝗜𝗟𝗘 ───
# Use a Linux-style path, which works natively in WSL.
har_path = "projects/auto-stack/docs/reference/dev-localhost.har"

# ─── 𝗟𝗼𝗮𝗱 𝗧𝗵𝗲 𝗛𝗔𝗥 ───
with open(har_path, "r", encoding="utf-8") as f:
    har_data = json.load(f)

entries = har_data.get("log", {}).get("entries", [])
print(f"✅ Loaded {len(entries)} entries from HAR")

# ─── 𝗣𝗮𝗿𝘀𝗲 𝗲𝗻𝘁𝗿𝗶𝗲𝘀 ───
parsed = []
for entry in entries:
    req = entry.get("request", {})
    resp = entry.get("response", {})
    timings = entry.get("timings", {})

    url = req.get("url", "")
    domain = urlparse(url).netloc or "n/a"
    mime_full = resp.get("content", {}).get("mimeType", "unknown")
    mime = mime_full.split("/")[0] if "/" in mime_full else mime_full
    size = resp.get("content", {}).get("size", 0)
    total_time = entry.get("time", 0)
    ttfb = timings.get("send", 0) + timings.get("wait", 0)
    status = resp.get("status", 0)
    method = req.get("method", "")

    parsed.append({
        "URL": url,
        "Domain": domain,
        "MimeType": mime,
        "SizeBytes": size,
        "TotalTimeMs": total_time,
        "TTFBms": ttfb,
        "Status": status,
        "Method": method
    })

df = pd.DataFrame(parsed)
if df.empty:
    print("⚠️ Parsed DataFrame is empty—no entries found.")
    exit(1)

# ─── 𝗖𝗼𝗿𝗲 𝗦𝘂𝗺𝗺𝗮𝗿𝘆 ───
total_requests = len(df)
total_bytes = df["SizeBytes"].sum()
unique_domains = df["Domain"].nunique()
top_domains = df["Domain"].value_counts().head(10)
by_type = df["MimeType"].value_counts()

print("\n🔹 𝗚𝗲𝗻𝗲𝗿𝗮𝗹 𝗦𝘁𝗮𝘁𝘀:")
print(f"   • Total requests: {total_requests}")
print(f"   • Total bytes transferred: {total_bytes} bytes")
print(f"   • Unique domains contacted: {unique_domains}")

print("\n🔹 𝗧𝗼𝗽 10 𝗗𝗼𝗺𝗮𝗶𝗻𝘀 𝗯𝘆 𝗖𝗼𝘂𝗻𝘁:")
print(top_domains.to_string())

print("\n🔹 𝗥𝗲𝗾𝘂𝗲𝘀𝘁 𝗖𝗼𝘂𝗻𝘁𝘀 𝗯𝘆 𝗠𝗶𝗺𝗲 𝗧𝘆𝗽𝗲:")
print(by_type.to_string())

# ─── 𝗟𝗮𝗿𝗴𝗲𝘀𝘁 𝗣𝗮𝘆𝗹𝗼𝗮𝗱𝘀 ───
largest = df.nlargest(10, "SizeBytes")[["URL","Domain","SizeBytes","Status","MimeType"]]
print("\n🔹 𝗧𝗼𝗽 10 𝗟𝗮𝗿𝗴𝗲𝘀𝘁 𝗣𝗮𝘆𝗹𝗼𝗮𝗱𝘀:")
print(largest.to_string(index=False))

# ─── 𝗦𝗹��𝘄𝗲𝘀𝘁 𝗘𝗻𝗱𝗽𝗼𝗶𝗻𝘁𝘀 ───
slowest = df.nlargest(10, "TotalTimeMs")[["URL","Domain","TotalTimeMs","TTFBms","Status","MimeType"]]
print("\n🔹 𝗧𝗼𝗽 10 𝗦𝗹𝗼𝘄𝗲𝘀𝘁 𝗘𝗻𝗱𝗽𝗼𝗶𝗻𝘁𝘀:")
print(slowest.to_string(index=False))

# ─── 𝗘𝗿𝗿𝗼𝗿 𝗥𝗲𝗾𝘂𝗲𝘀𝘁𝘀 ───
errors = df[df["Status"] >= 400]
if not errors.empty:
    print("\n🔹 𝗘𝗿𝗿𝗼𝗿 𝗥𝗲𝗾𝘂𝗲𝘀𝘁𝘀 (status ≥ 400):")
    print(errors[["URL","Domain","Status","MimeType"]].to_string(index=False))
else:
    print("\n🔹 No 4xx/5xx errors detected.")

# ─── 𝗣𝗮𝗴𝗲 𝗟𝗼𝗮𝗱 𝗧𝗶𝗺𝗶𝗻𝗴𝘀 ───
pages = har_data.get("log", {}).get("pages", [])
if pages:
    pt = pages[0].get("pageTimings", {})
    print(f"\n🔹 Page onContentLoad: {pt.get('onContentLoad')} ms")
    print(f"🔹 Page onLoad:        {pt.get('onLoad')} ms")
