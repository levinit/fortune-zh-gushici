# fortune-zh-gushici

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

使用前請先安裝 `fortune` 本體；本倉庫只提供詩詞數據文件，不包含 `fortune` 命令本身。

Ubuntu / Debian：

```bash
sudo apt install fortune-mod
```

Arch Linux：

```bash
sudo pacman -S fortune-mod
```

macOS（Homebrew）：

```bash
brew install fortune
```

### 直接使用

倉庫已包含預編譯文件，下載即用：

- `data/gushici-cht` / `data/gushici-cht.dat` — 繁體
- `data/gushici-chs` / `data/gushici-chs.dat` — 簡體

無需重新生成。

### 用 `make` 安裝

在 macOS + Homebrew 下，`make install` 會優先使用：

```bash
"$(brew --prefix fortune)/share/games/fortunes"
```

其他情況下默認安裝到：

```bash
/usr/local/share/games/fortunes
```

執行：

```bash
sudo make install
```

也可以覆蓋安裝目錄：

```bash
sudo make install PREFIX=/path/to/prefix
sudo make install FORTUNE_DIR=/path/to/fortunes
```

若不確定本機 `fortune` 的數據目錄，可先執行：

```bash
fortune -f
```

### 手動安裝

把 `data/` 下的文件拷貝到 `fortune` 的數據目錄即可。

Linux：

```bash
sudo cp data/gushici-cht data/gushici-cht.dat /usr/share/games/fortunes/
sudo cp data/gushici-chs data/gushici-chs.dat /usr/share/games/fortunes/
```

macOS（Homebrew）：

```bash
sudo cp data/gushici-cht data/gushici-cht.dat "$(brew --prefix fortune)/share/games/fortunes/"
sudo cp data/gushici-chs data/gushici-chs.dat "$(brew --prefix fortune)/share/games/fortunes/"
```

## 登入自動顯示

根據需要將以下內容寫入 `~/.bashrc`（Bash）或 `~/.zshrc`（Zsh）中的合適位置：

```bash
# 如果安裝到 fortune 的數據目錄中
fortune gushici-cht
# fortune gushici-chs

# 如果放在自定義目錄
fortune /path/to/gushici-cht
```

## 增補/刪改條目

### 源文件

正式維護請修改 [`gushici.yaml`](gushici.yaml)；其他文件均由它生成。

繁體文本（`gushici-cht`）手工維護，以唐詩宋詞原文正字為準，詳見[正字.md](正字.md)。簡體文本（`gushici-chs`）由 OpenCC 從繁體單向自動生成。

> _若只做本地臨時使用，也可以直接修改 `data/gushici-cht`，再用 `strfile` 生成索引：`strfile data/gushici-cht data/gushici-cht.dat`。_

### 所需工具

- `python3`
- `opencc`
- `strfile`（通常由 `fortune-mod` 提供）
- `ruby`，或可被 Python 載入的 `PyYAML`

Ubuntu / Debian：

```bash
sudo apt install fortune-mod opencc ruby
```

Arch Linux：

```bash
sudo pacman -S fortune-mod opencc ruby
```

macOS（Homebrew）：

```bash
brew install fortune opencc
```

如果不想依賴 Ruby，也可以改用 `PyYAML`：

```bash
python3 -m pip install pyyaml
```

### 常用命令

```bash
make compile   # 重新生成繁簡文本與 .dat 索引
FORTUNE_ANSI=no make compile   # 生成不帶 ANSI 的版本
make dev       # 生成後直接安裝
make list      # 列出所有條目
make check KEYWORD=李白   # 搜尋條目
make clean     # 清理派生文件
```

### 條目格式

源文件頂層是一個 YAML 列表，每首作品為一個列表項。常用欄位：

| 欄位 | 必填 | 說明 |
|------|:---:|------|
| `dynasty` | ✓ | 朝代；未知時用 `_` |
| `authors` | ✓ | 作者列表 |
| `title` | ✓ | 題名列表；後續元素可寫分題、序號或通行小題（如 `["琵琶行", "並序"]`、`["水龍吟", "登建康賞心亭"]`） |
| `body` | ✓ | 正文；原文小序、題序也放入正文 |
| `suffix` | | 署名後綴，如「（節選）」「四首」 |
| `alias` | | 別名，可為字串或列表 |
| `group` | | 分組標記，用於合併多個獨立條目為一個 fortune 條目 |
| `notes` | | 說明文字；記錄簡單的相關資訊 |

**單首作品示例：**

```yaml
- dynasty: "唐"
  authors: ["李白"]
  title: ["靜夜思"]
  body: |-
    床前明月光，疑是地上霜。
    舉頭望明月，低頭思故鄉。
```

**組詩**可存為一個條目；分題、序號寫在正文中，必要時用 `notes` 補充收錄範圍：

```yaml
- dynasty: "唐"
  authors: ["劉禹錫"]
  title: ["金陵五題"]
  body: |-
    其一
    石頭城

    山圍故國周遭在，潮打空城寂寞回。
    淮水東邊舊時月，夜深還過女牆來。

    其二
    烏衣巷

    朱雀橋邊野草花，烏衣巷口夕陽斜。
    舊時王謝堂前燕，飛入尋常百姓家。
  notes:
    - "其一/其二"
```

原文自帶的小序、題序屬於作品正文，放在 `body` 開頭；`notes` 只放編者補充、版本疑義、收錄範圍等外部說明。

**唱和、前後作聯動**等彼此獨立的作品，應分成多個條目；若希望它們在輸出中連在一起，使用 `group` 關聯。相同 `group` 值的條目會合併輸出為同一個 fortune 條目。

`python3 build.py` 默認生成純文字；傳入 `--ansi` 時會生成帶格式的 fortune 文本。`make compile` 默認帶 ANSI，如需關閉，可使用 `FORTUNE_ANSI=no make compile`。終端支援 ANSI 時，題名會加粗、`notes` 會以斜體顯示；又名有則輸出、無則略過。

```text
題名
又名：別名
作者

說明文字

正文
```

分組示例：

```yaml
- dynasty: "宋"
  authors: ["陸游"]
  title: ["釵頭鳳"]
  group: "宋陸游唐婉釵頭鳳"
  body: |-
    紅酥手，黃縢酒，滿城春色宮牆柳。
    ...

- dynasty: "宋"
  authors: ["唐婉"]
  title: ["釵頭鳳"]
  group: "宋陸游唐婉釵頭鳳"
  body: |-
    世情薄，人情惡，雨送黃昏花易落。
    ...
  notes:
    - "傳為唐婉回贈。"
```

## 許可

詩文均為超過一百年歷史的公共領域作品。
