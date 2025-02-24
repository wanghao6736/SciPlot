"""
统计分析工具模块，提供了数据统计和分析的功能。
包含了基础统计计算、描述性统计和数据分析等功能的实现。
"""
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from scipy import stats


class StatisticsCalculator:
    """统计计算器类
    
    提供了一系列统计计算方法，支持基础统计量计算、
    描述性统计分析和数据分布分析等功能。
    
    Example:
        ```python
        # 计算基础统计量
        stats = StatisticsCalculator.calculate_basic_stats(values)
        
        # 检测异常值
        outliers = StatisticsCalculator.detect_outliers(values)
        ```
    """
    
    @staticmethod
    def calculate_basic_stats(values: np.ndarray) -> Dict[str, Any]:
        """计算基础统计量
        
        Args:
            values: 数值数组
            
        Returns:
            Dict[str, Any]: 包含基础统计量的字典
            
        Example:
            ```python
            stats = StatisticsCalculator.calculate_basic_stats(values)
            # 返回格式示例:
            # {
            #     'mean': 1.5,
            #     'std': 0.5,
            #     'min': 1.0,
            #     'max': 2.0,
            #     'median': 1.5,
            #     'count': 10
            # }
            ```
        """
        return {
            'mean': float(np.mean(values)),
            'std': float(np.std(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'median': float(np.median(values)),
            'count': int(len(values))
        }
    
    @staticmethod
    def calculate_correlation(x: np.ndarray,
                            y: np.ndarray,
                            method: str = 'pearson') -> float:
        """计算相关性系数
        
        Args:
            x: 第一个数值数组
            y: 第二个数值数组
            method: 相关系数计算方法，可选 'pearson'、'spearman'、'kendall'
            
        Returns:
            float: 相关系数
            
        Example:
            ```python
            corr = StatisticsCalculator.calculate_correlation(x, y, method='spearman')
            ```
        """
        if method == 'pearson':
            return float(stats.pearsonr(x, y)[0])
        elif method == 'spearman':
            return float(stats.spearmanr(x, y)[0])
        elif method == 'kendall':
            return float(stats.kendalltau(x, y)[0])
        else:
            raise ValueError(f"不支持的相关系数计算方法: {method}")
    
    @staticmethod
    def calculate_distribution(values: np.ndarray,
                             bins: Optional[Union[int, List[float]]] = None) -> Tuple[np.ndarray, np.ndarray]:
        """计算数据分布
        
        Args:
            values: 数值数组
            bins: 直方图的分箱数或分箱边界列表
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: (频数数组, 分箱边界数组)
            
        Example:
            ```python
            counts, bins = StatisticsCalculator.calculate_distribution(values, bins=10)
            ```
        """
        return np.histogram(values, bins=bins)
    
    @staticmethod
    def calculate_summary(values: np.ndarray,
                         percentiles: Optional[List[float]] = None) -> Dict[str, float]:
        """计算数据摘要
        
        Args:
            values: 数值数组
            percentiles: 要计算的分位数列表，默认为[0.25, 0.5, 0.75]
            
        Returns:
            Dict[str, float]: 统计摘要字典
            
        Example:
            ```python
            summary = StatisticsCalculator.calculate_summary(
                values,
                percentiles=[0.1, 0.5, 0.9]
            )
            ```
        """
        if percentiles is None:
            percentiles = [0.25, 0.5, 0.75]
            
        result = {
            'count': len(values),
            'mean': float(np.mean(values)),
            'std': float(np.std(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values))
        }
        
        # 添加分位数
        for p in percentiles:
            result[f'p{int(p*100)}'] = float(np.percentile(values, p*100))
            
        return result
    
    @staticmethod
    def detect_outliers(values: np.ndarray,
                       method: str = 'zscore',
                       threshold: float = 3.0) -> np.ndarray:
        """检测异常值
        
        Args:
            values: 数值数组
            method: 检测方法，可选 'zscore'、'iqr'
            threshold: 异常值判定阈值
            
        Returns:
            np.ndarray: 布尔数组，True表示异常值
            
        Example:
            ```python
            outliers = StatisticsCalculator.detect_outliers(
                values,
                method='iqr',
                threshold=1.5
            )
            ```
        """
        if method == 'zscore':
            z_scores = np.abs((values - np.mean(values)) / np.std(values))
            return z_scores > threshold
        elif method == 'iqr':
            Q1 = np.percentile(values, 25)
            Q3 = np.percentile(values, 75)
            IQR = Q3 - Q1
            return (values < (Q1 - threshold * IQR)) | (values > (Q3 + threshold * IQR))
        else:
            raise ValueError(f"不支持的异常值检测方法: {method}")
    
    @staticmethod
    def calculate_box_plot_stats(values: np.ndarray) -> Dict[str, Any]:
        """计算箱型图统计量
        
        Args:
            values: 数值数组
            
        Returns:
            Dict[str, Any]: 包含箱型图统计量的字典
            
        Example:
            ```python
            stats = StatisticsCalculator.calculate_box_plot_stats(values)
            ```
        """
        q1, q2, q3 = np.percentile(values, [25, 50, 75])
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        
        # 计算异常值
        outliers = values[(values < lower) | (values > upper)]
        
        return {
            "q1": float(q1),
            "q2": float(q2),  # 中位数
            "q3": float(q3),
            "iqr": float(iqr),
            "lower": float(lower),
            "upper": float(upper),
            "outliers": outliers.tolist() if len(outliers) > 0 else []
        }
    
    @staticmethod
    def calculate_distribution_stats(values: np.ndarray,
                                   bins: Optional[Union[int, List[float]]] = None) -> Dict[str, Any]:
        """计算分布统计量
        
        Args:
            values: 数值数组
            bins: 直方图的箱数或边界值
            
        Returns:
            Dict[str, Any]: 包含分布统计量的字典
            
        Example:
            ```python
            stats = StatisticsCalculator.calculate_distribution_stats(values)
            ```
        """
        # 计算核密度估计
        kde = stats.gaussian_kde(values)
        x_range = np.linspace(min(values), max(values), 100)
        kde_values = kde(x_range)
        
        # 计算直方图
        if bins is None:
            bins = 'auto'
        hist, bin_edges = np.histogram(values, bins=bins, density=True)
        
        return {
            "kde": {
                "x": x_range.tolist(),
                "y": kde_values.tolist()
            },
            "histogram": {
                "counts": hist.tolist(),
                "bin_edges": bin_edges.tolist()
            },
            "skewness": float(stats.skew(values)),
            "kurtosis": float(stats.kurtosis(values))
        }
    
    @staticmethod
    def calculate_correlation_stats(x: np.ndarray,
                                  y: np.ndarray) -> Dict[str, Any]:
        """计算相关性统计量
        
        Args:
            x: X轴数据
            y: Y轴数据
            
        Returns:
            Dict[str, Any]: 包含相关性统计量的字典
            
        Example:
            ```python
            stats = StatisticsCalculator.calculate_correlation_stats(x, y)
            ```
        """
        # 计算皮尔逊相关系数
        pearson_r, pearson_p = stats.pearsonr(x, y)
        
        # 计算斯皮尔曼相关系数
        spearman_r, spearman_p = stats.spearmanr(x, y)
        
        # 线性回归
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        return {
            "pearson": {
                "r": float(pearson_r),
                "p": float(pearson_p)
            },
            "spearman": {
                "r": float(spearman_r),
                "p": float(spearman_p)
            },
            "linear_regression": {
                "slope": float(slope),
                "intercept": float(intercept),
                "r_squared": float(r_value ** 2),
                "p_value": float(p_value),
                "std_err": float(std_err)
            }
        } 