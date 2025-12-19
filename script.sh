#!/bin/bash

# ============================================================================
# LibFuzzer Monitor Script
# Отслеживает время с момента последнего найденного уникального пути
# ============================================================================

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Глобальные переменные
LAST_NEW_TIME=$(date +%s)
TIMER_FILE=$(mktemp)
FUZZER_PID=""

# Показать справку
usage() {
    echo "Usage: $0 <target> <corpus_dir> <artifacts_dir> [additional_libfuzzer_args...]"
    echo ""
    echo "Arguments:"
    echo "  target         - Path to the fuzzer executable"
    echo "  corpus_dir     - Directory with corpus files"
    echo "  artifacts_dir  - Directory for crash/timeout artifacts"
    echo ""
    echo "Example:"
    echo "  $0 ./my_fuzzer ./corpus ./artifacts -max_total_time=3600"
    exit 1
}

# Проверка аргументов
if [ $# -lt 3 ]; then
    usage
fi

TARGET="$1"
CORPUS_DIR="$2"
ARTIFACTS_DIR="$3"
shift 3
EXTRA_ARGS="$@"

# Проверка существования таргета
if [ ! -x "$TARGET" ]; then
    echo -e "${RED}Error: Target '$TARGET' not found or not executable${NC}"
    exit 1
fi

# Создание директорий если не существуют
mkdir -p "$CORPUS_DIR"
mkdir -p "$ARTIFACTS_DIR"

# Записать начальное время в файл
echo "$LAST_NEW_TIME" > "$TIMER_FILE"

# Функция для форматирования времени
format_duration() {
    local seconds=$1
    local hours=$((seconds / 3600))
    local minutes=$(((seconds % 3600) / 60))
    local secs=$((seconds % 60))
    printf "%02d:%02d:%02d" $hours $minutes $secs
}

# Фоновый процесс для отображения таймера
timer_display() {
    local last_displayed=""
    while true; do
        if [ -f "$TIMER_FILE" ]; then
            local last_new=$(cat "$TIMER_FILE" 2>/dev/null || echo "$LAST_NEW_TIME")
            local now=$(date +%s)
            local elapsed=$((now - last_new))
            local formatted=$(format_duration $elapsed)
            
            # Цвет в зависимости от времени
            local color=$GREEN
            if [ $elapsed -gt 300 ]; then  # > 5 минут
                color=$YELLOW
            fi
            if [ $elapsed -gt 1800 ]; then  # > 30 минут
                color=$RED
            fi
            
            # Сохраняем позицию, переходим в верхний правый угол, выводим таймер
            tput sc
            tput cup 0 $(($(tput cols) - 35))
            echo -ne "${color}⏱ Time since last NEW: ${formatted}${NC}"
            tput rc
        fi
        sleep 1
    done
}

# Очистка при выходе
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping fuzzer...${NC}"
    
    # Убить таймер
    if [ -n "$TIMER_PID" ]; then
        kill $TIMER_PID 2>/dev/null || true
    fi
    
    # Убить фаззер
    if [ -n "$FUZZER_PID" ]; then
        kill $FUZZER_PID 2>/dev/null || true
    fi
    
    # Удалить временный файл
    rm -f "$TIMER_FILE"
    
    # Показать финальную статистику
    echo ""
    echo -e "${CYAN}============================================${NC}"
    echo -e "${CYAN}Fuzzing session ended${NC}"
    echo -e "${CYAN}============================================${NC}"
    
    tput cnorm  # Показать курсор
    exit 0
}

trap cleanup EXIT INT TERM

# Очистить экран и показать заголовок
clear
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}LibFuzzer Monitor${NC}"
echo -e "${CYAN}============================================${NC}"
echo -e "${BLUE}Target:${NC}     $TARGET"
echo -e "${BLUE}Corpus:${NC}     $CORPUS_DIR"
echo -e "${BLUE}Artifacts:${NC}  $ARTIFACTS_DIR"
echo -e "${BLUE}Extra args:${NC} $EXTRA_ARGS"
echo -e "${CYAN}============================================${NC}"
echo ""

# Запустить фоновый таймер
timer_display &
TIMER_PID=$!

# Запустить фаззер и обрабатывать вывод
"$TARGET" "$CORPUS_DIR" \
    -artifact_prefix="$ARTIFACTS_DIR/" \
    $EXTRA_ARGS 2>&1 | while IFS= read -r line; do
    
    # Проверить, содержит ли строка "NEW" (новый путь найден)
    if echo "$line" | grep -qE "^\s*#[0-9]+\s+NEW"; then
        # Обновить время последнего нового пути
        date +%s > "$TIMER_FILE"
        echo -e "${GREEN}$line${NC}"
    
    # Подсветить REDUCE
    elif echo "$line" | grep -qE "^\s*#[0-9]+\s+REDUCE"; then
        echo -e "${CYAN}$line${NC}"
    
    # Подсветить краши и таймауты
    elif echo "$line" | grep -qiE "(crash|timeout|oom|deadly|error)"; then
        echo -e "${RED}$line${NC}"
    
    # Обычный вывод
    else
        echo "$line"
    fi
done

# Сохранить PID фаззера (для while pipe это сложнее, поэтому cleanup сработает по завершению)
wait
