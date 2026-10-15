#!/usr/bin/env python3
"""Bounded, read-only metadata inventory. Does not execute Elixir/project code."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

EXCLUDED = {'.git', '_build', 'node_modules', '.elixir_ls', '.next', 'vendor', '__pycache__'}
KEY = r'(?:"(?P<quoted>[a-zA-Z0-9_]+)"\s*:|(?P<atom>[a-zA-Z0-9_]+)\s*:)'
HEX = re.compile(KEY + r'\s*\{\s*:hex\s*,\s*(?::[a-zA-Z0-9_]+|:"[^"]+")\s*,\s*"(?P<version>[^"\r\n]+)"')
GIT = re.compile(KEY + r'\s*\{\s*:git\s*,\s*"[^"\r\n]*"\s*,\s*"(?P<revision>[0-9a-fA-F]{7,64})"')
MAX_BYTES = 2_000_000


def parse_lock(text: str) -> list[dict[str, str]]:
    """Extract familiar literal lock entries without evaluating arbitrary expressions."""
    found: dict[str, dict[str, str]] = {}
    for pattern, field, kind in ((HEX, 'version', 'hex'), (GIT, 'revision', 'git')):
        for match in pattern.finditer(text):
            name = match.group('quoted') or match.group('atom')
            found[name] = {'name': name, 'source': kind, field: match.group(field)}
    return [found[name] for name in sorted(found)]


def read_small(path: Path) -> str:
    if path.is_symlink() or path.stat().st_size > MAX_BYTES:
        raise ValueError('symlink or file larger than metadata limit')
    return path.read_text(encoding='utf-8')


def inventory(root: Path, max_files: int = 20000, max_depth: int = 8) -> dict:
    root = root.expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError('root must be a directory')
    if max_files < 1 or max_depth < 0:
        raise ValueError('scan limits must be positive (depth may be zero)')
    result: dict = {
        'root': str(root), 'mix_roots': [], 'lockfiles': [], 'toolchain_pins': [],
        'usage_rule_paths': [], 'candidate_ash_files': [], 'warnings': [],
        'files_seen': 0, 'scan_truncated': False,
        'limitations': [
            'Literal-pattern inventory, not an Elixir parser or a security review.',
            'Path dependencies and computed config require manual inspection.',
            'No project code, network request, Mix task, or secret config is executed/read.',
            'Candidate Ash modules are heuristic. Nested lockfiles may serve different apps.',
            'Dependency directories are searched only for usage-rule filenames, not full source.',
        ],
    }
    locks: list[Path] = []
    dep_roots: list[Path] = []
    def warn(message: str) -> None:
        result['warnings'].append(message)
    def walk_error(error: OSError) -> None:
        result['scan_truncated'] = True
        warn(f'An unreadable directory was skipped ({type(error).__name__}).')
    for directory, dirs, names in os.walk(root, followlinks=False, onerror=walk_error):
        current = Path(directory)
        depth = len(current.relative_to(root).parts)
        allowed = []
        for name in sorted(dirs):
            candidate = current / name
            if candidate.is_symlink() or name in EXCLUDED:
                continue
            if name == 'deps':
                dep_roots.append(candidate)
                continue
            if depth >= max_depth:
                result['scan_truncated'] = True
                continue
            allowed.append(name)
        dirs[:] = allowed
        for name in sorted(names):
            path = current / name
            if path.is_symlink():
                continue
            result['files_seen'] += 1
            if result['files_seen'] > max_files:
                result['scan_truncated'] = True
                break
            rel = path.relative_to(root).as_posix()
            if name == 'mix.exs':
                result['mix_roots'].append(current.relative_to(root).as_posix())
            elif name == 'mix.lock':
                locks.append(path)
            elif name == '.tool-versions':
                try:
                    pins = {}
                    for line in read_small(path).splitlines():
                        parts = line.split('#', 1)[0].split()
                        if len(parts) >= 2 and parts[0] in {'elixir', 'erlang', 'nodejs'}:
                            pins[parts[0]] = ' '.join(parts[1:])
                    result['toolchain_pins'].append({'path': rel, 'pins': pins})
                except (OSError, UnicodeError, ValueError) as exc:
                    warn(f'Cannot inspect {rel}: {type(exc).__name__}')
            elif name.endswith('.ex') and ('lib' in path.relative_to(root).parts):
                try:
                    text = read_small(path)
                    kinds = [kind for kind in ('Ash.Resource', 'Ash.Domain', 'Ash.Scope.ToOpts')
                             if re.search(r'\b' + re.escape(kind) + r'\b', text)]
                    if kinds:
                        result['candidate_ash_files'].append({'path': rel, 'mentions': kinds})
                except (OSError, UnicodeError, ValueError) as exc:
                    warn(f'Cannot inspect {rel}: {type(exc).__name__}')
        if result['files_seen'] > max_files:
            break
    for path in sorted(locks):
        rel = path.relative_to(root).as_posix()
        try:
            text = read_small(path)
            result['lockfiles'].append({'path': rel,
                'sha256': hashlib.sha256(text.encode('utf-8')).hexdigest(),
                'dependencies': parse_lock(text)})
        except (OSError, UnicodeError, ValueError) as exc:
            warn(f'Cannot inspect {rel}: {type(exc).__name__}')
    rule_count = 0
    for deps in dep_roots:
        try:
            packages = sorted(deps.iterdir())
        except OSError:
            warn('A dependency directory could not be listed.')
            continue
        for package in packages:
            if package.is_symlink() or not package.is_dir():
                continue
            main = package / 'usage-rules.md'
            if main.is_file() and not main.is_symlink():
                result['usage_rule_paths'].append(main.relative_to(root).as_posix())
            rules = package / 'usage-rules'
            if not rules.is_dir() or rules.is_symlink():
                continue
            for directory, dirs, names in os.walk(rules, followlinks=False, onerror=walk_error):
                current = Path(directory)
                rule_depth = len(current.relative_to(rules).parts)
                dirs[:] = sorted(d for d in dirs if not (current / d).is_symlink() and rule_depth < 3)
                for name in sorted(names):
                    rule_count += 1
                    if rule_count > 5000:
                        result['scan_truncated'] = True
                        break
                    path = current / name
                    if name.endswith('.md') and not path.is_symlink():
                        result['usage_rule_paths'].append(path.relative_to(root).as_posix())
                if rule_count > 5000:
                    break
            if rule_count > 5000:
                break
        if rule_count > 5000:
            break
    if not result['mix_roots']:
        warn('No mix.exs found within scan limits; choose the actual Mix root.')
    if not result['lockfiles']:
        warn('No mix.lock found; installed dependency versions are not established.')
    result['usage_rule_paths'] = sorted(set(result['usage_rule_paths']))
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--max-files', type=int, default=20000)
    parser.add_argument('--max-depth', type=int, default=8)
    args = parser.parse_args(argv)
    try:
        report = inventory(args.root, args.max_files, args.max_depth)
    except (OSError, ValueError) as exc:
        print(f'Inventory failed: {exc}', file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
