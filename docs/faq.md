# 常见问题 (FAQ)

本文档解答关于 Amazon Product Research Toolkit 的常见问题。

---

## 🚀 入门问题

### Q1: 如何开始使用这个工具？

**A**: 
1. 克隆项目并安装依赖
2. 配置 Apify API Token
3. 在 WorkBuddy 中输入：`"分析[市场][类目]的选品机会"`
   例如：`"分析美国市场儿童保健品类目的选品机会"`

详细教程请参考 [README.md](README.md)

---

### Q2: 需要付费吗？

**A**: 
- **基础功能**: 免费，使用工具内置的示例数据
- **数据采集**: 需要 Apify API Token
  - 免费配额: 每月有限次数
  - 付费版: $49/月起

---

### Q3: 支持哪些市场？

**A**: 
当前支持:
- 🇺🇸 US (美国) - 完整支持
- 🇬🇧 UK (英国) - 完整支持
- 🇩🇪 DE (德国) - 完整支持
- 🇫🇷 FR (法国) - 完整支持
- 🇮🇹 IT (意大利) - 完整支持
- 🇪🇸 ES (西班牙) - 完整支持
- 🇯🇵 JP (日本) - 基础支持
- 🇨🇦 CA (加拿大) - 基础支持

---

## 📊 数据采集问题

### Q4: 数据采集需要多长时间？

**A**: 
取决于采集范围:

| 采集范围 | 预计时间 |
|----------|----------|
| 单关键词 Top 50 | 5-10 分钟 |
| 单关键词 Top 100 | 15-20 分钟 |
| 5 个关键词 | 1-2 小时 |
| 全链路 (Amazon+TikTok+市场报告) | 2-4 小时 |

---

### Q5: 为什么采集的数据不完整？

**A**: 
可能的原因:
1. **网络问题**: 检查网络连接
2. **IP 被封**: 启用代理或降低请求频率
3. **商品数量不足**: 增加 `max_products` 参数
4. **API 配额不足**: 检查 Apify 账户余额

**解决方案**:
```bash
# 降低请求频率
REQUEST_DELAY=5

# 增加重试次数
RETRY_TIMES=5

# 使用代理
PROXY_ENABLED=true
```

---

### Q6: Apify API Token 是什么？如何获取？

**A**: 
Apify 是一个网页数据采集平台:

1. 访问 [apify.com](https://apify.com)
2. 注册账户
3. 进入 [Console](https://console.apify.com/account/integrations)
4. 复制你的 API Token

免费注册即可获得一定的配额。

---

## 💰 利润计算问题

### Q7: 利润计算是如何进行的？

**A**: 
本工具使用标准亚马逊 FBA 成本结构:

```
售价 - 产品成本 - 平台佣金(15%) - FBA费用 - 广告费 - 退款损耗 = 净利润
```

详细计算公式:
- **毛利率**: (售价 - 产品成本) / 售价
- **净利率**: 净利润 / 售价

---

### Q8: 如何调整成本参数？

**A**: 
编辑 `skills/profit-model-builder/scripts/config.py`:

```python
COST_CONFIG = {
    "product_cost": 5.0,        # 产品成本 (USD)
    "shipping_cost": 0.5,       # 头程运费
    "platform_fee_rate": 0.15,  # 平台佣金率
    "fba_fulfillment_fee": 3.5, # FBA 履约费
    "refund_rate": 0.03,       # 退款率
    "advertising_rate": 0.20,  # 广告占比
}
```

---

## 📝 报告问题

### Q9: 报告支持哪些格式？

**A**: 
当前支持:
- 📄 **Markdown** (默认，推荐)
- 📑 **PDF** (需要 pandoc)
- 📃 **Word** (需要 python-docx)
- 🌐 **HTML** (需要 markdown)

配置方式:
```bash
# .env 文件
OUTPUT_FORMAT=markdown  # 或 pdf, word, html
```

---

### Q10: 报告保存在哪里？

**A**: 
默认保存在:
```
./output/YYYY-MM-DD/报告标题.md
```

可配置输出目录:
```bash
# .env 文件
OUTPUT_DIR=/path/to/output
```

---

## 🔧 技术问题

### Q11: 遇到 "ModuleNotFoundError" 错误

**A**: 
缺少依赖包，解决方案:

```bash
# 重新安装依赖
pip install -r requirements.txt

# 或安装特定包
pip install requests beautifulsoup4
```

---

### Q12: 如何查看详细的日志信息？

**A**: 
启用 DEBUG 模式:

```bash
# .env 文件
DEBUG=true
LOG_LEVEL=DEBUG
```

或在命令行:

```bash
python main.py --debug --market US --category "kids vitamins"
```

---

### Q13: 支持 Docker 吗？

**A**: 
是的！提供了 Dockerfile:

```bash
# 构建镜像
docker build -t amazon-researcher .

# 运行容器
docker run -it --env-file .env amazon-researcher python main.py --market US --category "kids vitamins"
```

Dockerfile 位置: `docker/Dockerfile`

---

## 🤝 贡献问题

### Q14: 如何贡献代码？

**A**: 
请参考 [CONTRIBUTING.md](../CONTRIBUTING.md):

1. Fork 项目
2. 创建特性分支
3. 提交 Pull Request
4. 等待审核

---

### Q15: 如何报告 Bug 或请求新功能？

**A**: 
在 GitHub 上创建 Issue:
- Bug Report: 使用 Bug 模板
- Feature Request: 使用 Feature Request 模板

---

## 📞 其他问题

### Q16: 联系方式？

**A**: 
- GitHub Issues: [点击这里](https://github.com/yourusername/amazon-product-researcher/issues)
- Email: your.email@example.com

---

## ❓ 没有找到答案？

如果本文档没有解答你的问题，请:

1. 搜索 [GitHub Issues](https://github.com/yourusername/amazon-product-researcher/issues)
2. 创建新的 Issue
3. 联系开发者
