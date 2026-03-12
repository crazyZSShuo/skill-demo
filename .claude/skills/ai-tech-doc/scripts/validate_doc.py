#!/usr/bin/env python3
"""
validate_doc.py
验证生成的技术文档是否符合规范要求。

用法：
    python3 scripts/validate_doc.py <文档路径> [--strict]

返回码：
    0 = 通过
    1 = 有警告
    2 = 有错误
"""

import sys
import re
import argparse
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0


# 禁用词汇表
BANNED_PHRASES = [
    ("简单地", "直接描述操作步骤"),
    ("只需", "直接描述操作步骤"),
    ("请注意", "直接写注意内容，无需前缀"),
    ("众所周知", "直接陈述事实"),
    ("非常简单", "移除或改为具体描述"),
    ("轻松", "移除或改为具体描述"),
    ("笔者认为", "直接陈述结论"),
    ("等等", "列举完整内容"),
    ("诸如此类", "列举完整内容"),
]

# 必须包含的章节（至少有其一）
REQUIRED_SECTION_GROUPS = [
    ["环境要求", "系统要求", "前置条件", "Prerequisites"],
    ["故障排查", "常见问题", "Troubleshooting", "FAQ"],
]


def check_code_blocks(content: str, result: ValidationResult):
    """检查代码块是否都有语言标注。"""
    # 逐行扫描，只检查开启行（前一行不是代码块内容），跳过关闭行
    lines = content.splitlines()
    in_block = False
    bare_count = 0
    for line in lines:
        stripped = line.strip()
        if in_block:
            if stripped == "```":
                in_block = False
        else:
            if stripped.startswith("```"):
                lang = stripped[3:].strip()
                if lang == "":
                    bare_count += 1
                in_block = True
    if bare_count:
        result.errors.append(
            f"发现 {bare_count} 个未标注语言的代码块，请添加语言标识（如 ```bash、```yaml）"
        )


def check_banned_phrases(content: str, result: ValidationResult):
    """检查禁用词汇。"""
    for phrase, suggestion in BANNED_PHRASES:
        if phrase in content:
            occurrences = content.count(phrase)
            result.warnings.append(
                f"禁用表述「{phrase}」出现 {occurrences} 次，建议：{suggestion}"
            )


def check_required_sections(content: str, result: ValidationResult):
    """检查必要章节是否存在。"""
    for group in REQUIRED_SECTION_GROUPS:
        found = any(re.search(rf"#+\s*{re.escape(s)}", content) for s in group)
        if not found:
            result.warnings.append(
                f"建议添加章节：{' / '.join(group)}"
            )


def check_placeholder_variables(content: str, result: ValidationResult):
    """检查命令示例中是否有未替换的占位符。"""
    # 查找常见的遗漏占位符模式（如 YOUR_API_KEY、<your-key> 等）
    suspicious = re.findall(r"\bYOUR_\w+\b", content)
    if suspicious:
        result.warnings.append(
            f"发现可能未替换的占位符：{', '.join(set(suspicious))}，"
            "请改用 <变量名> 格式"
        )


def check_heading_structure(content: str, result: ValidationResult):
    """检查标题层级是否合理。"""
    # 只匹配行首真实标题，排除代码块内的伪标题
    in_code = False
    h1_count = 0
    for line in content.splitlines():
        s = line.strip()
        if s.startswith("```"):
            in_code = not in_code
        if not in_code and re.match(r"^# [^#]", line):
            h1_count += 1
    if h1_count == 0:
        result.errors.append("文档缺少一级标题（# 标题）")
    elif h1_count > 1:
        result.warnings.append(f"文档包含 {h1_count} 个一级标题，建议只保留一个")


def check_empty_sections(content: str, result: ValidationResult):
    """检查是否有空白章节（标题后无内容）。"""
    # 两个连续标题之间没有内容
    empty = re.findall(r"(^#{1,4} .+\n+)(^#{1,4} )", content, re.MULTILINE)
    if empty:
        result.warnings.append(
            f"发现 {len(empty)} 个可能的空白章节，请补充内容或删除章节标题"
        )


def check_doc_length(content: str, result: ValidationResult):
    """检查文档长度是否合理。"""
    word_count = len(content)
    if word_count < 500:
        result.warnings.append(f"文档内容较少（{word_count} 字符），可能信息不完整")
    elif word_count > 20000:
        result.info.append(f"文档较长（{word_count} 字符），考虑拆分为多个文档")


def validate(doc_path: Path, strict: bool = False) -> ValidationResult:
    result = ValidationResult()

    if not doc_path.exists():
        result.errors.append(f"文件不存在：{doc_path}")
        return result

    content = doc_path.read_text(encoding="utf-8")

    check_heading_structure(content, result)
    check_code_blocks(content, result)
    check_banned_phrases(content, result)
    check_required_sections(content, result)
    check_placeholder_variables(content, result)
    check_empty_sections(content, result)
    check_doc_length(content, result)

    return result


def main():
    parser = argparse.ArgumentParser(description="验证技术文档规范性")
    parser.add_argument("doc_path", help="Markdown 文档路径")
    parser.add_argument("--strict", action="store_true", help="警告也视为失败")
    args = parser.parse_args()

    result = validate(Path(args.doc_path), args.strict)

    print(f"\n文档验证报告：{args.doc_path}\n" + "=" * 50)

    if result.errors:
        print("\n[错误]")
        for e in result.errors:
            print(f"  ✗ {e}")

    if result.warnings:
        print("\n[警告]")
        for w in result.warnings:
            print(f"  ⚠ {w}")

    if result.info:
        print("\n[提示]")
        for i in result.info:
            print(f"  ℹ {i}")

    if result.passed and not result.warnings:
        print("\n✓ 文档通过所有检查\n")
    elif result.passed:
        print(f"\n通过（{len(result.warnings)} 个警告）\n")
    else:
        print(f"\n✗ 未通过（{len(result.errors)} 个错误，{len(result.warnings)} 个警告）\n")

    if args.strict:
        sys.exit(0 if result.passed and not result.warnings else 2)
    else:
        sys.exit(0 if result.passed else 2)


if __name__ == "__main__":
    main()
