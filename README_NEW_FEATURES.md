# 🚀 多厂商 API Key 扫描器 - 重构升级版

## ✨ 新功能亮点

### 🏭 多厂商支持
现在支持扫描以下厂商的 API Keys：
- **OpenAI** - GPT-3/4 API Keys 
- **Google Gemini** - Gemini AI API Keys
- **硅基流动 (SiliconFlow)** - 中文AI模型API Keys

### 📊 模块化架构
- 每个厂商拥有独立的扫描模块
- 独立的数据库文件管理
- 可扩展的厂商插件系统

### 🎯 智能选择
启动时提供交互式菜单，支持：
- 选择单个厂商扫描
- 全厂商同时扫描
- 命令行预选择厂商

## 🛠️ 使用方法

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动扫描器
```bash
# 交互式选择厂商
python src/main.py

# 预选择特定厂商
python src/main.py --vendor openai     # 仅扫描 OpenAI
python src/main.py --vendor gemini     # 仅扫描 Gemini
python src/main.py --vendor siliconflow # 仅扫描硅基流动
python src/main.py --vendor all       # 扫描所有厂商

# 仅检查已存在的 keys
python src/main.py --check-existed-keys-only

# 检查配额不足的 keys
python src/main.py --check-insuffcient-quota
```

### 重新检查无效 Keys
```bash
# 重新检查所有厂商的无效 keys
python src/recheck_unavailable_keys.py --vendor all

# 重新检查特定厂商
python src/recheck_unavailable_keys.py --vendor openai
python src/recheck_unavailable_keys.py --vendor gemini
python src/recheck_unavailable_keys.py --vendor siliconflow
```

### 测试系统
```bash
# 运行完整测试套件
python test_vendors.py
```

## 📁 数据库文件
每个厂商使用独立的数据库：
- `openai_keys.db` - OpenAI API Keys
- `gemini_keys.db` - Gemini API Keys  
- `siliconflow_keys.db` - 硅基流动 API Keys

## 🔧 技术架构

### 厂商模块结构
```
src/vendors/
├── base.py                 # 厂商基类
├── openai/
│   ├── __init__.py
│   └── vendor.py          # OpenAI 实现
├── gemini/
│   ├── __init__.py
│   └── vendor.py          # Gemini 实现
└── silicon_flow/
    ├── __init__.py
    └── vendor.py          # 硅基流动 实现
```

### 核心组件
- `vendor_factory.py` - 厂商工厂和选择器
- `manager.py` - 数据库和进度管理
- `utils.py` - 工具函数
- `main.py` - 主扫描器

## 🎨 支持的 API Key 格式

### OpenAI
- 经典格式: `sk-[20字符]T3BlbkFJ[20字符]`
- 项目密钥: `sk-proj-[64字符]`  
- 组织密钥: `sk-[48字符]`

### Google Gemini
- 标准格式: `AIzaSy[33字符]`

### 硅基流动 (SiliconFlow)
- 标准格式: `sk-[48个小写字母]`

## 🚀 扩展新厂商

要添加新的厂商支持：

1. 在 `src/vendors/` 下创建新厂商目录
2. 继承 `BaseVendor` 类实现：
   - `get_vendor_name()` - 厂商名称
   - `get_regex_patterns()` - 正则表达式
   - `validate_key()` - 验证方法
   - `get_search_keywords()` - 搜索关键词
3. 在 `vendor_factory.py` 中注册新厂商

## 📈 性能优化

- 多线程并发验证 (最大10个线程)
- 独立数据库避免冲突
- 增量扫描支持
- 智能去重机制

## 🔒 安全特性

- API Key 加密存储
- 敏感信息脱敏显示
- 安全的验证请求
- 错误处理和重试机制

## 📝 变更日志

### v2.0.0 (当前版本)
- ✅ 多厂商架构重构
- ✅ 独立数据库管理
- ✅ 交互式厂商选择
- ✅ 硅基流动厂商支持
- ✅ 模块化代码组织
- ✅ 完整测试套件

### v1.0.0 (原版本)
- 仅支持 Gemini API Key 扫描
- 单一数据库
- 硬编码配置

## 🤝 贡献

欢迎提交 Pull Request 来添加新的厂商支持或改进现有功能！

## 📄 许可证

请参考项目根目录下的 LICENSE 文件。 