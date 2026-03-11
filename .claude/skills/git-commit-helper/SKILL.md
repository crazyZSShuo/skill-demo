---
name: git-commit-helper
description: >
  帮助生成符合 Conventional Commits 规范的 Git 提交信息。
  当用户请求生成提交信息、写 commit message、规范化 git 提交，
  或运行 git commit 相关操作时，务必激活此 Skill。
---

# Git Commit Helper

## Quick Reference

| 操作 | 命令 |
|------|------|
| 查看暂存变更 | `git diff --staged` |
| 查看全部变更 | `git diff HEAD` |
| 提交 | `git commit -m "<message>"` |

## Conventional Commits 规范

格式：`<type>(<scope>): <subject>`

**type 枚举值：**
`feat` / `fix` / `docs` / `style` / `refactor` / `test` / `chore` / `perf` / `ci`

## 执行步骤

1. 运行 `git diff --staged` 获取暂存区变更
2. 若暂存区为空，改用 `git diff HEAD`，并提示用户先执行 `git add`
3. 分析变更，确定 `type`、`scope`（可省略）和 `subject`（≤50 字符，动词原形开头）
4. 变更复杂时，追加 body 段落（每行 ≤72 字符）
5. 有破坏性变更时，footer 注明 `BREAKING CHANGE:` 并在 type 后加 `!`
6. 如需查看完整示例，Read [references/examples.md]
7. 如需处理复杂破坏性变更，Read [references/breaking-changes-guide.md]

## 输出规范
- 仅输出最终提交信息文本，不添加解释
- 多个合理选项时，提供 2-3 个备选并简要说明差异

## 注意事项
- `subject` 使用英文，首字母小写
- 用户要求中文时，`subject` 可用中文，但 `type` 保持英文
- 变更涉及 10+ 个文件且类型混杂时，建议用户拆分提交
