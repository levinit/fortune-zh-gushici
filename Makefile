PREFIX ?= /usr/local
DESTDIR ?=
FORTUNE_ANSI ?= yes
BREW_FORTUNE_PREFIX := $(shell brew --prefix fortune 2>/dev/null)
BUILD_FLAGS :=
ifneq ($(FORTUNE_ANSI),no)
  BUILD_FLAGS += --ansi
endif

# Arch Linux 使用 share/fortune；Debian/Ubuntu 等使用 share/games/fortunes
IS_ARCH := $(shell [ -f /etc/arch-release ] && echo yes || echo no)

# FORTUNE_DIR：僅當未由環境變數或 make 命令列指定時，才依 PREFIX / Homebrew / 系統推導
_fortune_dir_origin := $(origin FORTUNE_DIR)
ifeq ($(_fortune_dir_origin),environment)
  FORTUNE_DIR_SOURCE := env
else ifeq ($(_fortune_dir_origin),command line)
  FORTUNE_DIR_SOURCE := command
else
  FORTUNE_DIR_SOURCE := default
  ifeq ($(origin PREFIX),command line)
    ifeq ($(IS_ARCH),yes)
      FORTUNE_DIR := $(PREFIX)/share/fortune
    else
      FORTUNE_DIR := $(PREFIX)/share/games/fortunes
    endif
  else ifneq ($(BREW_FORTUNE_PREFIX),)
    FORTUNE_DIR := $(BREW_FORTUNE_PREFIX)/share/games/fortunes
  else ifeq ($(IS_ARCH),yes)
    FORTUNE_DIR := $(PREFIX)/share/fortune
  else
    FORTUNE_DIR := $(PREFIX)/share/games/fortunes
  endif
endif

.PHONY: all compile install dev clean list check

all: compile

# 只安裝本專案的 gushici-*（及以本機 strfile 生成的 .dat），不清空整個目錄。
# data/ 不在倉庫中，故依賴 compile。
install: compile
	@if ! command -v strfile >/dev/null 2>&1; then \
		echo "錯誤: 未找到命令 'strfile'，請先安裝 fortune（strfile 隨 fortune 一起安裝）"; \
		exit 1; \
	fi
	@case "$(FORTUNE_DIR_SOURCE)" in \
	  env) echo "FORTUNE_DIR=$(FORTUNE_DIR)（來自已 export 的環境變數）" ;; \
	  command) echo "FORTUNE_DIR=$(FORTUNE_DIR)（來自 make 命令列，例如 make install FORTUNE_DIR=...）" ;; \
	  *) echo "FORTUNE_DIR=$(FORTUNE_DIR)（未由環境/命令列指定，依 PREFIX、Homebrew 或系統預設推導）" ;; \
	esac
	@echo "正在安裝文件到 $(DESTDIR)$(FORTUNE_DIR)/ ..."
	mkdir -p $(DESTDIR)$(FORTUNE_DIR)
	cp data/gushici-cht data/gushici-chs $(DESTDIR)$(FORTUNE_DIR)/
	strfile -c % $(DESTDIR)$(FORTUNE_DIR)/gushici-cht $(DESTDIR)$(FORTUNE_DIR)/gushici-cht.dat
	strfile -c % $(DESTDIR)$(FORTUNE_DIR)/gushici-chs $(DESTDIR)$(FORTUNE_DIR)/gushici-chs.dat
	@echo "安裝成功！可以使用 'fortune gushici-cht' 或 'fortune gushici-chs' 執行。"

# 需要 python3、opencc、strfile，以及 Ruby 或 PyYAML
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

dev: install

list:
	@python3 build.py --list

# 用法: make check KEYWORD=李白
check:
	@python3 build.py --check "$(KEYWORD)"

clean:
	rm -f data/gushici-cht data/gushici-cht.dat data/gushici-chs data/gushici-chs.dat
