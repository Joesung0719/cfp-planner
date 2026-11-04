# 客戶試用版：建置與發佈

試用版由 `index.html` 自動產生，Joe 自己的工作版（`index.html`）不受影響。

## 試用版與工作版的差異（由 `trial/build.py` 加上）

- 頁面頂端橫幅：「試用版，數字為示意估算，不構成稅務或投資建議」，附「回報問題」（表單）與 LINE 連結、版本號。
- 瀏覽器儲存鍵改為 `retirePlanner.trial.clients.v1`，與正式版分開，同網域下也不會讀到 Joe 的客戶資料。
- 加上 `noindex`，不被搜尋引擎收錄。
- 橫幅顯示試用到期日與剩餘天數，並連到美國稅務試算的測試版；頁面內原本連到美國稅務試算正式版的連結改成測試版。

## 試用期限（與美國稅務試算測試版共用）

- 到期日只在一個地方設定：us-tax-planner repo 的 `trial/expiry.js`（`TRIAL_EXPIRES = "YYYY-MM-DD"`，台灣時間當天 23:59:59 止）。兩個站台同網域，試用版都讀 `/us-tax-planner/trial/expiry.js`，改那一行並推上 us-tax-planner 的 main，兩個試用版同時生效，本 repo 不必改。
- `/cfp-planner/trial/` 是閘門頁（`trial/gate.html`）：未到期才轉到 `app.html`；到期或讀不到設定就只顯示「試用期已結束，請聯絡 Joe」，不載入試算內容。直接開 `app.html` 也會被轉回閘門頁。
- 這是前端軟性限制，懂技術的人可改電腦時間或直接讀原始碼繞過；正式版網址也是公開的。要硬性關閉，把 workflow 的試用版步驟拿掉（不產生 `site/trial/`）後合併，網址即 404。
- 其餘（預設值、「載入勞工範例」、待確認清單、頁尾免責聲明）與工作版相同。預設值是通用的 38 歲／月薪 6 萬等數字，不含任何個人資料。

## 資料不外流

頁面沒有任何 `fetch`、`XMLHttpRequest` 或表單送出；輸入只存在使用者自己的瀏覽器。唯一的對外請求是載入 Tailwind 與 Chart.js 兩個公開函式庫（CDN），不含使用者輸入。

## 發佈方式

同一個 Pages 站台有兩個版本（GitHub 一個 repo 只能一個站台）：

- `/cfp-planner/` 正式版：main 的 `index.html`，合併到 main 就自動更新。
- `/cfp-planner/trial/` 試用版：內容固定在 `trial/pinned-ref.txt` 記的 commit 的 `index.html`，橫幅與到期檢查由 main 的 `trial/build.py` 加上。要更新試用版內容，把該檔改成新的 commit 或標籤並合併到 main。

Settings → Pages → Source 必須是「GitHub Actions」。試用版可在 `trial/config.json` 選填表單與 LINE 連結（須 https），留空則橫幅不顯示。

本機預覽：`python3 trial/build.py --preview`，產生 `dist/index.html`（閘門頁）與 `dist/app.html`。到期檢查用絕對路徑 `/us-tax-planner/trial/expiry.js`，本機要把兩個 repo 放在同一個伺服器根目錄下（`/us-tax-planner/`、`/cfp-planner/`）才看得到內容。
