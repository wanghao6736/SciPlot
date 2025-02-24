"""
数据格式化工具模块，提供了数据格式转换和标准化的功能。
包含了基础格式化器和特定格式的格式化器实现，支持数据的灵活转换。
"""
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
import yaml

from data_processing.utils.statistics import StatisticsCalculator


class DataFormatter(ABC):
    """数据格式化器基类
    
    定义了数据格式化的标准接口，支持将数据转换为特定格式。
    所有具体的格式化器都应继承自此类并实现其抽象方法。
    
    Example:
        ```python
        class JSONFormatter(DataFormatter):
            def format(self, data: Dict[str, Any]) -> Dict[str, Any]:
                return {
                    "type": "json",
                    "content": json.dumps(data)
                }
        
        formatter = JSONFormatter()
        result = formatter.format({"key": "value"})
        ```
    """
    
    def __init__(self):
        self._stats_calculator = StatisticsCalculator()
    
    @abstractmethod
    def format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化数据
        
        Args:
            data: 要格式化的数据字典
            
        Returns:
            Dict[str, Any]: 格式化后的数据字典
        """
        pass

class BoxPlotFormatter(DataFormatter):
    """箱型图数据格式化器"""
    
    def __init__(
        self,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        unit: Optional[str] = None
    ):
        super().__init__()
        self.x_label = x_label
        self.y_label = y_label
        self.unit = unit
    
    def format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """将数据转换为箱型图格式
        
        Args:
            data: 包含DataFrame数据的字典
            
        Returns:
            转换后的数据字典
        """
        if "data" not in data:
            raise ValueError("Invalid data format: missing 'data' key")
            
        df = pd.DataFrame(data["data"])
        
        # 移除空列和Unnamed列
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df = df.loc[:, df.any()]  # 移除全为0或NA的列
        
        # 提取有效数据和计算统计量
        values_dict = {}
        stats_dict = {}
        for col in df.columns:
            # 移除0值和NA值
            values = df[col].values
            values = values[values != 0]
            values = values[~np.isnan(values)]
            if len(values) > 0:
                values_dict[col] = values.tolist()
                # 计算统计量
                stats_dict[col] = {
                    "basic": self._stats_calculator.calculate_basic_stats(values),
                    "box": self._stats_calculator.calculate_box_plot_stats(values),
                    "distribution": self._stats_calculator.calculate_distribution_stats(values)
                }
        
        # 构建标准格式
        formatted_data = {
            "type": "box",
            "data": {
                "values": values_dict
            },
            "metadata": {
                "x_label": self.x_label or "Categories",
                "y_label": self.y_label or "Values"
            },
            "statistics": stats_dict
        }
        
        # 添加单位信息（如果有）
        if self.unit:
            formatted_data["metadata"]["unit"] = self.unit
        
        return formatted_data

class ScatterPlotFormatter(DataFormatter):
    """散点图数据格式化器"""
    
    def __init__(
        self,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        x_unit: Optional[str] = None,
        y_unit: Optional[str] = None
    ):
        super().__init__()
        self.x_label = x_label
        self.y_label = y_label
        self.x_unit = x_unit
        self.y_unit = y_unit
    
    def format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """将数据转换为散点图格式
        
        Args:
            data: 包含DataFrame数据的字典
            
        Returns:
            转换后的数据字典
        """
        if "data" not in data:
            raise ValueError("Invalid data format: missing 'data' key")
            
        df = pd.DataFrame(data["data"])
        
        # 确保至少有两列数据
        if len(df.columns) < 2:
            raise ValueError("Scatter plot requires at least two columns of data")
        
        # 默认使用前两列作为x和y
        x_col = df.columns[0]
        y_col = df.columns[1]
        
        # 提取数据
        x_values = df[x_col].values
        y_values = df[y_col].values
        
        # 移除无效数据点
        valid_mask = ~(np.isnan(x_values) | np.isnan(y_values))
        x_values = x_values[valid_mask]
        y_values = y_values[valid_mask]
        
        # 计算统计量
        stats_dict = {
            "basic": {
                "x": self._stats_calculator.calculate_basic_stats(x_values),
                "y": self._stats_calculator.calculate_basic_stats(y_values)
            },
            "correlation": self._stats_calculator.calculate_correlation_stats(x_values, y_values)
        }
        
        # 构建标准格式
        formatted_data = {
            "type": "scatter",
            "data": {
                "x": x_values.tolist(),
                "y": y_values.tolist()
            },
            "metadata": {
                "x_label": self.x_label or x_col,
                "y_label": self.y_label or y_col
            },
            "statistics": stats_dict
        }
        
        # 添加单位信息
        if self.x_unit:
            formatted_data["metadata"]["x_unit"] = self.x_unit
        if self.y_unit:
            formatted_data["metadata"]["y_unit"] = self.y_unit
        
        return formatted_data

class JSONFormatter(DataFormatter):
    """JSON格式化器
    
    将数据转换为JSON格式，支持自定义的序列化选项。
    
    Attributes:
        indent (Optional[int]): JSON缩进空格数，默认为None
        ensure_ascii (bool): 是否确保ASCII编码，默认为False
        
    Example:
        ```python
        formatter = JSONFormatter(indent=2)
        result = formatter.format({
            "name": "张三",
            "age": 25
        })
        ```
    """
    
    def __init__(self, indent: Optional[int] = None, ensure_ascii: bool = False):
        """初始化JSON格式化器
        
        Args:
            indent: JSON缩进空格数，默认为None
            ensure_ascii: 是否确保ASCII编码，默认为False
        """
        self.indent = indent
        self.ensure_ascii = ensure_ascii
    
    def format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化为JSON
        
        Args:
            data: 要格式化的数据字典
            
        Returns:
            Dict[str, Any]: 包含JSON字符串的字典
        """
        return {
            "type": "json",
            "content": json.dumps(
                data,
                indent=self.indent,
                ensure_ascii=self.ensure_ascii
            )
        }

