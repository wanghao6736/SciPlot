"""
配置管理模块，定义了绘图系统的配置类结构。包含StyleConfig（样式配置）、
ElementConfig（元素配置）、BasePlotConfig（基础绘图配置）和BoxPlotConfig
（箱型图配置）等类。提供了配置的验证、继承和模板机制。
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import seaborn as sns


@dataclass
class StyleConfig:
    """样式配置类
    
    本类定义了图形的基本视觉样式，包括：
    - 基础设置：图形大小、分辨率等
    - 字体设置：字体族、大小等
    - 边框设置：线条宽度、颜色等
    - 刻度设置：方向、大小等
    - 网格设置：样式、透明度等
    
    属性说明：
        style (str): 图形样式主题，可选值：'ticks', 'white', 'whitegrid'等
        context (str): 图形上下文，可选值：'paper', 'talk', 'poster'等
        figsize (Tuple[float, float]): 图形尺寸（宽, 高），单位为英寸
        dpi (int): 图形分辨率，每英寸点数
        font_params (Dict[str, Any]): 字体参数配置
        spine_width (float): 边框线宽
        spine_color (str): 边框颜色
        tick_direction (str): 刻度方向，'in'或'out'
        tick_width (float): 刻度线宽
        tick_length (float): 刻度长度
        tick_color (str): 刻度颜色
        minor_ticks (bool): 是否显示次刻度
        minor_tick_width (float): 次刻度线宽
        minor_tick_length (float): 次刻度长度
        grid (bool): 是否显示网格
        grid_params (Dict[str, Any]): 网格参数配置
        rc_params (Dict[str, Any]): 自定义matplotlib参数
    
    示例：
        ```python
        # 创建默认样式配置
        style_config = StyleConfig()
        
        # 自定义样式
        custom_style = StyleConfig(
            style="ticks",
            figsize=(4.8, 3.6),
            font_params={"family": "Times New Roman", "size": 8}
        )
        ```
    """
    # 基础设置
    style: str = "ticks"  # 使用ticks样式，适合科研论文
    context: str = "paper"  # paper上下文，为论文输出优化
    figsize: Tuple[float, float] = (3.6, 2.7)  # 适合单栏论文的图形尺寸
    dpi: int = 300  # 期刊常用分辨率
    
    # 字体设置
    font_params: Dict[str, Any] = field(default_factory=lambda: {
        "family": "sans-serif",  # 使用无衬线字体族
        "size": 6  # 6pt字号，适合图形尺寸
    })
    
    # 边框设置
    spine_width: float = 0.8  # 边框线宽，与其他元素协调
    spine_color: str = "black"  # 边框颜色，标准黑色
    
    # 刻度设置
    tick_direction: str = "in"  # 刻度向内，专业期刊常用样式
    tick_width: float = 0.5  # 刻度线宽，略细于边框
    tick_length: float = 2.0  # 刻度长度，确保可见性
    tick_color: str = "black"  # 刻度颜色，与边框一致
    minor_ticks: bool = False  # 不显示次刻度，减少视觉干扰
    minor_tick_width: float = 0.4  # 次刻度线宽，细于主刻度
    minor_tick_length: float = 1.5  # 次刻度长度，短于主刻度
    
    # 网格设置
    grid: bool = False  # 不显示网格，保持简洁
    grid_params: Dict[str, Any] = field(default_factory=lambda: {
        "linestyle": "--",  # 虚线网格
        "linewidth": 0.5,  # 细网格线
        "alpha": 0.3,  # 较低透明度
        "color": "black"  # 黑色网格
    })
    
    # matplotlib 自定义RC参数
    rc_params: Dict[str, Any] = field(default_factory=lambda: {
        "font.sans-serif": ["Songti SC", "STHeiti", "LiHei Pro", "Arial"],  # 中文优先
        "font.serif": ["Songti SC", "STSong", "SimSun", "Times New Roman"],  # 衬线字体
        "axes.unicode_minus": False  # 使用 Unicode 负号
    })

@dataclass
class ElementConfig:
    """元素配置类
    
    本类定义了图形中的文本和标注元素，包括：
    - 标题：图形主标题
    - 轴标签：X轴和Y轴的标签
    - 刻度参数：刻度位置和标签
    - 注释：额外的文本标注
    
    属性说明：
        title (Optional[str]): 图形标题，None表示不显示标题
        xlabel (Optional[str]): X轴标签，None表示不显示
        ylabel (Optional[str]): Y轴标签，None表示不显示
        tick_params (Dict[str, Any]): 刻度参数配置，包括：
            - xticks: X轴刻度位置
            - yticks: Y轴刻度位置
            - xticklabels: X轴刻度标签
            - yticklabels: Y轴刻度标签
            - xlim: X轴显示范围
            - ylim: Y轴显示范围
        annotations (List[Dict[str, Any]]): 注释列表，每个注释是一个字典
    
    示例：
        ```python
        # 创建默认元素配置
        element_config = ElementConfig()
        
        # 自定义元素配置
        custom_element = ElementConfig(
            title="数据分布图",
            xlabel="类别",
            ylabel="数值",
            tick_params={"xlim": (0, 10)},
            annotations=[{
                "text": "峰值",
                "xy": (5, 10),
                "xytext": (6, 12),
                "arrowprops": {"arrowstyle": "->"}
            }]
        )
        ```
    """
    title: Optional[str] = None  # 图形标题，默认不显示
    xlabel: Optional[str] = None  # X轴标签，默认不显示
    ylabel: Optional[str] = None  # Y轴标签，默认不显示
    tick_params: Dict[str, Any] = field(default_factory=lambda: {
        "xticks": None,  # X轴刻度位置，None表示自动计算
        "yticks": None,  # Y轴刻度位置，None表示自动计算
        "xticklabels": None,  # X轴刻度标签，None表示使用刻度值
        "yticklabels": None,  # Y轴刻度标签，None表示使用刻度值
        "xlim": None,  # X轴范围，None表示自动计算
        "ylim": None  # Y轴范围，None表示自动计算
    })
    annotations: List[Dict[str, Any]] = field(default_factory=list)  # 注释列表，默认为空

@dataclass
class BasePlotConfig:
    """基础绘图配置类
    
    本类提供了绘图的基础配置框架，包括：
    - 样式配置：控制图形的视觉外观
    - 元素配置：管理图形中的文本和标注
    - 输出配置：控制图形的保存参数
    
    同时提供了配置更新和模板创建的功能。
    
    属性说明：
        style (StyleConfig): 样式配置对象
        element (ElementConfig): 元素配置对象
        output_params (Dict[str, Any]): 输出参数配置，包括：
            - format: 输出格式，如'pdf', 'png'等
            - dpi: 输出分辨率
            - path: 输出路径
    
    示例：
        ```python
        # 创建默认配置
        config = BasePlotConfig()
        
        # 使用模板创建配置
        paper_config = BasePlotConfig.create_template("paper")
        
        # 更新配置
        config.update({
            "style.font_params.size": 8,
            "output_params.format": "png"
        })
        ```
    """
    style: StyleConfig = field(default_factory=StyleConfig)  # 样式配置
    element: ElementConfig = field(default_factory=ElementConfig)  # 元素配置
    output_params: Dict[str, Any] = field(default_factory=lambda: {
        "format": "pdf",  # 输出格式，默认PDF
        "dpi": 300,  # 输出分辨率，适合印刷
        "transparent": True,  # 透明背景
        "bbox_inches": "tight",  # 裁剪空白区域
        "path": None  # 输出路径，None表示需要手动指定
    })
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """更新配置参数
        
        使用点号分隔的键路径更新嵌套配置。
        
        Args:
            config_dict: 配置字典，键使用点号分隔表示路径
                例如：{"style.font_params.size": 8}
        
        示例：
            ```python
            config.update({
                "style.font_params.size": 8,
                "element.title": "新标题",
                "output_params.format": "png"
            })
            ```
        """
        for key, value in config_dict.items():
            parts = key.split('.')
            obj = self
            for part in parts[:-1]:
                obj = getattr(obj, part)
            setattr(obj, parts[-1], value)
    
    @classmethod
    def create_template(cls, template_name: str) -> 'BasePlotConfig':
        """创建预设模板配置
        
        提供了常用场景的预设配置模板。
        
        Args:
            template_name: 模板名称，可选值：
                - "paper": 适用于学术论文的配置
                - "presentation": 适用于演示的配置
        
        Returns:
            配置实例
        
        示例：
            ```python
            # 创建论文模板配置
            paper_config = BasePlotConfig.create_template("paper")
            
            # 创建演示模板配置
            pres_config = BasePlotConfig.create_template("presentation")
            ```
        """
        templates = {
            "paper": {  # 论文模板
                "style": {
                    "figsize": (3.6, 2.7),  # 单栏宽度
                    "style": "white",  # 简洁白色背景
                    "context": "paper",  # 论文场景
                    "font_params": {"size": 8}  # 论文字号
                }
            },
            "presentation": {  # 演示模板
                "style": {
                    "figsize": (6.4, 4.8),  # 演示尺寸
                    "style": "whitegrid",  # 网格背景
                    "context": "talk",  # 演讲场景
                    "font_params": {"size": 12}  # 演示字号
                }
            }
        }
        
        config = cls()
        if template_name in templates:
            config.update(templates[template_name])
        return config

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