"""
基础绘图模块，提供标准化的绘图流程框架。定义了绘图器的基类和资源管理机制，
实现了统一的异常处理和上下文管理。所有具体的绘图器都应继承自此模块的BasePlotter类。

主要功能包括标准化的绘图流程管理、统一的样式应用机制、资源的安全管理和异常的统一处理。
使用上下文管理器确保资源的正确释放，推荐使用with语句进行安全的资源管理。
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Union

import matplotlib.pyplot as plt
import seaborn as sns

from static_plot.config import BasePlotConfig
from static_plot.style import BaseStyleManager
from static_plot.validators import ConfigValidator


class BasePlotter(ABC):
    """基础绘图类
    
    本类提供了绘图的标准框架，定义了完整的绘图流程和资源管理机制。
    
    主要特性：
    - 标准化的绘图流程
    - 统一的样式管理
    - 安全的资源处理
    - 完整的异常处理
    
    工作流程：
    1. 初始化：创建配置和样式管理器
    2. 验证：检查配置和数据的有效性
    3. 绘图：按照标准流程创建和绘制图形
    4. 清理：确保资源被正确释放
    
    属性说明：
        config (BasePlotConfig): 基础配置对象
        fig (Optional[plt.Figure]): matplotlib图形对象
        ax (Optional[plt.Axes]): matplotlib坐标轴对象
        style_manager (BaseStyleManager): 样式管理器对象
    
    示例：
        ```python
        class MyPlotter(BasePlotter):
            def prepare_data(self, data):
                # 实现数据准备逻辑
                pass
                
            def draw_plot(self):
                # 实现具体绘图逻辑
                pass
        
        # 使用绘图器
        with MyPlotter() as plotter:
            plotter.plot(data)
            plotter.save("output.pdf")
        ```
    """
    
    def __init__(self, config: Optional[BasePlotConfig] = None):
        """初始化绘图器
        
        创建绘图器实例并进行必要的初始化工作。
        
        Args:
            config: 基础配置对象，如果为None则使用默认配置
            
        Raises:
            ValueError: 当配置无效时抛出
        
        示例：
            ```python
            # 使用默认配置
            plotter = BasePlotter()
            
            # 使用自定义配置
            config = BasePlotConfig()
            plotter = BasePlotter(config)
            ```
        """
        self.config = config or BasePlotConfig()
        self.fig: Optional[plt.Figure] = None
        self.ax: Optional[plt.Axes] = None
        self.style_manager = BaseStyleManager(self.config)
        
        # 验证配置
        self.validate_config()
        
        # 设置基础环境
        self._setup_environment()
    
    def validate_config(self) -> None:
        """验证配置有效性
        
        检查配置参数是否满足要求。
        
        Raises:
            ValueError: 当配置参数无效时抛出
        
        注意：
            子类可以重写此方法以添加特定的验证逻辑
        """
        ConfigValidator.validate_style_config(self.config)
        ConfigValidator.validate_element_config(self.config)
    
    def validate_data(self, data: Dict[str, Any]) -> None:
        """验证数据有效性
        
        检查输入数据是否满足要求。
        
        Args:
            data: 输入数据字典
            
        Raises:
            ValueError: 当数据无效时抛出
            
        注意：
            子类必须实现具体的验证逻辑
        """
        pass  # 由子类实现具体验证逻辑
    
    def _setup_environment(self) -> None:
        """设置基础绘图环境
        
        配置matplotlib和seaborn的基本参数。
        
        Raises:
            RuntimeError: 环境设置失败时抛出
        """
        try:
            sns.set_theme(
                context=self.config.style.context,
                font=self.config.style.font_params["family"],
                font_scale=self.config.style.font_params["size"] / 8.0,
                rc=self.config.style.rc_params # 更新自定义参数
            )
        except Exception as e:
            raise RuntimeError(f"环境设置失败: {str(e)}")
    
    def plot(self, data: Dict[str, Any]) -> None:
        """标准化绘图流程
        
        按照预定义的流程完成绘图任务。
        
        Args:
            data: 绘图数据字典
            
        Raises:
            ValueError: 数据无效时抛出
            RuntimeError: 绘图过程出错时抛出
        
        工作流程：
        1. 验证数据
        2. 创建图形
        3. 准备数据
        4. 绘制图形
        5. 应用样式
        6. 添加元素
        7. 调整布局
        
        示例：
            ```python
            data = {
                "data": {"values": {"A": [1, 2, 3]}},
                "metadata": {"x_label": "类别", "y_label": "值"}
            }
            plotter.plot(data)
            ```
        """
        try:
            # 验证数据
            self.validate_data(data)
            
            # 1. 创建图形
            self.create_figure()
            
            # 2. 准备数据
            self.prepare_data(data)
            
            # 3. 绘制图形
            self.draw_plot()
            
            # 4. 应用样式
            self.apply_style()
            
            # 5. 添加元素
            self.add_elements()
            
            # 6. 调整布局
            self.adjust_layout()
            
        except Exception as e:
            self.cleanup()
            raise RuntimeError(f"绘图失败: {str(e)}")
    
    def create_figure(self) -> None:
        """创建图形并初始化
        
        创建matplotlib图形和坐标轴对象。
        
        Raises:
            RuntimeError: 创建图形失败时抛出
        """
        try:
            with sns.axes_style(self.config.style.style, rc=self.config.style.rc_params):
                self.fig, self.ax = plt.subplots(
                    figsize=self.config.style.figsize,
                    dpi=self.config.style.dpi
                )
        except Exception as e:
            raise RuntimeError(f"创建图形失败: {str(e)}")
    
    @abstractmethod
    def prepare_data(self, data: Dict[str, Any]) -> None:
        """准备绘图数据
        
        处理输入数据，使其满足绘图要求。
        
        Args:
            data: 原始数据字典
            
        注意：
            子类必须实现此方法以处理特定类型的数据
        """
        pass
    
    @abstractmethod
    def draw_plot(self) -> None:
        """实现具体绘图逻辑
        
        注意：
            子类必须实现此方法以实现具体的绘图功能
        """
        pass
    
    def apply_style(self) -> None:
        """应用样式设置
        
        应用基础样式和特定样式设置。
        
        Raises:
            RuntimeError: 样式应用失败时抛出
        """
        if self.ax is None:
            return
            
        try:
            # 1. 应用基础样式
            self.style_manager.apply_style(self.ax)
            
            # 2. 应用特定样式
            self.apply_specific_style()
        except Exception as e:
            raise RuntimeError(f"样式应用失败: {str(e)}")
    
    def apply_specific_style(self) -> None:
        """应用特定样式设置
        
        注意：
            子类可以重写此方法以应用特定的样式设置
        """
        pass
    
    def add_elements(self) -> None:
        """添加图表元素
        
        添加标题、标签、刻度和注释等元素。
        
        Raises:
            ValueError: 坐标轴不可用时抛出
            RuntimeError: 添加元素失败时抛出
        """
        if self.ax is None:
            raise ValueError("坐标轴对象不可用")
            
        try:
            self._add_text_elements()
            self._set_ticks_and_limits()
            self._add_annotations()
        except Exception as e:
            raise RuntimeError(f"添加元素失败: {str(e)}")
    
    def _add_text_elements(self) -> None:
        """添加文本元素
        
        添加标题和轴标签。
        """
        if self.config.element.title:
            self.ax.set_title(self.config.element.title)
        if self.config.element.xlabel:
            self.ax.set_xlabel(self.config.element.xlabel)
        if self.config.element.ylabel:
            self.ax.set_ylabel(self.config.element.ylabel)
    
    def _set_ticks_and_limits(self) -> None:
        """设置刻度和范围
        
        设置坐标轴的刻度位置、标签和显示范围。
        """
        tick_params = self.config.element.tick_params
        
        if tick_params["xticks"] is not None:
            self.ax.set_xticks(tick_params["xticks"])
            if tick_params["xticklabels"] is not None:
                self.ax.set_xticklabels(tick_params["xticklabels"])
        
        if tick_params["yticks"] is not None:
            self.ax.set_yticks(tick_params["yticks"])
            if tick_params["yticklabels"] is not None:
                self.ax.set_yticklabels(tick_params["yticklabels"])
        
        if tick_params["xlim"] is not None:
            self.ax.set_xlim(tick_params["xlim"])
        if tick_params["ylim"] is not None:
            self.ax.set_ylim(tick_params["ylim"])
    
    def _add_annotations(self) -> None:
        """添加注释
        
        添加自定义注释。
        """
        for annotation in self.config.element.annotations:
            self.ax.annotate(**annotation)
    
    def adjust_layout(self) -> None:
        """调整图表布局
        
        优化图表的整体布局。
        
        Raises:
            RuntimeError: 布局调整失败时抛出
        """
        if self.fig is not None:
            try:
                self.fig.tight_layout()
            except Exception as e:
                raise RuntimeError(f"布局调整失败: {str(e)}")
    
    def save(self, path: Optional[Union[str, Path]] = None) -> None:
        """保存图像
        
        将图形保存到指定路径。
        
        Args:
            path: 保存路径，如果为None则使用配置中的路径
            
        Raises:
            ValueError: 图形不可用或路径无效时抛出
            RuntimeError: 保存失败时抛出
        
        示例：
            ```python
            # 使用指定路径保存
            plotter.save("output.pdf")
            
            # 使用配置中的路径保存
            plotter.save()
            ```
        """
        if self.fig is None:
            raise ValueError("没有可保存的图形")
        
        try:
            save_path = Path(path) if path else self.config.output_params["path"]
            if save_path is None:
                raise ValueError("未指定输出路径")
            
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.fig.savefig(
                save_path,
                format=self.config.output_params["format"],
                dpi=self.config.output_params["dpi"],
                bbox_inches="tight"
            )
        except Exception as e:
            raise RuntimeError(f"保存图形失败: {str(e)}")
    
    def show(self) -> None:
        """显示图像
        
        在屏幕上显示当前图形。
        
        Raises:
            ValueError: 图形不可用时抛出
        """
        if self.fig is None:
            raise ValueError("没有可显示的图形")
        plt.show()
    
    def close(self) -> None:
        """关闭图形
        
        关闭当前图形并释放资源。
        """
        if self.fig is not None:
            plt.close(self.fig)
            self.fig = None
            self.ax = None
    
    def cleanup(self) -> None:
        """清理所有资源
        
        关闭所有打开的图形并释放资源。
        """
        self.close()
        plt.close('all')
    
    def __enter__(self):
        """上下文管理器入口
        
        Returns:
            绘图器实例
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口
        
        确保资源被正确清理。
        """
        self.cleanup()