# 更新日志

所有重要的更新都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

---

## [3.5.0] - 2026-07-17

### 采集与交付

- Amazon 固定为本地 `amazon-product-scraper` 优先，失败、样本不足或字段缺失时才用 Apify 补采。
- TikTok、Reddit、1688、Google Trends 和市场报告优先使用 Apify Actor，Web Search/Web Fetch 仅兜底。
- 增加有效样本量验收门：Amazon ≥50、TikTok ≥50、Reddit ≥20、1688 ≥20。
- Google Trends 同时交付最近 6 个月数据与趋势截图。
- 新增全面 Excel 总表：标准化分表、`Data_Lineage` 和「原始字段明细」。
- 主流程固定先导出 Excel，再生成独立 HTML 深度报告。

---

## [2.0.0] - 2024-XX-XX

### 🆕 新增功能

- **通用化重构**: 用户只需输入"市场+类目"即可自动运行全流程
- **模块化架构**: 支持独立使用各子 skills
- **环境变量配置**: 统一的 `.env` 配置管理
- **开源准备**: 添加完整文档和贡献指南

### 📦 子 Skills 更新

- `amazon-product-researcher`: 重写为主入口 Skill
- `amazon-product-scraper`: 优化采集逻辑
- `profit-model-builder`: 新增多方案对比功能
- `report-generator`: 支持多种输出格式

### 📚 文档

- 完整项目 README (中英文)
- 配置指南
- 方法论详解
- 常见问题解答
- 贡献指南

---

## [1.0.0] - 2024-05-12

### 🎉 初始版本

- 基于精细化选品方法论的工具链
- 支持 Amazon + TikTok 数据采集
- 利润模型构建
- 报告自动生成

---

## 提交规范

提交信息格式:
```
<类型>: <描述>

[可选的详细说明]
```

类型:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 维护

示例:
```
feat: 添加多市场支持

添加对英国、德国市场的完整支持，
包括本地化关键词和价格区间。
```
