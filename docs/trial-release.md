# 客戶試用版：建置與發佈

試用版由 `index.html` 自動產生，Joe 自己的工作版（`index.html`）不受影響。

## 試用版與工作版的差異（由 `trial/build.py` 加上）

- 頁面頂端橫幅：「試用版，數字為示意估算，不構成稅務或投資建議」，附「回報問題」（表單）與 LINE 連結、版本號。
- 瀏覽器儲存鍵改為 `retirePlanner.trial.clients.v1`，與正式版分開，同網域下也不會讀到 Joe 的客戶資料。
- 加上 `noindex`，不被搜尋引擎收錄。
- 其餘（預設值、「載入勞工範例」、待確認清單、頁尾免責聲明）與工作版相同。預設值是通用的 38 歲／月薪 6 萬等數字，不含任何個人資料。

## 資料不外流

頁面沒有任何 `fetch`、`XMLHttpRequest` 或表單送出；輸入只存在使用者自己的瀏覽器。唯一的對外請求是載入 Tailwind 與 Chart.js 兩個公開函式庫（CDN），不含使用者輸入。

## 發佈步驟（需 Joe 核准後才做）

1. 在 `trial/config.json` 填入 `feedbackFormUrl` 與 `lineUrl`（皆須 https）。
2. 在 GitHub：Settings → Pages → Source 選「GitHub Actions」。
3. 建立 Release，標籤為 `trial-0.1`（之後 `trial-0.2`…）。工作流程會用該標籤的程式碼建置並發佈，所以試用版固定在該版本，工作版繼續改也不會影響。
4. 網址通常是 `https://joesung0719.github.io/cfp-planner/`。

本機預覽：`python3 trial/build.py --preview`，再開 `dist/index.html`。
