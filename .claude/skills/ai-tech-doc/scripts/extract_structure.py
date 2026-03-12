#!/usr/bin/env python3
"""
extract_structure.py
提取项目目录结构与关键配置信息，供文档生成时使用。

用法：
    python3 scripts/extract_structure.py <项目路径> [--depth <层级>] [--output <输出文件>]

示例：
    python3 scripts/extract_structure.py /home/user/my-rag-project --depth 3
"""

import os
import sys
import json
import argparse
from pathlib import Path

# 忽略的目录和文件
IGNORE_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    "env", ".env", "dist", "build", ".pytest_cache", ".mypy_cache",
    "htmlcov", ".DS_Store", "*.egg-info",
}

IGNORE_EXTENSIONS = {
    ".pyc", ".pyo", ".pyd", ".so", ".dll", ".exe",
    ".log", ".tmp", ".cache", ".lock",
}

# 高价值文件（优先展示）
KEY_FILES = {
    "docker-compose.yml", "docker-compose.yaml",
    "Dockerfile", ".env.example", "requirements.txt",
    "pyproject.toml", "setup.py", "config.yaml", "config.yml",
    "README.md", "README.rst",
}


def should_ignore(path: Path) -> bool:
    if path.name in IGNORE_DIRS:
        return True
    if path.suffix in IGNORE_EXTENSIONS:
        return True
    if path.name.startswith(".") and path.name not in {".env.example"}:
        return True
    return False


def build_tree(root: Path, depth: int, current_depth: int = 0) -> dict:
    """递归构建目录树结构。"""
    if current_depth > depth:
        return {}

    result = {
        "name": root.name,
        "type": "directory" if root.is_dir() else "file",
        "path": str(root),
        "is_key_file": root.name in KEY_FILES,
    }

    if root.is_dir():
        children = []
        try:
            for child in sorted(root.iterdir()):
                if not should_ignore(child):
                    children.append(build_tree(child, depth, current_depth + 1))
        except PermissionError:
            pass
        result["children"] = children

    return result


def extract_docker_compose_info(project_root: Path) -> dict:
    """提取 docker-compose 中的服务和端口信息。"""
    import re

    for name in ("docker-compose.yml", "docker-compose.yaml"):
        compose_file = project_root / name
        if compose_file.exists():
            content = compose_file.read_text(encoding="utf-8")
            services = re.findall(r"^\s{2}(\w[\w-]*):", content, re.MULTILINE)
            ports = re.findall(r'["\'"]?(\d+:\d+)["\'"]?', content)
            return {
                "file": name,
                "services": list(set(services)),
                "port_mappings": list(set(ports)),
            }
    return {}


def extract_env_example(project_root: Path) -> list[str]:
    """提取 .env.example 中的变量名（不含值）。"""
    env_file = project_root / ".env.example"
    if not env_file.exists():
        return []

    variables = []
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key = line.split("=")[0].strip()
            variables.append(key)
    return variables


def extract_python_deps(project_root: Path) -> list[str]:
    """提取 Python 依赖列表。"""
    req_file = project_root / "requirements.txt"
    if req_file.exists():
        deps = []
        for line in req_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("-"):
                # 只取包名，不含版本号
                pkg = line.split("==")[0].split(">=")[0].split("<=")[0].strip()
                deps.append(pkg)
        return deps

    pyproject = project_root / "pyproject.toml"
    if pyproject.exists():
        import re
        content = pyproject.read_text(encoding="utf-8")
        deps = re.findall(r'"([\w-]+)(?:[>=<!\s].*?)?"', content)
        return list(set(deps))

    return []


def main():
    parser = argparse.ArgumentParser(description="提取项目结构信息用于文档生成")
    parser.add_argument("project_path", help="项目根目录路径")
    parser.add_argument("--depth", type=int, default=3, help="目录遍历深度（默认 3）")
    parser.add_argument("--output", help="输出 JSON 文件路径（默认输出到 stdout）")
    args = parser.parse_args()

    root = Path(args.project_path).resolve()
    if not root.exists():
        print(f"错误：路径不存在：{root}", file=sys.stderr)
        sys.exit(1)

    result = {
        "project_name": root.name,
        "project_path": str(root),
        "directory_tree": build_tree(root, args.depth),
        "docker_compose": extract_docker_compose_info(root),
        "env_variables": extract_env_example(root),
        "python_dependencies": extract_python_deps(root),
    }

    output = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"已写入：{args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
