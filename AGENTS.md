# AGENTS.md

本項目為古詩詞 fortune 數據庫。維護時遵循以下硬約束：

- **單一事實源**：`gushici.yaml` 是唯一手工維護的繁體源數據；禁止直接修改 `data/`。
- **繁體手工維護**：必須維護權威繁體正字（參照 [正字.md](正字.md)）；嚴禁使用 OpenCC 簡轉繁逆向生成源數據。
- **排版與驗證閉環**：正文換行遵循 [排版規則](.agents/README.md#body-排版規則)；任何修改後必須執行 `make compile` 生成派生文件並通過 `make verify` 驗證。

**任務路由**：
- 新增作品：遵循 [.agents/workflows/add-work.md](.agents/workflows/add-work.md)
- 修改/校對作品：遵循 [.agents/workflows/edit-work.md](.agents/workflows/edit-work.md)
- 詳細條目規範與排版規則：查閱 [.agents/README.md](.agents/README.md)
