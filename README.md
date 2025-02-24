# Scientific Plot Module

## 项目简介
这是一个用于科研论文绘图的Python模块，采用模块化设计，将数据处理和静态绘图分离，以提供最大的灵活性和可维护性。每个模块都有独立的文档说明其详细实现。

## 核心优势
### 数据处理模块
- **统一的数据格式化系统**
  - 支持多种输入格式（CSV、Excel、文本等）
  - 提供标准化的数据输出接口
  - 灵活的格式转换机制

- **强大的统计分析工具**
  - 基础统计量计算
  - 异常值检测和处理
  - 数据分布分析
  - 相关性分析支持

- **完善的数据验证**
  - 数据类型检查
  - 数值范围验证
  - 完整性校验
  - 自定义验证规则

### 静态绘图模块
- **精确的样式控制**
  - 符合期刊要求的输出质量
  - 精确的字体和尺寸控制
  - 丰富的自定义选项

- **资源管理**
  - 自动内存管理
  - 安全的文件操作
  - 异常保护机制

- **多样的图表支持**
  - 箱型图
  - 散点图
  - 误差线图
  - 分布图

## 系统架构
```
Plot/
├── data_processing/      # 数据处理模块
│   ├── base.py          # 数据处理基础类
│   ├── config.py        # 数据处理配置
│   ├── processor.py     # 处理器实现
│   ├── exceptions.py    # 异常定义
│   └── utils/           # 工具函数
├── static_plot/         # 静态绘图模块
│   ├── base.py         # 绘图基础类
│   ├── plotter.py      # 绘图器实现
│   ├── style.py        # 样式系统
│   ├── config.py       # 绘图配置
│   └── validators.py   # 验证器
└── requirements.txt    # 依赖包列表
```

## 模块设计
### 1. 模块职责
- 数据处理模块
  - 提供统一的数据处理框架
  - 实现数据格式转换和标准化
  - 确保数据质量和格式规范
  - [详细说明](data_processing/README.md)

- 静态绘图模块
  - 提供科研论文级别的图表绘制
  - 实现精确的样式控制系统
  - 支持多种图表类型和布局
  - [详细说明](static_plot/README.md)

### 2. 模块间接口
#### 标准数据格式
```python
{
    "data": {
        "values": Dict[str, List[float]]  # 数据值
    },
    "metadata": {
        "x_label": str,  # X轴标签
        "y_label": str,  # Y轴标签
        "unit": str      # 单位（可选）
    }
}
```

#### 配置系统
- 处理器配置：控制数据处理流程和验证规则
- 绘图配置：管理样式和布局参数
- 配置继承：支持模块间的配置复用和扩展

### 3. 使用流程
```python
from data_processing.config import ProcessorConfig
from data_processing.processor import TableFileProcessor
from data_processing.utils.statistics import StatisticsCalculator
from data_processing.utils.formatters import BoxPlotFormatter
from static_plot.config import BoxPlotConfig
from static_plot.plotter import BoxPlotter

# 1. 数据处理配置
processor_config = ProcessorConfig(
    input_path="data.csv",
    validation_rules={"required_columns": ["A", "B"]}
)

# 2. 数据处理和统计分析
# 格式化数据
formatter = BoxPlotFormatter(
    x_label="类别",
    y_label="数值",
    unit="mm"
)
with TableFileProcessor(processor_config, formatter) as processor:
    # 基础处理
    data = processor.process() # 处理数据、统计分析和格式化
    plot_data = processor.to_standard_format() # 转换为标准格式

# 3. 绘图配置
plot_config = BoxPlotConfig()
plot_config.style.update({
    "style": "ticks",
    "context": "paper"
})

# 4. 绘图
with BoxPlotter(plot_config) as plotter:
    plotter.plot(plot_data)
    plotter.save("output.pdf")
```

## 技术栈
- 数据处理：NumPy, Pandas
- 静态绘图：Matplotlib, Seaborn

## 安装和依赖
```bash
pip install -r requirements.txt
```

## 开发规范
1. 代码风格
   - 遵循PEP 8规范
   - 使用类型注解
   - 编写文档字符串
   - 注释复杂逻辑

2. 测试要求
   - 单元测试覆盖率>80%
   - 包含边界条件测试
   - 验证异常处理
   - 检查资源释放

3. 文档维护
   - 及时更新模块文档
   - 提供使用示例
   - 记录重要变更

## 版本兼容性
- Python >= 3.7
- 具体依赖版本见requirements.txt

## 注意事项
- 确保数据符合标准格式要求
- 使用上下文管理器处理资源
- 参考各模块文档了解详细用法