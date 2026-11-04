#!/usr/bin/env python3
"""由 index.html 產生「客戶試用版」到 dist/index.html，原檔不動。

用法：
  python3 trial/build.py --preview   # 回報連結未填也能產生（僅供本機預覽，不可發佈）
  python3 trial/build.py --release   # 發佈用（表單與 LINE 連結可留空）
  --src 指定來源 index.html（預設本 repo 的 index.html），--out 指定輸出檔（預設 dist/app.html）。

試用期限由美國稅務試算 repo 的 trial/expiry.js 統一設定（同網域 /us-tax-planner/trial/expiry.js），
兩個試用版共用同一個到期日。過期或讀不到設定時，app.html 會轉回 ./（閘門頁）顯示到期訊息。
"""
import argparse, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
cfg = json.loads((ROOT / "trial" / "config.json").read_text(encoding="utf-8"))

ap = argparse.ArgumentParser()
g = ap.add_mutually_exclusive_group(required=True)
g.add_argument("--preview", action="store_true")
g.add_argument("--release", action="store_true")
ap.add_argument("--src", default=str(ROOT / "index.html"))
ap.add_argument("--out", default=str(ROOT / "dist" / "app.html"))
args = ap.parse_args()

form, line = cfg["feedbackFormUrl"].strip(), cfg["lineUrl"].strip()
for name, url in (("feedbackFormUrl", form), ("lineUrl", line)):
    if url and not url.startswith("https://"):
        sys.exit(f"{name} 必須是 https:// 開頭")

html = pathlib.Path(args.src).read_text(encoding="utf-8")

def link(url, text):
    return f'<a href="{url}" target="_blank" rel="noopener" class="underline font-bold">{text}</a>'

banner = f"""
<div id="trialBanner" style="background:#fef3c7;border-bottom:2px solid #f59e0b;color:#78350f;font-size:0.9375rem;line-height:1.5;padding:8px 12px;text-align:center">
  <strong>試用版</strong>，試用至 <strong id="trialEnd"></strong><span id="trialLeft"></span>，數字為示意估算，不構成投資、法律或稅務建議。
  ｜ <a href="https://joesung0719.github.io/us-tax-planner/trial/" target="_blank" rel="noopener" class="underline font-bold">美國稅務試算（測試版）</a>
  <span class="no-print">
    {" ｜ " + link(form, "回報問題") if form else ""}{" ｜ " + link(line, cfg.get("lineLabel", "LINE 聯絡")) if line else ""}
    ｜ 所有計算都在您的瀏覽器內完成，不會上傳或蒐集您輸入的資料。有問題請直接回覆給提供試用連結的規劃人，請勿傳送身分證字號。
  </span>
  <span style="opacity:.7">（{cfg["trialVersion"]}）</span>
</div>
<script>document.getElementById("trialEnd").textContent = TRIAL.expires; document.getElementById("trialLeft").textContent = "（剩 " + TRIAL.daysLeft + " 天）";</script>
"""

# 1) 橫幅放在 <body> 之後
html, n = re.subn(r"(<body[^>]*>)", lambda m: m.group(1) + banner, html, count=1)
assert n == 1, "找不到 <body>"

# 2) 試用版使用自己的儲存鍵，避免與同網域下的正式版共用瀏覽器資料
old_key = "retirePlanner.clients.v1"
assert html.count(old_key) == 1, "儲存鍵出現次數不符，請檢查 index.html"
html = html.replace(old_key, "retirePlanner.trial.clients.v1")

# 3) 試用版不被搜尋引擎收錄；加上到期檢查（過期就不顯示試算內容，轉回閘門頁）
guard = ('<meta name="robots" content="noindex,nofollow">\n'
         '  <script src="/us-tax-planner/trial/expiry.js"></script>\n'
         '  <script>if (!window.TRIAL || TRIAL.expired) location.replace("./" + location.hash);</script>\n  <title>')
assert html.count("<title>") == 1, "找不到 <title>"
html = html.replace("<title>", guard, 1)

# 4) 連到美國稅務試算的測試版，不連正式版
html = html.replace("https://joesung0719.github.io/us-tax-planner/", "https://joesung0719.github.io/us-tax-planner/trial/")

out = pathlib.Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding="utf-8")
(out.parent / "index.html").write_text((ROOT / "trial" / "gate.html").read_text(encoding="utf-8"), encoding="utf-8")
(out.parent / ".nojekyll").write_text("", encoding="utf-8")
print(f"OK {out} + index.html 閘門頁 ({'release' if args.release else 'preview'}, {cfg['trialVersion']})")
