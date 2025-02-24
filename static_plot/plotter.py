"""
绘图器实现模块，提供具体的绘图功能。目前实现了BoxPlotter用于绘制箱型图，
支持数据的预处理、样式定制和分组管理。使用标准化的数据格式和配置系统，
确保输出图表符合学术出版标准。
"""

from typing import Any, Dict, List, Optional

import seaborn as sns

from static_plot.base import BasePlotter
from static_plot.config import BoxPlotConfig
from static_plot.style import BoxStyleManager
from static_plot.validators import ConfigValidator, DataValidator


class BoxPlotter(BasePlotter):
    """箱型图绘制器类
    
    本类继承自BasePlotter，实现了箱型图的具体绘制功能。
    
    主要特性：
    - 支持单组和多组数据
    - 自动处理异常值
    - 灵活的样式配置
    - 完整的数据验证
    
    工作流程：
    1. 配置验证：检查绘图参数
    2. 数据处理：格式化输入数据
    3. 图形绘制：创建和绘制图形
    4. 样式应用：设置视觉样式
    5. 元素添加：补充文本标签
    
    属性说明：
        config (BoxPlotConfig): 箱型图配置对象
        data_list (List[Any]): 处理后的数据列表
        labels (List[str]): 数据标签列表
        style_manager (BoxStyleManager): 样式管理器对象
    
    示例：
        ```python
        # 创建绘图器
        config = BoxPlotConfig()
        plotter = BoxPlotter(config)
        
        # 准备数据
        data = {
            "data": {"values": {"A": [1, 2, 3]}},
            "metadata": {
                "x_label": "类别",
                "y_label": "值",
                "unit": "mm"
            }
        }
        
        # 绘制图形
        plotter.plot(data)
        plotter.save("output.pdf")
        ```
    """
    
    def __init__(self, config: Optional[BoxPlotConfig] = None):
        """初始化箱型图绘制器
        
        创建绘图器实例并进行必要的初始化。
        
        Args:
            config: 箱型图配置对象，如果为None则使用默认配置
            
        Raises:
            ValueError: 当配置无效时抛出
            
        示例：
            ```python
            # 使用默认配置
            plotter = BoxPlotter()
            
            # 使用自定义配置
            config = BoxPlotConfig()
            plotter = BoxPlotter(config)
            ```
        """
        super().__init__(config or BoxPlotConfig())
        self.data_list: List[Any] = []  # 存储处理后的数据
        self.labels: List[str] = []  # 存储数据标签
        self.style_manager = BoxStyleManager(self.config)  # 创建样式管理器
    
    def validate_config(self) -> None:
        """验证配置有效性
        
        检查箱型图配置参数是否满足要求。
        
        Raises:
            ValueError: 当配置参数无效时抛出
            
        注意：
            除了基础配置，还会验证箱型图特有的配置
        """
        super().validate_config()
        ConfigValidator.validate_box_config(self.config)
    
    def validate_data(self, data: Dict[str, Any]) -> None:
        """验证数据有效性
        
        检查输入数据是否满足箱型图的要求。
        
        Args:
            data: 输入数据字典，必须包含：
                - data: 包含values字典的数据部分
                - metadata: 包含标签信息的元数据部分
            
        Raises:
            ValueError: 当数据格式或内容无效时抛出
            
        示例：
            ```python
            data = {
                "data": {"values": {"A": [1, 2, 3]}},
                "metadata": {"x_label": "类别", "y_label": "值"}
            }
            plotter.validate_data(data)
            ```
        """
        DataValidator.validate_box_data(data)
        
    @property
    def config(self) -> BoxPlotConfig:
        """获取配置对象
        
        Returns:
            箱型图配置对象
        """
        return self._config
    
    @config.setter
    def config(self, value: BoxPlotConfig) -> None:
        """设置配置对象
        
        更新配置并重新创建样式管理器。
        
        Args:
            value: 新的配置对象
            
        Raises:
            TypeError: 配置类型错误时抛出
            ValueError: 配置无效时抛出
            
        示例：
            ```python
            plotter = BoxPlotter()
            new_config = BoxPlotConfig()
            plotter.config = new_config
            ```
        """
        if not isinstance(value, BoxPlotConfig):
            raise TypeError("配置必须是BoxPlotConfig类型")
        self._config = value
        self.style_manager = BoxStyleManager(value)
        
        # 验证新配置
        self.validate_config()
    
    def prepare_data(self, data: Dict[str, Any]) -> None:
        """准备绘图数据
        
        处理输入数据，提取必要的信息。
        
        Args:
            data: 原始数据字典，包含：
                - data: 数据值
                - metadata: 元数据
                
        示例：
            ```python
            data = {
                "data": {"values": {"A": [1, 2, 3]}},
                "metadata": {
                    "x_label": "类别",
                    "y_label": "值",
                    "unit": "mm"
                }
            }
            plotter.prepare_data(data)
            ```
        """
        values = data["data"]["values"]
        self.data_list = list(values.values())  # 提取数据值
        self.labels = list(values.keys())  # 提取标签
        
        # 设置标签
        x_label = data["metadata"].get("x_label", "类别")
        y_label = data["metadata"].get("y_label", "数值")
        unit = data["metadata"].get("unit", "")
        
        self.config.element.xlabel = self.config.element.xlabel if self.config.element.xlabel else x_label
        self.config.element.ylabel = self.config.element.ylabel if self.config.element.ylabel else (y_label + f" ({unit})" if unit else y_label)
        self.config.element.title = self.config.element.title if self.config.element.title else f"{y_label}按{x_label}的分布"
    
    def draw_plot(self) -> None:
        """绘制箱型图
        
        使用seaborn绘制箱型图并应用样式。
        
        Raises:
            RuntimeError: 绘图失败时抛出
            
        注意：
            - 会自动处理颜色分配
            - 支持多组数据的绘制
        """
        try:
            # 获取样式
            colors = self.config.get_colors(len(self.data_list))
            style_dict = self.config.get_style_dict()
            
            # 绘制箱型图
            sns.boxplot(
                data=self.data_list,
                ax=self.ax,
                palette=colors,
                **style_dict
            )
            
            # 设置刻度标签
            self.ax.set_xticks(range(len(self.labels)))
            self.ax.set_xticklabels(self.labels)
        except Exception as e:
            raise RuntimeError(f"箱型图绘制失败: {str(e)}")
    
    def apply_specific_style(self) -> None:
        """应用箱型图特有样式
        
        设置箱型图的特定样式和分组样式。
        
        Raises:
            RuntimeError: 样式应用失败时抛出
            
        注意：
            - 会应用箱体样式
            - 会处理分组样式
        """
        if self.ax is None:
            return
            
        try:
            # 应用箱型图样式
            self.style_manager.apply_box_style(self.ax)
            
            # 应用分组样式
            self.style_manager.apply_group_style(self.ax, len(self.data_list))
        except Exception as e:
            raise RuntimeError(f"箱型图样式应用失败: {str(e)}")
