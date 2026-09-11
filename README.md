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

### 1. 安裝 fortune 主程式

- Ubuntu / Debian：`sudo apt install fortune-mod`
- Arch Linux：`sudo pacman -S fortune-mod`
- macOS（Homebrew）：`brew install fortune`

### 2. 安裝本詩詞庫

**Arch Linux (AUR)**

```bash
yay -S fortune-mod-zh-gushici
```

**用 make 安裝**

```bash
make install
```

> 💡 是否需要 `sudo` 取決於安裝目錄的寫入權限：
> - **macOS (Homebrew)**：fortune 數據目錄歸用戶所有，直接 `make install` 即可
> - **Linux**：安裝到系統目錄通常需要 `sudo make install`

`make install` 會自動安裝到 fortune 的數據目錄（可用 `fortune -f 2>&1 | head -n 1` 查看）。

- 預設（未指定 `PREFIX`）：
  - macOS (Homebrew)：`$(brew --prefix fortune)/share/games/fortunes/`
  - Arch Linux：`/usr/local/share/fortune/`
  - Debian / Ubuntu：`/usr/local/share/games/fortunes/`
- 系統安裝（指定 `PREFIX=/usr`）：
  - Arch Linux：`/usr/share/fortune/`
  - Debian / Ubuntu：`/usr/share/games/fortunes/`

也可手動指定安裝路徑：

```bash
make install PREFIX=/path/to/prefix
# 或
make install FORTUNE_DIR=/path/to/fortunes
```

**手動安裝**

```bash
make compile   # 生成 data/ 下的文本與索引
cp data/gushici-cht data/gushici-chs /path/to/fortunes/
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
