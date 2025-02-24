"""
箱型图配置类，继承自BasePlotConfig，提供了箱型图特有的配置项。
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

import seaborn as sns

from static_plot.base.base_config import BasePlotConfig


@dataclass
class BoxPlotConfig(BasePlotConfig):
    """箱型图配置类
    
    本类继承自BasePlotConfig，提供了箱型图特有的配置项，包括：
    - 箱体参数：控制箱体的外观
    - 须线参数：控制须线的样式
    - 中位线参数：控制中位线的样式
    - 离群点参数：控制离群点的显示
    - 分组参数：控制多组箱型图的布局
    
    属性说明：
        box_params (Dict[str, Any]): 箱体参数配置，包括：
            - width: 箱体宽度，范围(0,1]
            - alpha: 箱体透明度，范围[0,1]
            - linewidth: 箱体线宽
            - notch: 是否显示凹槽
            - showfliers: 是否显示离群点
        
        whisker_params (Dict[str, Any]): 须线参数配置，包括：
            - linewidth: 线宽
            - style: 线型，如'-', '--'等
        
        median_params (Dict[str, Any]): 中位线参数配置，包括：
            - color: 线条颜色
            - linewidth: 线宽
        
        outlier_params (Dict[str, Any]): 离群点参数配置，包括：
            - marker: 标记样式，如'o', 'D'等
            - size: 标记大小
            - alpha: 透明度
            - color: 颜色，None表示使用箱体颜色
        
        group_params (Dict[str, Any]): 分组参数配置，包括：
            - size: 每组的箱子数量
            - divider: 分组分隔线的样式设置
    
    示例：
        ```python
        # 创建默认箱型图配置
        config = BoxPlotConfig()
        
        # 自定义箱型图样式
        custom_config = BoxPlotConfig(
            box_params={"width": 0.5, "notch": True},
            outlier_params={"marker": "x", "size": 4},
            group_params={"size": 3}
        )
        ```
    """
    box_params: Dict[str, Any] = field(default_factory=lambda: {
        "width": 0.4,  # 箱体宽度，适中值
        "alpha": 1.0,  # 不透明
        "linewidth": 0.8,  # 线宽，与其他元素协调
        "notch": False,  # 不使用凹槽
        "showfliers": True  # 显示离群点
    })
    
    whisker_params: Dict[str, Any] = field(default_factory=lambda: {
        "linewidth": 0.8,  # 线宽，与箱体一致
        "style": "-"  # 实线样式
    })
    
    median_params: Dict[str, Any] = field(default_factory=lambda: {
        "color": "black",  # 黑色中位线
        "linewidth": 0.8  # 线宽，与箱体一致
    })
    
    outlier_params: Dict[str, Any] = field(default_factory=lambda: {
        "marker": "o",  # 圆形标记
        "size": 2,  # 较小的标记尺寸
        "alpha": 0.6,  # 适中的透明度
        "color": None  # 使用箱体颜色
    })
    
    group_params: Dict[str, Any] = field(default_factory=lambda: {
        "size": 4,  # 每组4个箱子
        "divider": {
            "show": True,  # 显示分隔线
            "style": "-",  # 实线样式
            "color": "black",  # 黑色
            "alpha": 0.8,  # 较高的不透明度
            "width": 0.6  # 较细的线宽
        }
    })
    
    def get_style_dict(self) -> Dict[str, Any]:
        """获取箱型图样式字典
        
        将配置参数转换为seaborn.boxplot函数可用的样式字典。
        
        Returns:
            样式参数字典
        
        示例：
            ```python
            config = BoxPlotConfig()
            style_dict = config.get_style_dict()
            sns.boxplot(**style_dict)
            ```
        """
        return {
            "width": self.box_params["width"],
            "boxprops": {
                "alpha": self.box_params["alpha"], 
                "linewidth": self.box_params["linewidth"]
            },
            "whiskerprops": {
                "linewidth": self.whisker_params["linewidth"], 
                "linestyle": self.whisker_params["style"]
            },
            "medianprops": {
                "color": self.median_params["color"], 
                "linewidth": self.median_params["linewidth"]
            },
            "flierprops": {
                "marker": self.outlier_params["marker"],
                "markersize": self.outlier_params["size"],
                "alpha": self.outlier_params["alpha"],
                "markerfacecolor": self.outlier_params["color"],
                "markeredgewidth": self.box_params["linewidth"]
            },
            "notch": self.box_params["notch"],
            "showfliers": self.box_params["showfliers"]
        }
    
    def get_colors(self, num_boxes: int) -> List[str]:
        """获取箱型图颜色列表
        
        为每个箱子分配颜色，同组中的箱子使用相同的颜色序列。
        
        Args:
            num_boxes: 箱子总数
        
        Returns:
            颜色列表
        
        示例：
            ```python
            config = BoxPlotConfig()
            colors = config.get_colors(8)  # 获取8个箱子的颜色
            ```
        
        注意：
            - 颜色数量由group_params["size"]决定
            - 使用seaborn默认调色板
            - 颜色会循环使用以匹配箱子数量
        """
        group_size = self.group_params["size"]
        # 计算需要的基础颜色数量（等于每组的箱子数）
        base_colors = list(sns.color_palette())[:group_size]
        # 重复基础颜色以匹配总箱子数
        colors = []
        num_groups = (num_boxes + group_size - 1) // group_size  # 向上取整
        for i in range(num_groups):
            colors.extend(base_colors)
        return colors[:num_boxes]