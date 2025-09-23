import os
import re

# Путь к директории проекта vector
project_dir = 'vector-0.47.0'

# Регулярка для поиска атрибутов с clippy
clippy_lint_pattern = re.compile(r'#!\[\s*(allow|warn|deny|forbid)\s*\(([^)]*clippy::[^)]*)\)\s*\]')

# Словарь для хранения найденных линтов
found_lints = {}

# Обход всех файлов в проекте
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
                        if file_path not in found_lints:
                            found_lints[file_path] = []
                        found_lints[file_path].append((level, lints))

# Вывод результатов
for file_path, entries in found_lints.items():
    print(f'\nФайл: {file_path}')
    for level, lints in entries:
        print(f'  Уровень: {level}')
        for lint in lints:
            print(f'    - {lint}')
