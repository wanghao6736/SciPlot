"""
数据格式化工具模块，提供了数据格式转换和标准化的功能。
包含了基础格式化器和特定格式的格式化器实现，支持数据的灵活转换。
"""
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
import yaml

from data_processing.utils.curve_simpler import CurveData, CurveSimplifier
from data_processing.utils.statistics import StatisticsCalculator


class DataFormatter(ABC):
    """数据格式化器基类
    
    定义了数据格式化的标准接口，支持将数据转换为特定格式。
    所有具体的格式化器都应继承自此类并实现其抽象方法。
    
    Attributes:
        _stats_calculator (StatisticsCalculator): 统计计算器
    
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
        """初始化格式化器"""
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

class ParticleSizeFormatter(DataFormatter):
    """粒径分布格式化器
    
    将表格数据转换为粒径分布数据格式，支持两种输入形式：
    1. 粒径和密度数据 -> 计算累积分布
    2. 粒径和累积分布数据 -> 直接使用
    
    同时支持曲线简化和区间分布计算。
    
    Attributes:
        diameter_column (str): 粒径列名
        density_column (Optional[str]): 密度列名，可选
        cumulative_column (Optional[str]): 累积分布列名，可选
        simplify_curve (bool): 是否简化曲线
        target_ncc (float): 目标NCC值
    """
    
    def __init__(
        self,
        diameter_column: str,
        density_column: Optional[str] = None,
        cumulative_column: Optional[str] = None,
        simplify_curve: bool = True,
        target_ncc: float = 0.998
    ):
        """初始化格式化器
        
        Args:
            diameter_column: 粒径列名
            density_column: 密度列名，可选
            cumulative_column: 累积分布列名，可选
            simplify_curve: 是否简化曲线
            target_ncc: 目标NCC值
        """
        super().__init__()
        self.diameter_column = diameter_column
        self.density_column = density_column
        self.cumulative_column = cumulative_column
        self.simplify_curve = simplify_curve
        self._simplifier = CurveSimplifier(target_ncc=target_ncc)
    
    def _calculate_mass_distribution(self, 
                                   diameters: np.ndarray,
                                   density: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        """计算质量分布
        
        Args:
            diameters: 已排序的粒径数组
            density: 密度数组，可选
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: (合并后的直径数组, 累积分布数组)
        """
        # 计算体积(假设球形)
        volumes = (4/3) * np.pi * (diameters/2)**3
        
        # 计算质量
        masses = volumes * density if density is not None else volumes
        
        # 合并相同直径颗粒并计算占比
        unique_diameters, indices = np.unique(diameters, return_inverse=True)
        combined_masses = np.zeros_like(unique_diameters)
        np.add.at(combined_masses, indices, masses)
        
        # 计算体积占比
        total_mass = np.sum(combined_masses)
        if total_mass > 0:
            volume_fraction = combined_masses / total_mass
        else:
            volume_fraction = np.zeros_like(combined_masses)
        
        # 计算累积分布
        cumulative = np.cumsum(volume_fraction) * 100  # 转换为百分比
        return unique_diameters, cumulative
    
    def format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化数据
        
        Args:
            data: 包含数据的字典
            
        Returns:
            Dict[str, Any]: 标准格式的数据字典
        """
        try:
            # 1. 数据验证
            if "data" not in data:
                raise ValueError("Invalid data format: missing 'data' key")
            
            available_columns = list(data["data"].keys())
            required_columns = [self.diameter_column]
            if self.density_column:
                required_columns.append(self.density_column)
            if self.cumulative_column:
                required_columns.append(self.cumulative_column)
            
            missing = [col for col in required_columns if col not in data["data"]]
            if missing:
                raise ValueError(f"Missing columns: {', '.join(missing)}. Available: {', '.join(available_columns)}")
            
            # 2. 数据读取和清理
            diameters = np.array(data["data"][self.diameter_column], dtype=np.float64)
            valid_mask = ~np.isnan(diameters)
            diameters = diameters[valid_mask]
            
            if len(diameters) == 0:
                raise ValueError("No valid data points after cleaning")
            
            # 3. 计算或处理累积分布
            if self.cumulative_column:
                # 处理已知累积分布
                cumulative = np.array(data["data"][self.cumulative_column], dtype=np.float64)[valid_mask]
                valid_mask = ~np.isnan(cumulative)
                diameters = diameters[valid_mask]
                cumulative = cumulative[valid_mask]
                
                # 排序并合并相同直径的累积分布
                sort_idx = np.argsort(diameters)
                diameters = diameters[sort_idx]
                cumulative = cumulative[sort_idx]
                
                # 合并相同直径的值（取平均）
                unique_diameters, unique_idx = np.unique(diameters, return_index=True)
                unique_cumulative = np.array([
                    np.mean(cumulative[diameters == d]) for d in unique_diameters
                ])
                diameters, cumulative = unique_diameters, unique_cumulative
            else:
                # 计算累积分布
                density = None
                if self.density_column:
                    density = np.array(data["data"][self.density_column], dtype=np.float64)[valid_mask]
                    valid_mask = ~np.isnan(density)
                    diameters = diameters[valid_mask]
                    density = density[valid_mask]
                
                # 排序并计算分布
                sort_idx = np.argsort(diameters)
                diameters = diameters[sort_idx]
                if density is not None:
                    density = density[sort_idx]
                
                # 计算累积分布（返回合并后的直径和分布）
                diameters, cumulative = self._calculate_mass_distribution(diameters, density)
            
            # 4. 曲线简化（如果需要）
            if self.simplify_curve and len(diameters) > 100:
                curve_data = CurveData(x=diameters, y=cumulative)
                simplified = self._simplifier.simplify(curve_data)
                diameters = simplified.x
                cumulative = simplified.y
            
            # 5. 计算区间分布
            interval = np.diff(cumulative)
            interval = np.concatenate(([cumulative[0]], interval))
            
            # 6. 计算统计量
            stats_dict = {
                "basic": {
                    "diameter": self._stats_calculator.calculate_basic_stats(diameters),
                    "cumulative": self._stats_calculator.calculate_basic_stats(cumulative),
                    "interval": self._stats_calculator.calculate_basic_stats(interval)
                },
                "distribution": self._stats_calculator.calculate_distribution_stats(diameters),
                "characteristic": self._stats_calculator.calculate_characteristic_diameters(diameters, cumulative)
            }
            
            # 7. 返回标准格式
            return {
                "type": "particle_size",
                "data": {
                    "diameter": diameters.tolist(),
                    "cumulative": cumulative.tolist(),
                    "interval": interval.tolist()
                },
                "metadata": {
                    "x_label": "粒径",
                    "y_label": "累积百分比",
                    "x_unit": "mm",
                    "y_unit": "%",
                    "num_points": len(diameters),
                    "diameter_range": {
                        "min": float(diameters.min()),
                        "max": float(diameters.max())
                    }
                },
                "statistics": stats_dict
            }
            
        except Exception as e:
            raise ValueError(f"Format error: {str(e)}") 