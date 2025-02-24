# 静态绘图模块开发者文档

## 1. 模块概述

### 1.1 设计目标
- 提供科研论文级别的静态图表绘制功能
- 确保图表质量符合学术出版标准
- 提供灵活且可扩展的绘图框架
- 实现样式的精确控制和标准化

### 1.2 核心特性
- 标准化的绘图流程
- 精确的样式控制系统
- 灵活的配置管理
- 完善的异常处理
- 资源安全管理

### 1.3 主要应用场景
- 学术论文图表绘制
- 实验数据可视化
- 科研报告制作
- 数据分析结果展示

## 2. 架构设计

### 2.1 整体架构
```
static_plot/
├── base/                 # 基础组件
│   ├── base_plotter.py  # 基础绘图器
│   ├── base_config.py   # 基础配置系统
│   ├── base_style.py    # 基础样式系统
│   └── validators.py    # 数据和配置验证
├── box_plot/            # 箱型图组件
│   ├── box_config.py    # 箱型图配置
│   ├── box_plotter.py   # 箱型图绘制器
│   └── box_style.py     # 箱型图样式
└── other_plots/         # 其他图表类型（未来扩展）
```

### 2.2 核心组件关系
```
基础组件 (base/)
    BasePlotter (base_plotter.py)
    ├── 使用 -> BaseConfig (base_config.py)
    ├── 调用 -> BaseStyleManager (base_style.py)
    └── 使用 -> Validators (validators.py)

箱型图组件 (box_plot/)
    BoxPlotter (box_plotter.py)
    ├── 继承 -> BasePlotter
    ├── 使用 -> BoxPlotConfig (box_config.py)
    └── 调用 -> BoxStyleManager (box_style.py)
```

### 2.3 数据流
1. 数据输入 -> 数据验证
2. 配置加载 -> 配置验证
3. 图形创建 -> 数据准备
4. 绘图实现 -> 样式应用
5. 元素添加 -> 布局调整
6. 图形输出

## 3. 组件说明

### 3.1 基础组件 (base/)
- **基础绘图器** (base_plotter.py)
  - 定义标准绘图流程
  - 提供资源管理机制
  - 实现异常处理框架
  - 管理图形生命周期

- **基础配置** (base_config.py)
  - 定义配置基类
  - 提供配置继承机制
  - 实现配置验证
  - 支持配置模板

- **基础样式** (base_style.py)
  - 定义样式管理基类
  - 提供样式继承机制
  - 实现基础样式应用
  - 支持样式扩展

### 3.2 箱型图组件 (box_plot/)
- **箱型图配置** (box_config.py)
  - 继承基础配置
  - 定义箱型图参数
  - 提供参数验证
  - 支持样式定制

- **箱型图绘制器** (box_plotter.py)
  - 继承基础绘图器
  - 实现箱型图绘制
  - 处理特定样式
  - 管理数据转换

- **箱型图样式** (box_style.py)
  - 继承基础样式
  - 实现特定样式
  - 处理分组样式
  - 管理颜色方案

## 4. 使用指南

### 4.1 基本使用流程
```python
from static_plot.box_plot.box_config import BoxPlotConfig
from static_plot.box_plot.box_plotter import BoxPlotter

# 1. 创建配置
config = BoxPlotConfig()

# 2. 准备数据
data = {
    "data": {
        "values": {
            "组A": [1, 2, 3, 4, 5],
            "组B": [2, 3, 4, 5, 6]
        }
    },
    "metadata": {
        "x_label": "组别",
        "y_label": "数值",
        "unit": "mm"
    }
}

# 3. 创建绘图器并绘图
with BoxPlotter(config) as plotter:
    plotter.plot(data)
    plotter.save("output.pdf")
```

### 4.2 配置说明
- **配置层次关系**：
  ```
  BoxPlotConfig
  ├── style (StyleConfig)
  │   ├── style: str          # 基础样式
  │   │   ├── "ticks"     -> tick_params, spine_*
  │   │   ├── "white"     -> spine_*
  │   │   └── "whitegrid" -> grid_params
  │   ├── context: str        # 上下文环境
  │   │   ├── "paper"     -> 紧凑型布局
  │   │   └── "talk"      -> 演示型布局
  │   ├── font_params: dict   # 字体设置
  │   └── rc_params: dict     # 自定义参数
  │
  ├── element (ElementConfig)
  │   ├── title: str         # 标题
  │   ├── xlabel: str        # X轴标签
  │   ├── ylabel: str        # Y轴标签
  │   └── tick_params: dict  # 刻度设置
  │
  └── box_params: dict        # 箱型图参数
      ├── width: float       # 箱体宽度
      ├── notch: bool        # 凹槽显示
      └── showfliers: bool   # 异常点显示
  ```

- **关键配置项及其影响**：
  - `figsize`: 决定图表物理尺寸
  - `dpi`: 影响输出质量
  - `font_params`: 控制文字样式
  - `style`: 设置整体风格

### 4.3 数据格式要求
- **标准数据格式**：
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

## 5. 扩展开发指南

### 5.1 创建新的图表类型
1. 创建新的图表目录
   ```
   static_plot/
   └── new_plot/
       ├── new_config.py
       ├── new_plotter.py
       └── new_style.py
   ```

2. 实现必要的类
   ```python
   # new_config.py
   from static_plot.base.base_config import BasePlotConfig
   
   class NewPlotConfig(BasePlotConfig):
       pass
   
   # new_plotter.py
   from static_plot.base.base_plotter import BasePlotter
   
   class NewPlotter(BasePlotter):
       pass
   
   # new_style.py
   from static_plot.base.base_style import BaseStyleManager
   
   class NewStyleManager(BaseStyleManager):
       pass
   ```

