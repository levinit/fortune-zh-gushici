# Workflow: 修改/校對作品條目

當用戶要求勘誤、補正文、調整題名或作者、修改註解、或刪除現有作品時，使用本流程。目標是確保「定位條目 -> 查證依據 -> 用戶確認 -> 局部修改 -> 生成派生文件 -> 驗證閉環」。

## 1. 定位條目

先在 `gushici.yaml` 中檢索目標作品，確認唯一位置與當前收錄型態：

```bash
python3 build.py --check "題名、作者或正文片段"
rg -n "題名|作者|關鍵句" gushici.yaml
```

確認：
- 該作品是單獨條目，還是包含在組詩/組文中。
- 是整首修改，還是局部字詞勘誤。
- 是否涉及 `group`（唱和/前後作關聯）。

## 2. 查證依據與正字

- **版本依據**：古籍異文、版本疑義應查核權威出處（如《全唐詩》、《全宋詞》、四庫本等）。若僅為通行本與古本異文，正文從通行本或古本時應於 `notes` 記明。
- **繁體與正字**：必須維護繁體文本，恪守 [正字.md](../../正字.md)（如「挂/掛」、「涌/湧」、「横/橫」等字理辨析）；嚴禁使用 OpenCC 簡轉繁反推。

## 3. 擬定變更並確認

在修改 `gushici.yaml` 前，向用戶清楚展示擬變更內容：
- 修改目標（朝代、作者、題名、行號）。
- 修改前 vs 修改後內容。
- 變更理由或版本出處依據。
- 取得用戶確認後再執行寫入。

## 4. 寫入源文件

- 僅對目標條目做最小局部替換（patch），保持 YAML 縮進與列表格式一致。
- 正文換行必須嚴格遵循 [.agents/README.md](../README.md#body-排版規則)（絕句每句一行、律詩兩句一聯、長短句按句號分行）。
- 不順手重排或改動無關條目。

## 5. 生成派生文件

修改 `gushici.yaml` 後，執行：

```bash
make compile
```

確保 `data/gushici-cht`、`data/gushici-chs` 及其 `.dat` 索引同步更新。

## 6. 驗證閉環

執行：

```bash
make verify
git diff --check
python3 build.py --check "修改的作品題名"
fortune data/gushici-cht
fortune data/gushici-chs
```

若環境有 OpenCC，可核驗繁簡派生一致性：

```bash
opencc -i data/gushici-cht -o /private/tmp/gushici-chs.check -c t2s.json
diff -u data/gushici-chs /private/tmp/gushici-chs.check
```

## 7. 回覆用戶

簡要說明：
- 修改了哪個作品、修改了哪些字詞或欄位。
- 派生文件是否已更新。
- 執行了哪些驗證與結果。
- 當前變更是否已提交。
