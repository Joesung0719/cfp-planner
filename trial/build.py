#!/usr/bin/env python3
"""由 index.html 產生「客戶試用版」到 dist/index.html，原檔不動。

用法：
  python3 trial/build.py --preview   # 回報連結未填也能產生（僅供本機預覽，不可發佈）
  python3 trial/build.py --release   # 發佈用（表單與 LINE 連結可留空）
"""
import argparse, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
cfg = json.loads((ROOT / "trial" / "config.json").read_text(encoding="utf-8"))

ap = argparse.ArgumentParser()
g = ap.add_mutually_exclusive_group(required=True)
g.add_argument("--preview", action="store_true")
g.add_argument("--release", action="store_true")
args = ap.parse_args()

form, line = cfg["feedbackFormUrl"].strip(), cfg["lineUrl"].strip()
for name, url in (("feedbackFormUrl", form), ("lineUrl", line)):
    if url and not url.startswith("https://"):
        sys.exit(f"{name} 必須是 https:// 開頭")

html = (ROOT / "index.html").read_text(encoding="utf-8")

def link(url, text):
    return f'<a href="{url}" target="_blank" rel="noopener" class="underline font-bold">{text}</a>'

banner = f"""
<div id="trialBanner" style="background:#fef3c7;border-bottom:2px solid #f59e0b;color:#78350f;font-size:0.9375rem;line-height:1.5;padding:8px 12px;text-align:center">
  <strong>試用版</strong>，數字為示意估算，不構成稅務或投資建議。
  <span class="no-print">
    {" ｜ " + link(form, "回報問題") if form else ""}{" ｜ " + link(line, cfg.get("lineLabel", "LINE 聯絡")) if line else ""}
    ｜ 所有計算都在您的瀏覽器內完成，不會上傳或蒐集您輸入的資料。有問題請直接回覆給提供試用連結的規劃人，請勿傳送身分證字號。
  </span>
  <span style="opacity:.7">（{cfg["trialVersion"]}）</span>
</div>
"""

# 1) 橫幅放在 <body> 之後
html, n = re.subn(r"(<body[^>]*>)", lambda m: m.group(1) + banner, html, count=1)
assert n == 1, "找不到 <body>"

# 2) 試用版使用自己的儲存鍵，避免與同網域下的正式版共用瀏覽器資料
old_key = "retirePlanner.clients.v1"
assert html.count(old_key) == 1, "儲存鍵出現次數不符，請檢查 index.html"
html = html.replace(old_key, "retirePlanner.trial.clients.v1")

# 3) 試用版不被搜尋引擎收錄
html = html.replace("<title>", '<meta name="robots" content="noindex,nofollow">\n  <title>', 1)

out = ROOT / "dist"
out.mkdir(exist_ok=True)
(out / "index.html").write_text(html, encoding="utf-8")
(out / ".nojekyll").write_text("", encoding="utf-8")
print(f"OK dist/index.html ({'release' if args.release else 'preview'}, {cfg['trialVersion']})")