class YAMLFormatter(DataFormatter):
    """YAML格式化器
    
    将数据转换为YAML格式，支持自定义的序列化选项。
    
    Attributes:
        default_flow_style (Optional[bool]): YAML流样式，默认为None
        encoding (str): 编码格式，默认为utf-8
        
    Example:
        ```python
        formatter = YAMLFormatter(default_flow_style=False)
        result = formatter.format({
            "config": {
                "name": "测试配置",
                "version": 1.0
            }
        })
        ```
    """
    
    def __init__(self, default_flow_style: Optional[bool] = None, encoding: str = 'utf-8'):
        """初始化YAML格式化器
        
        Args:
            default_flow_style: YAML流样式，默认为None
            encoding: 编码格式，默认为utf-8
        """
        self.default_flow_style = default_flow_style
        self.encoding = encoding
    
    def format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化为YAML
        
        Args:
            data: 要格式化的数据字典
            
        Returns:
            Dict[str, Any]: 包含YAML字符串的字典
        """
        return {
            "type": "yaml",
            "content": yaml.dump(
                data,
                default_flow_style=self.default_flow_style,
                encoding=self.encoding
            )
        }

class CompositeFormatter(DataFormatter):
    """组合格式化器
    
    支持多个格式化器的组合使用，可以同时输出多种格式。
    
    Attributes:
        formatters (Dict[str, DataFormatter]): 格式化器字典
        
    Example:
        ```python
        composite = CompositeFormatter({
            "json": JSONFormatter(indent=2),
            "yaml": YAMLFormatter()
        })
        result = composite.format({"key": "value"})
        ```
    """
    
    def __init__(self, formatters: Dict[str, DataFormatter]):
        """初始化组合格式化器
        
        Args:
            formatters: 格式化器字典，键为格式名称
        """
        self.formatters = formatters
    
    def format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """使用所有格式化器格式化数据
        
        Args:
            data: 要格式化的数据字典
            
        Returns:
            Dict[str, Any]: 包含所有格式的结果字典
        """
        return {
            name: formatter.format(data)
            for name, formatter in self.formatters.items()
        } 