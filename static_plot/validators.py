"""
验证器模块，提供数据和配置的验证功能。包含ConfigValidator用于验证配置参数的
有效性，和DataValidator用于确保输入数据格式的正确性。验证失败时会抛出
ValueError异常并提供详细的错误信息。
"""

from typing import Any, Dict

import numpy as np

from static_plot.config import BasePlotConfig, BoxPlotConfig


class ConfigValidator:
    """配置验证器类
    
    本类提供了对绘图配置的验证功能，包括：
    - 样式配置验证
    - 元素配置验证
    - 箱型图配置验证
    
    所有方法都是静态方法，可以直接调用。
    
    验证失败时会抛出ValueError异常，并给出详细的错误信息。
    
    示例：
        ```python
        # 验证样式配置
        config = BoxPlotConfig()
        try:
            ConfigValidator.validate_style_config(config)
            ConfigValidator.validate_element_config(config)
            ConfigValidator.validate_box_config(config)
        except ValueError as e:
            print(f"配置无效: {str(e)}")
        ```
    """
    
    @staticmethod
    def validate_style_config(config: BasePlotConfig) -> None:
        """验证样式配置的有效性
        
        检查样式配置中的各项参数是否合法，包括：
        - 图形尺寸的正确性
        - DPI值的有效性
        - 字体参数的完整性
        - 线条参数的有效性
        
        Args:
            config: 基础配置对象
            
        Raises:
            ValueError: 当配置参数无效时抛出，错误信息会指明具体问题
        
        示例：
            ```python
            config = BoxPlotConfig()
            try:
                ConfigValidator.validate_style_config(config)
            except ValueError as e:
                print(f"样式配置无效: {str(e)}")
            ```
        """
        # 验证图形尺寸
        if not isinstance(config.style.figsize, tuple) or len(config.style.figsize) != 2:
            raise ValueError("图形尺寸必须是包含两个元素的元组")
        if config.style.figsize[0] <= 0 or config.style.figsize[1] <= 0:
            raise ValueError("图形尺寸必须为正数")
            
        # 验证DPI
        if config.style.dpi <= 0:
            raise ValueError("DPI必须为正数")
            
        # 验证字体参数
        if not isinstance(config.style.font_params, dict):
            raise ValueError("字体参数必须是字典类型")
        if "family" not in config.style.font_params or "size" not in config.style.font_params:
            raise ValueError("字体参数必须包含'family'和'size'")
        if config.style.font_params["size"] <= 0:
            raise ValueError("字体大小必须为正数")
            
        # 验证线条参数
        if config.style.spine_width <= 0:
            raise ValueError("边框线宽必须为正数")
        if config.style.tick_width <= 0:
            raise ValueError("刻度线宽必须为正数")
        if config.style.tick_length <= 0:
            raise ValueError("刻度长度必须为正数")
    
    @staticmethod
    def validate_element_config(config: BasePlotConfig) -> None:
        """验证元素配置的有效性
        
        检查元素配置中的各项参数是否合法，包括：
        - 刻度参数的类型
        - 注释参数的完整性
        
        Args:
            config: 基础配置对象
            
        Raises:
            ValueError: 当配置参数无效时抛出，错误信息会指明具体问题
        
        示例：
            ```python
            config = BoxPlotConfig()
            try:
                ConfigValidator.validate_element_config(config)
            except ValueError as e:
                print(f"元素配置无效: {str(e)}")
            ```
        """
        # 验证刻度参数
        tick_params = config.element.tick_params
        if not isinstance(tick_params, dict):
            raise ValueError("刻度参数必须是字典类型")
            
        # 验证注释参数
        for annotation in config.element.annotations:
            if not isinstance(annotation, dict):
                raise ValueError("注释必须是字典类型")
            if "text" not in annotation:
                raise ValueError("注释必须包含'text'字段")
    
    @staticmethod
    def validate_box_config(config: BoxPlotConfig) -> None:
        """验证箱型图配置的有效性
        
        检查箱型图配置中的各项参数是否合法，包括：
        - 箱体参数的范围
        - 离群点参数的有效性
        - 分组参数的合法性
        
        Args:
            config: 箱型图配置对象
            
        Raises:
            ValueError: 当配置参数无效时抛出，错误信息会指明具体问题
        
        示例：
            ```python
            config = BoxPlotConfig()
            try:
                ConfigValidator.validate_box_config(config)
            except ValueError as e:
                print(f"箱型图配置无效: {str(e)}")
            ```
        """
        # 验证箱体参数
        if config.box_params["width"] <= 0 or config.box_params["width"] > 1:
            raise ValueError("箱体宽度必须在0到1之间")
        if config.box_params["alpha"] <= 0 or config.box_params["alpha"] > 1:
            raise ValueError("箱体透明度必须在0到1之间")
        if config.box_params["linewidth"] <= 0:
            raise ValueError("箱体线宽必须为正数")
            
        # 验证离群点参数
        if config.outlier_params["size"] <= 0:
            raise ValueError("离群点大小必须为正数")
        if config.outlier_params["alpha"] <= 0 or config.outlier_params["alpha"] > 1:
            raise ValueError("离群点透明度必须在0到1之间")
            
        # 验证分组参数
        if config.group_params["size"] <= 0:
            raise ValueError("分组大小必须为正数")
        if config.group_params["divider"]["alpha"] <= 0 or config.group_params["divider"]["alpha"] > 1:
            raise ValueError("分隔线透明度必须在0到1之间")
        if config.group_params["divider"]["width"] <= 0:
            raise ValueError("分隔线宽度必须为正数")


