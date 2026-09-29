# fortune-zh-gushici

<p align="center">
  <img src="cover.png" alt="fortune-zh-gushici 古詩詞" width="600">
</p>

給 `fortune` 命令使用的中文古詩詞庫，提供繁體與簡體兩個版本。

內容以傳世經典詩詞為主，也收錄部分辭賦、駢文與富有韻律的短篇散文。

> ```shell
> 登鸛雀樓
> 唐·王之渙
>
> 白日依山盡，黃河入海流。
> 欲窮千里目，更上一層樓。
> ```

## 安裝

### 1. 安裝依賴

執行 `make` / `make install` 前需安裝 fortune、OpenCC，以及 YAML 解析依賴（Ruby 或 PyYAML）：

- Ubuntu / Debian：`sudo apt install fortune-mod opencc python3-yaml`
- Arch Linux：`sudo pacman -S fortune-mod opencc python-yaml`
- macOS（Homebrew）：`brew install fortune opencc`（另需 `pip3 install pyyaml`，或安裝 Ruby）

> Debian / Ubuntu 上 `fortune` 位於 `/usr/games`；若命令找不到，請確認 `PATH` 含 `/usr/games`。

### 2. 安裝本詩詞庫

**Arch Linux (AUR)**

```bash
yay -S fortune-mod-zh-gushici
```

**用 make 安裝**

```bash
make            # 從 gushici.yaml 生成 data/（等同 make compile）
make install    # 先 compile，再安裝文本並用本機 strfile 生成 .dat
```

安裝目錄由 `FORTUNE_DIR` 決定（若未設定，則由 `PREFIX` 推導）：

```bash
# 使用者目錄（推薦）：先設定環境變數，再 make install
export FORTUNE_DIR=$HOME/.local/share/fortunes
make install

# 系統目錄（通常需要 sudo）
sudo make install

# 若已 export FORTUNE_DIR 但仍需 sudo，請保留環境變數，否則 sudo 會清掉它：
sudo --preserve-env=FORTUNE_DIR make install
# 或：sudo -E make install
```

> 請用 `$HOME/...`，不要依賴 `~`（Make 對波浪號支援有限）。
>
> `make install` 只寫入 `gushici-cht`、`gushici-chs` 及其 `.dat`，不會清空整個 fortune 目錄。

- 預設（未設 `FORTUNE_DIR` / `PREFIX`）：
  - macOS (Homebrew)：`$(brew --prefix fortune)/share/games/fortunes/`
  - Arch Linux：`/usr/local/share/fortune/`
  - Debian / Ubuntu：`/usr/local/share/games/fortunes/`
- `PREFIX=/usr`（且未設 `FORTUNE_DIR`）：
  - Arch：`/usr/share/fortune/`
  - Debian / Ubuntu：`/usr/share/games/fortunes/`

```bash
make install PREFIX=/path/to/prefix
make install FORTUNE_DIR=$HOME/.local/share/fortunes
make install DESTDIR=/path/to/stage PREFIX=/usr
```

**手動安裝**

```bash
make compile
cp data/gushici-cht data/gushici-chs /path/to/fortunes/
strfile -c % /path/to/fortunes/gushici-cht /path/to/fortunes/gushici-cht.dat
strfile -c % /path/to/fortunes/gushici-chs /path/to/fortunes/gushici-chs.dat
```

## 登入自動顯示

在 `~/.bashrc` 或 `~/.zshrc` 中加入：

```bash
fortune gushici-cht   # 或 fortune gushici-chs
```

## 相關文檔

- [編輯條目](./編輯條目.md) — 增補/刪改詩詞條目、條目格式、常用命令
- [正字](./正字.md) — 繁體正字規則



## 許可

詩文均為超過一百年歷史的公共領域作品。
