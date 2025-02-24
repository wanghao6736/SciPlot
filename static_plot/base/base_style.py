"""
样式管理模块，实现了图表样式的统一管理和应用。提供了基础样式管理器BaseStyleManager，
支持样式的继承和扩展。样式系统采用分层设计，包括基础样式、特定样式和自定义样式三个层次。
"""

import matplotlib.pyplot as plt

from static_plot.base.base_config import BasePlotConfig


class BaseStyleManager:
    """基础样式管理器类
    
    本类提供了基础的样式管理功能，负责处理通用的图形样式设置。
    
    主要功能：
    - 边框样式设置
    - 刻度样式设置
    - 网格样式设置
    - 字体样式设置
    
    工作流程：
    1. 初始化：接收配置对象
    2. 验证：检查样式参数
    3. 应用：设置具体样式
    
    属性说明：
        config (BasePlotConfig): 基础配置对象，包含样式参数
    
    示例：
        ```python
        # 创建样式管理器
        config = BasePlotConfig()
        style_manager = BaseStyleManager(config)
        
        # 应用样式
        fig, ax = plt.subplots()
        style_manager.apply_style(ax)
        ```
    """
    
    def __init__(self, config: BasePlotConfig):
        """初始化样式管理器
        
        Args:
            config: 基础配置对象，包含样式参数
            
        示例：
            ```python
            config = BasePlotConfig()
            style_manager = BaseStyleManager(config)
            ```
        """
        self.config = config
    
    def apply_style(self, ax: plt.Axes) -> None:
        """应用基础样式
        
        为指定的坐标轴对象应用基础样式设置。
        
        Args:
            ax: matplotlib坐标轴对象
            
        注意：
            - 样式应用顺序：边框 -> 刻度 -> 网格
            - 确保坐标轴对象可用
        
        示例：
            ```python
            fig, ax = plt.subplots()
            style_manager.apply_style(ax)
            ```
        """
        if ax is None:
            return
            
        self.apply_spines(ax)
        self.apply_ticks(ax)
        self.apply_grid(ax)
    
    def apply_spines(self, ax: plt.Axes) -> None:
        """设置边框样式
        
        配置坐标轴边框的样式，包括线宽和颜色。
        
        Args:
            ax: matplotlib坐标轴对象
            
        注意：
            应用于所有可见的边框
        """
        for spine in ax.spines.values():
            spine.set_linewidth(self.config.style.spine_width)
            spine.set_color(self.config.style.spine_color)
    
    def apply_ticks(self, ax: plt.Axes) -> None:
        """设置刻度样式
        
        配置坐标轴刻度的样式，包括主刻度和次刻度。
        
        Args:
            ax: matplotlib坐标轴对象
            
        注意：
            - 主刻度和次刻度使用不同的参数
            - 可以通过配置控制次刻度的显示
        """
        # 设置主刻度
        ax.tick_params(
            which="major",
            direction=self.config.style.tick_direction,
            width=self.config.style.tick_width,
            length=self.config.style.tick_length,
            color=self.config.style.tick_color,
            top=False,
            right=False
        )
        
        # 设置次刻度
        if self.config.style.minor_ticks:
            ax.minorticks_on()
            ax.tick_params(
                which="minor",
                direction=self.config.style.tick_direction,
                width=self.config.style.minor_tick_width,
                length=self.config.style.minor_tick_length,
                color=self.config.style.tick_color,
                top=False,
                right=False
            )
    
    def apply_grid(self, ax: plt.Axes) -> None:
        """设置网格样式
        
        配置坐标网格的显示和样式。
        
        Args:
            ax: matplotlib坐标轴对象
            
        注意：
            网格可以通过配置完全禁用
        """
        if self.config.style.grid:
            ax.grid(True, which="major", **self.config.style.grid_params)
        else:
            ax.grid(False)
