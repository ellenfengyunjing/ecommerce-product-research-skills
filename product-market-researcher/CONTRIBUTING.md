# 贡献指南

感谢你考虑为 Amazon Product Research Toolkit 做出贡献！🎉

---

## 如何贡献

### 报告 Bug

如果你发现了 Bug，请：

1. 搜索 [现有的 Issues](https://github.com/yourusername/amazon-product-researcher/issues) 确保问题尚未被报告
2. 创建一个新的 Issue，包含：
   - 清晰的标题和描述
   - 复现步骤
   - 预期 vs 实际行为
   - 你的环境信息 (Python 版本、操作系统等)
   - 相关的日志或截图

### 提交代码

#### 开发流程

1. **Fork 本仓库**

2. **Clone 你的 Fork**
   ```bash
   git clone https://github.com/yourusername/amazon-product-researcher.git
   cd amazon-product-researcher
   ```

3. **创建特性分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

4. **安装开发依赖**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # 如果存在
   ```

5. **编写代码并测试**
   ```bash
   # 运行测试
   pytest

   # 代码格式
   black .
   flake8 .
   ```

6. **提交更改**
   ```bash
   git add .
   git commit -m "Add: 简洁的提交信息"
   ```

7. **推送到你的 Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **创建 Pull Request**

---

## 代码规范

### Python 代码风格

我们使用以下工具确保代码一致性：

- **Black** - 代码格式化
- **Flake8** - 代码检查
- **Type hints** - 类型提示 (推荐)

```python
# 好的示例
def calculate_profit(revenue: float, cost: float) -> float:
    """计算利润"""
    return revenue - cost

# 避免
def calculate_profit(revenue, cost):
    return revenue - cost
```

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 变量 | 小写下划线 | `review_count` |
| 函数 | 小写下划线 | `get_product_data()` |
| 类名 | 大驼峰 | `ProductAnalyzer` |
| 常量 | 全大写下划线 | `MAX_PRODUCTS` |
| 文件 | 小写下划线 | `market_analyzer.py` |

### 文档字符串

```python
def fetch_amazon_products(keyword: str, limit: int = 100) -> list:
    """
    获取亚马逊商品数据

    Args:
        keyword: 搜索关键词
        limit: 最大采集数量，默认 100

    Returns:
        商品数据列表，每项包含 ASIN、标题、价格等信息

    Raises:
        ValueError: 当 keyword 为空时
        RequestException: 当网络请求失败时

    Example:
        >>> products = fetch_amazon_products("kids vitamins", limit=50)
        >>> len(products)
        50
    """
```

---

## 新增 Skill 规范

如果你想添加新的 Skill，请遵循以下结构：

```
new-skill/
├── SKILL.md           # 必需：Skill 定义
├── README.md          # 推荐：详细文档
├── scripts/          # 必需：Python 脚本
│   └── main.py        # 入口脚本
├── references/        # 可选：参考资料
└── tests/            # 推荐：测试文件
    └── test_main.py
```

### SKILL.md 模板

```markdown
---
name: new-skill
description: 新 Skill 的简要描述
triggers:
  - 触发词1
  - 触发词2
agent_created: true
---

# New Skill Name

## 功能说明

详细的功能描述...

## 使用方法

1. 第一步
2. 第二步

## 参数说明

- `param1`: 参数1说明
- `param2`: 参数2说明
```

---

## Issue 规范

### Bug Report

```markdown
**Bug 描述**
清晰描述问题

**复现步骤**
1. 步骤1
2. 步骤2

**预期行为**
描述期望的结果

**实际行为**
描述实际的结果

**环境信息**
- OS: [e.g. Windows 10]
- Python 版本: [e.g. 3.10.0]
- 工具版本: [e.g. v1.0.0]

**日志**
```
粘贴相关日志
```
```

### Feature Request

```markdown
**功能描述**
清晰描述你想要的功能

**使用场景**
描述这个功能的使用场景

**建议的实现方式**
如果有建议的实现方案

**其他**
任何其他相关信息
```

---

## 感谢

感谢所有为这个项目做出贡献的人！ 🙏

<a href="https://github.com/yourusername/amazon-product-researcher/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=yourusername/amazon-product-researcher" />
</img>
</a>

---

*本贡献指南基于 [Contributor Covenant](https://www.contributor-covenant.org/)*
