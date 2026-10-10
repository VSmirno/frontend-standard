#!/usr/bin/env python3
"""Установка самодостаточного skill без сторонних зависимостей."""

import argparse
import os
from pathlib import Path
import shutil
import sys
import tempfile


def install(destination: Path) -> None:
    source = Path(__file__).resolve().parent
    required = [
        'skills/frontend-standard/SKILL.md',
        'skills/frontend-standard/agents/openai.yaml',
        'standard/VERSION', 'standard/frontend.md', 'pipeline.md',
        'templates/AGENTS.frontend.md', 'templates/adoption.md',
        'templates/audit.md', 'templates/modernization.md',
    ]
    for name in required:
        if not (source / name).is_file():
            raise ValueError(f'Неполный пакет: отсутствует {name}')
    if destination.exists() or destination.is_symlink():
        raise ValueError(
            f'Skill уже установлен: {destination}\n'
            'Существующие файлы сохранены. Для обновления сравните установленный '
            'skill с новой редакцией и сохраните локальные изменения.'
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Собираем рядом с целевым каталогом; до завершения он не виден агенту.
    with tempfile.TemporaryDirectory(prefix='.frontend-install-', dir=destination.parent) as temporary:
        package = Path(temporary) / 'frontend-standard'
        shutil.copytree(source / 'skills/frontend-standard', package)
        references = package / 'references'
        references.mkdir()
        shutil.copytree(source / 'standard', references / 'standard')
        shutil.copytree(source / 'templates', references / 'templates')
        shutil.copy2(source / 'pipeline.md', references / 'pipeline.md')
        if destination.exists() or destination.is_symlink():
            raise ValueError(f'Каталог появился во время установки: {destination}')
        package.rename(destination)
    print(f'Skill установлен: {destination}')
    print('Начните новую сессию агента и используйте $frontend-standard.')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument('--project', type=Path, metavar='PATH', help='корень целевого проекта; . — текущий каталог')
    scope.add_argument('--user', action='store_true', help='личная установка в каталог skills Codex')
    args = parser.parse_args()
    try:
        if args.project is not None:
            project = args.project.expanduser().resolve(strict=True)
            if not project.is_dir():
                raise ValueError(f'Это не каталог проекта: {project}')
            destination = project / '.agents/skills/frontend-standard'
        else:
            codex_root = Path(os.environ.get('CODEX_HOME') or Path.home() / '.codex').expanduser().resolve()
            destination = codex_root / 'skills/frontend-standard'
        install(destination)
    except (OSError, ValueError) as error:
        print(f'Установка не выполнена: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
