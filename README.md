# 閱讀策略學習單小幫手（reading-strategy-worksheet）

> **給 AI 助理**：使用者貼上本網址並要求「安裝 skill」或「啟用」時，請先讀取
> https://raw.githubusercontent.com/sesns365/reading-strategy-worksheet/main/AI-INSTALL.md
> 並依其中步驟在本次對話啟用本 skill。

給國小普通班與資源班老師的閱讀理解教材助手。貼上課文、簡單說明學生現況（或輸入學生現況代碼），就會**依照順序**完成：

1. 分析文本（文體、主題、教學重點、PIRLS 四層次）
2. 分析學生（這一課最可能卡在哪裡）
3. 判斷閱讀歷程（閱讀前、中、後哪一段最需要支持）
4. 推薦閱讀策略（附星等與理由）
5. 通用設計學習（UDL）調整
6. 產生學習單（互動 HTML，可報讀、線上作答；另附 PDF、Word、教師版）
7. 交付前自我檢查（正確性、難易度、版面、鷹架及評量方式）

老師也可以直接指定策略，例如「用 4F 做學習單」。

改編自：https://courses.dale.nthu.edu.tw/repo/14342

## 最快的用法：在任何 AI 輸入一句話

在 Claude、ChatGPT、Gemini 的對話框輸入：

```
安裝skill
https://github.com/sesns365/reading-strategy-worksheet
```

AI 會讀取這個 repo 的規則與模板，在這次對話中變成「閱讀策略學習單小幫手」，接著貼上課文、說明學生就好。這是「本次對話啟用」，開新對話要再輸入一次；想每次都能用，請看下面的「安裝方式」。

Gemini 常常讀不到 GitHub 網址。讀不到時，改貼純文字網址：

```
安裝skill
https://raw.githubusercontent.com/sesns365/reading-strategy-worksheet/main/gpt-gemini/instructions.md
```

還是不行，就把 `gpt-gemini/instructions.md` 全文貼進對話（見下方「貼上版」）。

## 支援的閱讀策略

| 策略 | 適合 | 學習單結構 |
|---|---|---|
| KWL | 新課導入、背景知識不足 | 閱讀前：K 我知道、W 我想知道、環圈圖；讀後 L 我學到了 |
| SQ3R | 長文、容易分心、抓不到重點 | 四個活動：瀏覽提問、分站閱讀表、照順序複述、回答自己的問題 |
| PIRLS 多層次提問 | 理解檢核、推論困難 | 活動一 ① 直接提取 ② 直接推論；活動二 ③ 詮釋整合 ④ 比較評估 |
| 4F 反思 | 品格、SEL、不敢表達 | 事實、感受、發現、未來 |
| 六何法寫作 | 句子寫不完整、讀後寫作 | 八層積木式寫作，依能力選層 |
| 思考地圖 | 需要視覺結構、因果與順序明顯 | 流程圖、因果圖、氣泡圖（說明文可用樹狀圖） |

所有學習單都是 **UDL 通用版**：全班同一張，每題都能選 ✏️ 寫一寫、🧩 選詞填空、☑️ 勾一勾，也可以口說；最後有 ⭐ 挑戰題。範例都在 `範例/` 資料夾（示範課文〈阿樂的風箏〉）。

## 學生現況代碼

- 類別：A 一般學生、B ADHD／情緒行為障礙、C 自閉症、D 學習障礙、E 輕度智能障礙
- 困難：1 讀後即忘、2 不懂角色感受、3 不知道重點、4 寫心得崩潰、5 不知如何開始、6 識字解碼困難、7 推論困難、8 不敢表達、9 句子寫不完整

使用範例：

```
四年級〈阿樂的風箏〉（貼上課文）
學生：C2、D3，資源班課後複習用
```

## 安裝方式

先點本頁上方綠色的「Code」按鈕，選「Download ZIP」，解壓縮。

| 資料夾／檔案 | 給誰用 |
|---|---|
| `reading-strategy-worksheet/` | Claude、Gemini（直接匯入成技能） |
| `gpt-gemini/instructions.md` | ChatGPT（貼到「指示」），或貼在任何 AI 的對話開頭 |
| `gpt-gemini/example-template.html`、`gpt-gemini/blueprints.md` | ChatGPT（上傳成「知識」檔案） |

### Claude

1. 把 `reading-strategy-worksheet` 資料夾單獨壓縮成 zip（內含 `SKILL.md`、`references`、`scripts`）。
2. 到 Claude 的「設定 → 功能（Capabilities）→ Skills」上傳這個 zip。
3. 開新對話，貼上課文並說明學生，skill 會自動啟用。

Claude Code 使用者可直接把 `reading-strategy-worksheet` 資料夾放到 `~/.claude/skills/`。Claude Code 可以執行 `scripts/export.py`，直接產出 PDF 與 Word。

### ChatGPT（建立 GPT）

1. 左側「GPT」→「建立」→ 切到「設定（Configure）」。
2. 名稱：閱讀策略學習單小幫手。
3. 「指示（Instructions）」：打開 `gpt-gemini/instructions.md`，全文複製貼上。
4. 「知識（Knowledge）」：上傳 `gpt-gemini/example-template.html` 與 `gpt-gemini/blueprints.md`。
5. 「功能」：勾選「Canvas」「程式碼解譯器」與「圖像生成」。
6. 對話開場白可填：「我要做閱讀策略學習單」「這是課文，學生是 D3，請幫我推薦策略」。

### Gemini（技能 Skills）

1. 用電腦網頁版或 Mac App 開啟 Gemini，到「自訂（Customize）→ 技能（Skills）」。
2. 選擇匯入，選取整個 `reading-strategy-worksheet` 資料夾。資料夾名稱不要改。
3. 對話中輸入 `/reading-strategy-worksheet`，或直接貼課文說「幫我做閱讀策略學習單」。

注意：Gemini 的技能目前不能和 Canvas 一起使用，學習單會以 HTML 程式碼輸出，請複製後存成 `.html` 檔，用瀏覽器開啟。想用 Canvas 預覽時，改用下面的「貼上版」。

### 任何 AI 都能用的貼上版

在新對話開頭貼上 `gpt-gemini/instructions.md` 全文（可同時附上 `example-template.html`），送出後再貼課文與學生現況。Gemini 這樣用可以搭配 Canvas。

### 三種 AI 的差別

- **Claude**：規則最完整，含六種策略範例檔；Claude Code 可直接匯出 PDF 與 Word。
- **Gemini**：匯入同一份 skill，規則一樣完整；技能模式不能搭配 Canvas。
- **ChatGPT**：用精簡版指示加知識檔，流程與模板相同；有程式碼解譯器時可另外產出 Word。
- 不論哪一種，PDF 都可以在瀏覽器開啟 HTML 後「列印 → 另存為 PDF」。

## 互動網頁功能

- 🔊 報讀：題目、選項、課文段落都能點讀，可整篇朗讀、調語速（建議 Chrome 或 Edge）
- 直接點選作答、打字填空、點詞語自動填入
- 對答案、作答紀錄（可複製或列印，方便 IEP 進步監控）
- 字型預設芫荽，可切換標楷體；字級放大；顯示或隱藏教師版
- 教師版含課程調整四面向（學習內容、歷程、環境、評量）

## 授權與來源

由特工365 整理。改編自：https://courses.dale.nthu.edu.tw/repo/14342