### 5.2 开发规范
- 遵循基类接口规范
- 实现必要的抽象方法
- 提供完整的单元测试
- 编写详细的文档说明

## 6. 注意事项

### 6.1 导入路径
- 使用绝对导入
- 避免循环依赖
- 保持导入层次清晰
- 遵循模块化原则

### 6.2 配置继承
- 遵循基类约定
- 保持向后兼容
- 验证配置有效性
- 文档化新增参数

### 6.3 样式管理
- 基础样式优先
- 特定样式补充
- 避免样式冲突
- 保持风格一致

## 7. 版本兼容性

### 7.1 依赖要求
- Python >= 3.7
- matplotlib >= 3.3.0
- seaborn >= 0.11.0

### 7.2 版本特性
- v0.1.0: 基础功能实现
- v0.2.0: 模块化重构
- v0.3.0: 样式系统优化

## 8. 开发计划

### 8.1 近期计划
- [ ] 完善基础组件文档
- [ ] 添加散点图支持
- [ ] 添加误差线图支持
- [ ] 优化样式系统

### 8.2 长期目标
- [ ] 支持更多图表类型
- [ ] 提供图表组合功能
- [ ] 增加交互式调整
- [ ] 优化性能

## 9. 常见问题

### 9.1 样式调整
- Q: 如何调整图表尺寸？
- A: 通过修改 `config.style.figsize` 参数

### 9.2 数据处理
- Q: 如何处理异常值？
- A: 通过配置 `box_params.showfliers` 控制

### 9.3 布局优化
- Q: 如何处理标签重叠？
- A: 调整 `figsize` 或使用 `tick_params`
  
### 9.4 字体设置
- Q: 如何设置字体？
- A: 通过修改 `config.style.rc_params` 参数，参考[seaborn issue 1009][seaborn_issue_1009]
  ```python
  sns.set_theme(rc=self.config.style.rc_params)
  ```

## 10. 重要注意事项

### 10.1 样式系统依赖关系
- **基础样式与参数的关系**：
  ```python
  # 正确的使用方式
  config.style.style = "whitegrid"  # 先设置网格样式
  config.style.grid = True          # 然后才能修改网格参数
  config.style.grid_params = {      # 网格参数才会生效
      "linestyle": "--",
      "alpha": 0.3
  }
  
  # 错误的使用方式
  config.style.style = "white"      # 使用无网格样式
  config.style.grid = True          # 网格设置将不会生效
  ```

- **样式参数生效条件**：
  | 样式参数 | 依赖的基础样式 | 说明 |
  |---------|--------------|------|
  | grid_params | whitegrid | 需要先启用网格样式 |
  | tick_params | ticks | 需要先启用刻度样式 |
  | spine_* | white/ticks | 边框参数在这些样式下生效 |

### 10.2 样式优先级
- **样式应用顺序**：
  1. 基础样式 (style)
  2. 上下文设置 (context)
  3. 字体参数 (font_params)
  4. 具体元素样式
  5. 自定义RC参数

- **避免样式冲突**：
  ```python
  # 推荐的样式设置顺序
  config = BoxPlotConfig()
  config.style.style = "ticks"      # 1. 设置基础样式
  config.style.context = "paper"    # 2. 设置上下文
  config.style.font_params = {      # 3. 设置字体
      "family": "Arial",
      "size": 8
  }
  config.box_params.update({        # 4. 设置具体元素
      "width": 0.5,
      "linewidth": 0.8
  })
  ```

### 10.3 资源管理注意事项
- **内存管理**：
  ```python
  # 推荐：使用上下文管理器
  with BoxPlotter(config) as plotter:
      plotter.plot(data)
      plotter.save("output.pdf")
  # 自动清理资源
  
  # 不推荐：手动管理
  plotter = BoxPlotter(config)
  try:
      plotter.plot(data)
      plotter.save("output.pdf")
  finally:
      plotter.cleanup()  # 容易忘记清理
  ```

### 10.4 配置继承注意事项
- **参数覆盖规则**：
  ```python
  # 基类配置
  base_config = BasePlotConfig()
  base_config.style.font_params["size"] = 8
  
  # 子类配置
  box_config = BoxPlotConfig()
  # 注意：某些参数会被子类默认值覆盖
  # 需要在子类实例化后重新设置
  box_config.style.font_params["size"] = 8
  ```

### 10.5 数据验证注意事项
- **数据格式检查**：
  ```python
  # 正确的数据格式
  data = {
      "data": {"values": {"A": [1, 2, 3]}},
      "metadata": {
          "x_label": "类别",
          "y_label": "值",
          "unit": "mm"  # 单位是可选的
      }
  }
  
  # 常见错误
  data = {
      "data": {"values": [1, 2, 3]},  # 错误：values必须是字典
      "metadata": {"x_label": "类别"}  # 错误：缺少y_label
  }
  ```

### 10.6 性能优化注意事项
- **大数据集处理**：
  ```python
  # 推荐：数据量大时进行采样
  import numpy as np
  
  def sample_data(data, max_points=1000):
      if len(data) > max_points:
          indices = np.linspace(0, len(data)-1, max_points, dtype=int)
          return [data[i] for i in indices]
      return data
  
  # 使用采样数据
  sampled_values = {k: sample_data(v) for k, v in data["values"].items()}
  ```

## 11. 参考资料
- [seaborn documentation][seaborn_doc]
- [matplotlib documentation][matplotlib_doc]
- [seaborn issue 1009][seaborn_issue_1009]

[seaborn_doc]: https://seaborn.pydata.org/api.html
[matplotlib_doc]: https://matplotlib.org/stable/api/index.html
[seaborn_issue_1009]: https://github.com/mwaskom/seaborn/issues/1009