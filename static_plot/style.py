"""
样式管理模块，实现了图表样式的统一管理和应用。提供了基础样式管理器BaseStyleManager
和箱型图样式管理器BoxStyleManager，支持样式的继承和扩展。样式系统采用分层设计，
包括基础样式、特定样式和自定义样式三个层次。
"""

from typing import Any, List

import matplotlib.pyplot as plt

from static_plot.config import BasePlotConfig, BoxPlotConfig


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


class BoxStyleManager(BaseStyleManager):
    """箱型图样式管理器类
    
    本类继承自BaseStyleManager，提供了箱型图特有的样式管理功能。
    
    主要功能：
    - 箱体样式设置
    - 须线样式设置
    - 离群点样式设置
    - 分组样式设置
    
    工作流程：
    1. 应用基础样式
    2. 设置箱体样式
    3. 配置分组样式
    
    属性说明：
        config (BoxPlotConfig): 箱型图配置对象，包含特有样式参数
    
    示例：
        ```python
        # 创建箱型图样式管理器
        config = BoxPlotConfig()
        style_manager = BoxStyleManager(config)
        
        # 应用样式
        fig, ax = plt.subplots()
        style_manager.apply_style(ax)  # 应用基础样式
        style_manager.apply_box_style(ax)  # 应用箱型图样式
        ```
    """
    
    def __init__(self, config: BoxPlotConfig):
        """初始化箱型图样式管理器
        
        Args:
            config: 箱型图配置对象
            
        示例：
            ```python
            config = BoxPlotConfig()
            style_manager = BoxStyleManager(config)
            ```
        """
        super().__init__(config)
        self.config: BoxPlotConfig = config
    
    def apply_box_style(self, ax: plt.Axes) -> None:
        """应用箱型图样式
        
        为箱型图的各个组件设置样式。
        
        Args:
            ax: matplotlib坐标轴对象
            
        注意：
            - 需要在绘制箱型图后调用
            - 会影响所有箱体的样式
        
        示例：
            ```python
            sns.boxplot(data=data, ax=ax)
            style_manager.apply_box_style(ax)
            ```
        """
        if ax is None:
            return
            
        # 获取箱子对象
        box_patches = [patch for patch in ax.patches 
                      if hasattr(patch, 'get_facecolor')]
        if len(box_patches) == 0:  # 对于老版本matplotlib，boxes存储在artists中
            box_patches = ax.artists
        
        # 应用样式
        self._apply_box_colors(ax, box_patches)
    
    def _apply_box_colors(self, ax: plt.Axes, patches: List[Any]) -> None:
        """应用箱子颜色
        
        为每个箱子及其关联的元素设置颜色。
        
        Args:
            ax: matplotlib坐标轴对象
            patches: 箱子对象列表
            
        注意：
            - 颜色会应用到箱体、须线和离群点
            - 保持颜色的一致性
        """
        num_patches = len(patches)
        lines_per_boxplot = len(ax.lines) // num_patches
        
        for i, patch in enumerate(patches):
            self._style_single_box(ax, patch, i, lines_per_boxplot)
    
    def _style_single_box(
        self, 
        ax: plt.Axes, 
        patch: Any, 
        index: int, 
        lines_per_box: int
    ) -> None:
        """设置单个箱子的样式
        
        配置单个箱子及其关联元素的样式。
        
        Args:
            ax: matplotlib坐标轴对象
            patch: 箱子对象
            index: 箱子索引
            lines_per_box: 每个箱子的线条数
            
        注意：
            - 箱体设置为空心
            - 所有关联元素使用相同的颜色
        """
        # 获取并设置箱子颜色
        col = patch.get_facecolor()
        patch.set_edgecolor(col)
        patch.set_facecolor('None')  # 设置箱子为空心
        
        # 设置关联的所有线条颜色
        start_idx = index * lines_per_box
        end_idx = (index + 1) * lines_per_box
        
        for line in ax.lines[start_idx:end_idx]:
            line.set_color(col)
            line.set_mfc(col)  # 异常点填充色
            line.set_mec(col)  # 异常点边框色
    
    def apply_group_style(self, ax: plt.Axes, num_boxes: int) -> None:
        """应用分组样式
        
        为多组箱型图添加分隔线。
        
        Args:
            ax: matplotlib坐标轴对象
            num_boxes: 箱子总数
            
        注意：
            - 只在启用分组显示时添加分隔线
            - 分隔线位于组之间
        
        示例：
            ```python
            style_manager.apply_group_style(ax, 8)  # 8个箱子
            ```
        """
        if not self.config.group_params["divider"]["show"]:
            return
            
        group_size = self.config.group_params["size"]
        divider = self.config.group_params["divider"]
        
        # 添加分组分隔线
        for i in range(group_size, num_boxes, group_size):
            if i < num_boxes:
                ax.axvline(
                    i - 0.5,
                    linestyle=divider["style"],
                    color=divider["color"],
                    alpha=divider["alpha"],
                    linewidth=divider["width"],
                    zorder=1
                ) 