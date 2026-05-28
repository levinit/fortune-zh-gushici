PREFIX ?= /usr/local
FORTUNE_ANSI ?= yes
BREW_FORTUNE_PREFIX := $(shell brew --prefix fortune 2>/dev/null)
BUILD_FLAGS :=
ifneq ($(FORTUNE_ANSI),no)
  BUILD_FLAGS += --ansi
endif

ifeq ($(origin FORTUNE_DIR),undefined)
  ifeq ($(origin PREFIX),command line)
    FORTUNE_DIR := $(PREFIX)/share/games/fortunes
  else ifneq ($(BREW_FORTUNE_PREFIX),)
    FORTUNE_DIR := $(BREW_FORTUNE_PREFIX)/share/games/fortunes
  else
    FORTUNE_DIR := $(PREFIX)/share/games/fortunes
  endif
endif

.PHONY: all compile install dev clean list check

all: install

# 直接安裝預編譯文件到 fortune 數據目錄（需已安裝 fortune）
install:
	@echo "正在安裝文件到 $(FORTUNE_DIR)..."
	mkdir -p $(FORTUNE_DIR)
	cp data/gushici-cht data/gushici-cht.dat $(FORTUNE_DIR)/
	cp data/gushici-chs data/gushici-chs.dat $(FORTUNE_DIR)/
	@echo "安裝成功！可以使用 'fortune gushici-cht' 或 'fortune gushici-chs' 執行。"

# 生成 data/ 與索引（需要 python3、opencc、strfile，並且需安裝 Ruby 或 PyYAML）
compile:
	@for cmd in python3 strfile opencc; do \
		if ! command -v $$cmd >/dev/null 2>&1; then \
			echo "錯誤: 未找到命令 '$$cmd'，請先安裝"; \
			echo "  Ubuntu/Debian: sudo apt install fortune-mod opencc"; \
			echo "  Arch Linux: sudo pacman -S fortune-mod opencc"; \
			echo "  macOS(Homebrew): brew install fortune opencc"; \
			exit 1; \
		fi; \
	done
	@command -v ruby >/dev/null 2>&1 || { \
		python3 -c 'import importlib.util; raise SystemExit(0 if importlib.util.find_spec("yaml") else 1)' >/dev/null 2>&1 || { \
			echo "錯誤: 需要 Ruby 或 PyYAML 來解析 gushici.yaml"; \
			echo "  安裝 Ruby，或執行: python3 -m pip install pyyaml"; \
			exit 1; \
		}; \
	}
	@echo ">>> 1. 正在從 YAML 生成繁體文本 (data/gushici-cht)..."
	@python3 build.py $(BUILD_FLAGS)
	@echo ">>> 2. 正在編譯繁體版索引 (data/gushici-cht.dat)..."
	@strfile data/gushici-cht data/gushici-cht.dat
	@echo ">>> 3. 正在通過 OpenCC 生成簡體文本 (data/gushici-chs)..."
	@opencc -i data/gushici-cht -o data/gushici-chs -c t2s.json
	@echo ">>> 4. 正在編譯簡體版索引 (data/gushici-chs.dat)..."
	@strfile data/gushici-chs data/gushici-chs.dat
	@echo ""
	@echo "============================================="
	@echo "  編譯完成！"
	@echo "  本地測試繁體: fortune data/gushici-cht"
	@echo "  本地測試簡體: fortune data/gushici-chs"
	@echo "============================================="

# 編譯後安裝
dev: compile install

# 列出所有詩詞條目
list:
	@python3 build.py --list

# 按關鍵詞搜尋已有條目（避免重複添加）
# 用法: make check KEYWORD=李白
check:
	@python3 build.py --check "$(KEYWORD)"

# 清理生成的派生文件
clean:
	rm -f data/gushici-cht data/gushici-cht.dat data/gushici-chs data/gushici-chs.dat
