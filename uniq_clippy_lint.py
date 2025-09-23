import os
import re
from collections import defaultdict

# Путь к директории проекта vector
project_dir = 'vector-0.47.0'

# Регулярное выражение для поиска clippy-атрибутов
clippy_lint_pattern = re.compile(r'#!\[\s*(allow|warn|deny|forbid)\s*\(([^)]*clippy::[^)]*)\)\s*\]')

# Словарь для хранения уникальных линтов по категориям
clippy_lints_by_level = defaultdict(set)

# Обход всех .rs файлов в проекте
for root, _, files in os.walk(project_dir):
    for file in files:
        if file.endswith('.rs'):
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    match = clippy_lint_pattern.search(line)
                    if match:
                        level = match.group(1)
                        lints = [lint.strip() for lint in match.group(2).split(',') if 'clippy::' in lint]
                        for lint in lints:
                            clippy_lints_by_level[level].add(lint)

# Вывод результатов
print("\n Уникальные lint-правила Clippy, найденные в vector-0.47.0:\n")

for level in ['allow', 'warn', 'deny', 'forbid']:
    lints = sorted(clippy_lints_by_level[level])
    print(f"{level.upper()} ({len(lints)}):")
    for lint in lints:
        print(f"  - {lint}")
    print()
