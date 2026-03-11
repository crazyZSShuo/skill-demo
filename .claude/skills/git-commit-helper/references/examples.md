# Commit Message 示例集合

## 好的示例

### 简单 Bug 修复
```
fix(auth): prevent login bypass with empty password field
```

### 新功能 + Body
```
feat(payments): add support for Alipay payment method

Integrated Alipay SDK v3.2.1. Closes #427
```

### 破坏性变更
```
refactor(api)!: rename user endpoint from /users to /accounts

BREAKING CHANGE: Update all API calls from /api/users to /api/accounts.
```

## 常见错误示例

```
Fixed stuff          ← 无 type，描述模糊
feat: Update         ← subject 过于简短
FEAT(Auth): Fixed bug ← type 应小写；fix 与 feat 混用
```