class DataValidator:
    """数据验证器类
    
    本类提供了对绘图数据的验证功能，确保数据格式和内容的正确性。
    
    主要验证内容：
    - 数据结构的完整性
    - 数据类型的正确性
    - 数据值的有效性
    
    所有方法都是静态方法，可以直接调用。
    
    示例：
        ```python
        # 验证箱型图数据
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
        
        try:
            DataValidator.validate_box_data(data)
            print("数据格式正确")
        except ValueError as e:
            print(f"数据无效: {str(e)}")
        ```
    """
    
    @staticmethod
    def validate_box_data(data: Dict[str, Any]) -> None:
        """验证箱型图数据的有效性
        
        检查数据的格式和内容是否满足箱型图的要求，包括：
        - 数据结构的完整性
        - 数据值的有效性
        - 元数据的完整性
        
        Args:
            data: 箱型图数据字典，必须包含：
                - data: 包含values字典的数据部分
                - metadata: 包含x_label和y_label的元数据部分
            
        Raises:
            ValueError: 当数据格式或内容无效时抛出，错误信息会指明具体问题
        
        示例：
            ```python
            data = {
                "data": {"values": {"A": [1, 2, 3]}},
                "metadata": {"x_label": "类别", "y_label": "值"}
            }
            
            try:
                DataValidator.validate_box_data(data)
            except ValueError as e:
                print(f"数据无效: {str(e)}")
            ```
        """
        # 验证数据结构
        if not isinstance(data, dict):
            raise ValueError("数据必须是字典类型")
        if "data" not in data or "metadata" not in data:
            raise ValueError("数据必须包含'data'和'metadata'字段")
            
        # 验证数据内容
        if "values" not in data["data"]:
            raise ValueError("数据必须包含'values'字段")
        if not isinstance(data["data"]["values"], dict):
            raise ValueError("values必须是字典类型")
            
        # 验证数据有效性
        for key, value in data["data"]["values"].items():
            if not isinstance(value, (list, np.ndarray)):
                raise ValueError(f"'{key}'的值必须是列表或numpy数组")
            if len(value) == 0:
                raise ValueError(f"'{key}'的数据不能为空")
            
        # 验证元数据
        metadata = data["metadata"]
        if not isinstance(metadata, dict):
            raise ValueError("元数据必须是字典类型")
        if "x_label" not in metadata or "y_label" not in metadata:
            raise ValueError("元数据必须包含'x_label'和'y_label'字段") 