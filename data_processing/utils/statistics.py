"""
统计分析工具模块，提供了数据统计和分析的功能。
包含了基础统计计算、描述性统计和数据分析等功能的实现。
"""
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from scipy import stats


class StatisticsCalculator:
    """统计计算器类
    
    提供各种统计计算功能，用于计算数据的统计量和分布特征。
    所有方法都是静态方法，可以直接调用。
    """
    
    @staticmethod
    def calculate_basic_stats(values: np.ndarray) -> Dict[str, Any]:
        """计算基本统计量
        
        计算数据的基本统计量，包括最小值、最大值、平均值、中位数等。
        
        Args:
            values: 数据数组
            
        Returns:
            Dict[str, Any]: 基本统计量字典
        """
        # 处理空数组
        if len(values) == 0:
            return {
                "min": None,
                "max": None,
                "mean": None,
                "median": None,
                "std": None,
                "count": 0
            }
        
        # 计算基本统计量
        return {
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "std": float(np.std(values)),
            "count": int(len(values))
        }
    
    @staticmethod
    def calculate_correlation(x: np.ndarray,
                            y: np.ndarray,
                            method: str = 'pearson') -> float:
        """计算相关系数
        
        计算两个数组之间的相关系数。
        
        Args:
            x: 第一个数组
            y: 第二个数组
            method: 相关系数类型，可选值：pearson, spearman, kendall
            
        Returns:
            float: 相关系数
            
        Raises:
            ValueError: 方法无效或数据无效时抛出
        """
        # 验证数组长度
        if len(x) != len(y):
            raise ValueError("数组长度不一致")
        
        # 验证method参数
        valid_methods = ['pearson', 'spearman', 'kendall']
        if method not in valid_methods:
            raise ValueError(f"无效的相关系数方法，可选值：{', '.join(valid_methods)}")
        
        # 计算相关系数
        if method == 'pearson':
            return float(np.corrcoef(x, y)[0, 1])
        elif method == 'spearman':
            return float(stats.spearmanr(x, y)[0])
        elif method == 'kendall':
            return float(stats.kendalltau(x, y)[0])
    
    @staticmethod
    def calculate_distribution(values: np.ndarray,
                             bins: Optional[Union[int, List[float]]] = None) -> Tuple[np.ndarray, np.ndarray]:
        """计算分布
        
        计算数据的分布直方图。
        
        Args:
            values: 数据数组
            bins: 分箱数或分箱边界列表
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: 直方图计数和箱边界
        """
        # 如果没有指定bins，根据数据量自动选择
        if bins is None:
            bins = min(int(np.sqrt(len(values))), 50)
        
        # 计算直方图
        hist, bin_edges = np.histogram(values, bins=bins, density=True)
        return hist, bin_edges
    
    @staticmethod
    def calculate_summary(values: np.ndarray,
                         percentiles: Optional[List[float]] = None) -> Dict[str, float]:
        """计算汇总统计量
        
        计算数据的汇总统计量，包括百分位数、偏度、峰度等。
        
        Args:
            values: 数据数组
            percentiles: 百分位数列表，默认为[0.25, 0.5, 0.75]
            
        Returns:
            Dict[str, float]: 汇总统计量字典
        """
        # 默认百分位数
        if percentiles is None:
            percentiles = [0.25, 0.5, 0.75]
        
        # 处理空数组
        if len(values) == 0:
            return {f"p{int(p*100)}": None for p in percentiles}
        
        # 计算汇总统计量
        summary = {}
        
        # 计算百分位数
        for p in percentiles:
            summary[f"p{int(p*100)}"] = float(np.percentile(values, p * 100))
        
        # 计算偏度和峰度
        if len(values) > 2:
            summary["skewness"] = float(stats.skew(values))
            summary["kurtosis"] = float(stats.kurtosis(values))
        
        return summary
    
    @staticmethod
    def detect_outliers(values: np.ndarray,
                       method: str = 'zscore',
                       threshold: float = 3.0) -> np.ndarray:
        """检测异常值
        
        根据指定方法检测数据中的异常值。
        
        Args:
            values: 数据数组
            method: 检测方法，可选值：zscore, iqr
            threshold: 阈值
            
        Returns:
            np.ndarray: 布尔掩码数组，True表示异常值
            
        Raises:
            ValueError: 方法无效时抛出
        """
        # 验证方法参数
        valid_methods = ['zscore', 'iqr']
        if method not in valid_methods:
            raise ValueError(f"无效的异常值检测方法，可选值：{', '.join(valid_methods)}")
        
        # Z-score方法
        if method == 'zscore':
            z_scores = np.abs((values - np.mean(values)) / np.std(values))
            return z_scores > threshold
        
        # IQR方法
        elif method == 'iqr':
            q1 = np.percentile(values, 25)
            q3 = np.percentile(values, 75)
            iqr = q3 - q1
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            return (values < lower_bound) | (values > upper_bound)
    
    @staticmethod
    def calculate_box_plot_stats(values: np.ndarray) -> Dict[str, Any]:
        """计算箱线图统计量
        
        计算箱线图所需的统计量。
        
        Args:
            values: 数据数组
            
        Returns:
            Dict[str, Any]: 箱线图统计量字典
        """
        # 处理空数组
        if len(values) == 0:
            return {
                "min": None,
                "q1": None,
                "median": None,
                "q3": None,
                "max": None,
                "outliers": []
            }
        
        # 计算四分位数
        q1 = float(np.percentile(values, 25))
        median = float(np.median(values))
        q3 = float(np.percentile(values, 75))
        
        # 计算IQR
        iqr = q3 - q1
        
        # 计算上下边界
        lower_bound = max(float(np.min(values)), q1 - 1.5 * iqr)
        upper_bound = min(float(np.max(values)), q3 + 1.5 * iqr)
        
        # 查找异常值
        outliers = values[(values < lower_bound) | (values > upper_bound)].tolist()
        
        return {
            "min": lower_bound,
            "q1": q1,
            "median": median,
            "q3": q3,
            "max": upper_bound,
            "outliers": outliers
        }
    
    @staticmethod
    def calculate_distribution_stats(values: np.ndarray,
                                   bins: Optional[Union[int, List[float]]] = None) -> Dict[str, Any]:
        """计算分布统计量
        
        计算数据分布的相关统计量。
        
        Args:
            values: 数据数组
            bins: 分箱数或分箱边界列表
            
        Returns:
            Dict[str, Any]: 分布统计量字典
        """
        # 处理空数组
        if len(values) == 0:
            return {
                "hist": [],
                "bin_edges": [],
                "bin_centers": []
            }
        
        # 计算直方图
        hist, bin_edges = StatisticsCalculator.calculate_distribution(values, bins)
        
        # 计算bin中心
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        # 添加正态分布拟合
        try:
            mu, sigma = stats.norm.fit(values)
            pdf = stats.norm.pdf(bin_centers, mu, sigma)
            fit_result = {
                "mu": float(mu),
                "sigma": float(sigma),
                "pdf": pdf.tolist()
            }
        except Exception:
            fit_result = {
                "mu": None,
                "sigma": None,
                "pdf": []
            }
        
        return {
            "hist": hist.tolist(),
            "bin_edges": bin_edges.tolist(),
            "bin_centers": bin_centers.tolist(),
            "fit": fit_result
        }
    
    @staticmethod
    def calculate_correlation_stats(x: np.ndarray,
                                  y: np.ndarray) -> Dict[str, Any]:
        """计算相关性统计量
        
        计算两个数组之间的相关性统计量。
        
        Args:
            x: 第一个数组
            y: 第二个数组
            
        Returns:
            Dict[str, Any]: 相关性统计量字典
        """
        # 验证数组长度
        if len(x) != len(y):
            return {
                "pearson": None,
                "spearman": None,
                "kendall": None,
                "linear_fit": {
                    "slope": None,
                    "intercept": None,
                    "r_value": None,
                    "p_value": None,
                    "std_err": None
                }
            }
        
        # 计算相关系数
        try:
            pearson = StatisticsCalculator.calculate_correlation(x, y, 'pearson')
            spearman = StatisticsCalculator.calculate_correlation(x, y, 'spearman')
            kendall = StatisticsCalculator.calculate_correlation(x, y, 'kendall')
        except Exception:
            pearson = spearman = kendall = None
        
        # 线性回归
        try:
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            linear_fit = {
                "slope": float(slope),
                "intercept": float(intercept),
                "r_value": float(r_value),
                "p_value": float(p_value),
                "std_err": float(std_err)
            }
        except Exception:
            linear_fit = {
                "slope": None,
                "intercept": None,
                "r_value": None,
                "p_value": None,
                "std_err": None
            }
        
        return {
            "pearson": pearson,
            "spearman": spearman,
            "kendall": kendall,
            "linear_fit": linear_fit
        }
    
    @staticmethod
    def calculate_characteristic_diameters(
        diameters: np.ndarray,
        cumulative: np.ndarray,
        percentages: Optional[List[float]] = None
    ) -> Dict[str, float]:
        """计算特征粒径
        
        通过插值计算特定累积百分比对应的粒径值。
        
        Args:
            diameters: 粒径数组（升序）
            cumulative: 累积分布数组（升序）
            percentages: 需要计算的百分比列表，默认为[10, 30, 50, 60]
            
        Returns:
            Dict[str, float]: 特征粒径字典，key为"d{percentage}"格式
        """
        if percentages is None:
            percentages = [10, 30, 50, 60]
            
        # 确保数据是升序的
        sort_idx = np.argsort(cumulative)
        x = cumulative[sort_idx]
        y = diameters[sort_idx]
        
        # 使用线性插值计算特征粒径
        result = {}
        for p in percentages:
            try:
                d = float(np.interp(p, x, y))
                result[f"d{p}"] = d
            except Exception:
                result[f"d{p}"] = np.nan
                
        # 计算均匀系数和曲率系数（如果可能）
        if "d60" in result and "d10" in result and result["d10"] > 0:
            result["Cu"] = result["d60"] / result["d10"]  # 均匀系数
            if "d30" in result:
                result["Cc"] = (result["d30"]**2) / (result["d10"] * result["d60"])  # 曲率系数
                
        return result 