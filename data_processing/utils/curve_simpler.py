"""
曲线简化工具模块

本模块实现了基于Douglas-Peucker算法的曲线简化功能,可用于压缩和分析各类数据曲线。
主要功能:
1. 曲线关键点提取
2. 曲线相似度计算
3. 自适应阈值选择

适用场景:
- 粒径分布曲线简化
- 应力应变曲线压缩
- 其他需要保持关键特征的曲线数据压缩
"""

from dataclasses import dataclass
from typing import List

import numpy as np
from numba import njit

# 类型别名
Points = np.ndarray  # shape: (N, 2)
Vector = np.ndarray  # shape: (N,)

@dataclass
class CurveData:
    """曲线数据类
    
    用于存储和处理二维曲线数据。
    
    Attributes:
        x: Vector, x轴数据(如粒径、应变等)
        y: Vector, y轴数据(如累积分布、应力等)
    """
    x: Vector  # x轴数据
    y: Vector  # y轴数据
    
    @property
    def points(self) -> Points:
        """返回点集形式的数据
        
        将x和y数据组合为二维点集,便于几何计算。
        
        Returns:
            Points: 包含x和y数据的点集,shape为(N, 2)
        """
        return np.column_stack((self.x, self.y))

class CurveSimplifier:
    """曲线简化器
    
    使用Douglas-Peucker算法对曲线进行简化,通过自适应阈值选择保证简化质量。
    支持任意二维曲线数据的简化,如粒径分布曲线、应力应变曲线等。
    
    主要特点:
    1. 自适应阈值选择
    2. 保持关键拐点
    3. 基于NCC的质量控制
    
    Example:
        ```python
        # 创建简化器
        simplifier = CurveSimplifier(target_ncc=0.995)
        
        # 简化曲线
        curve_data = CurveData(x=diameters, y=cumulative)
        simplified = simplifier.simplify(curve_data)
        ```
    """
    
    def __init__(self, target_ncc: float = 0.995):
        """初始化曲线简化器
        
        Args:
            target_ncc: float, 目标NCC值，用于控制简化质量，默认0.995
                       值越大保留的点越多,曲线还原度越高
        """
        self.target_ncc = target_ncc
        self.epsilon = None
    
    def _find_optimal_epsilon(self, data: CurveData, 
                            initial_epsilon: float = 1.0,
                            max_iterations: int = 50,
                            ncc_tolerance: float = 1e-4) -> float:
        """使用非递归的改进区间搜索算法寻找最优epsilon值
        
        通过二分搜索找到能满足目标NCC值的最优epsilon值。
        搜索过程会平衡简化程度和还原精度。
        
        Args:
            data: CurveData, 原始曲线数据
            initial_epsilon: float, 初始epsilon值，默认1.0
            max_iterations: int, 最大迭代次数，默认50
            ncc_tolerance: float, NCC容差，默认1e-4
        
        Returns:
            float: 最优epsilon值
        """
        left = 1e-6
        right = 1.0
        best_epsilon = initial_epsilon
        best_ncc_diff = float('inf')
        
        def evaluate_epsilon(eps: float) -> float:
            """评估指定epsilon值的效果
            
            Args:
                eps: float, epsilon值
            
            Returns:
                float: 计算得到的NCC值
            """
            simplified = self._simplify_with_epsilon(data, eps)
            ncc = self.calculate_ncc(data, simplified)
            return ncc
        
        stack = [(left, right, 0)]
        
        while stack:
            left, right, depth = stack.pop()
            
            if depth >= max_iterations or right - left < ncc_tolerance:
                continue
            
            mid = (left + right) / 2
            ncc = evaluate_epsilon(mid)
            
            current_diff = abs(self.target_ncc - ncc)
            if current_diff < ncc_tolerance:
                return mid
            
            if current_diff < best_ncc_diff:
                best_ncc_diff = current_diff
                best_epsilon = mid
            
            mid_left = (left + mid) / 2
            mid_right = (mid + right) / 2
            ncc_left = evaluate_epsilon(mid_left)
            ncc_right = evaluate_epsilon(mid_right)
            
            if abs(ncc_left - self.target_ncc) < abs(ncc_right - self.target_ncc):
                stack.append((left, mid, depth + 1))
            else:
                stack.append((mid, right, depth + 1))
        
        return best_epsilon
    
    @staticmethod
    @njit
    def _perpendicular_distance(points: Points, start: Points, end: Points) -> Vector:
        """计算点到线段的垂直距离
        
        使用向量计算方法计算点集到线段的垂直距离。
        使用numba加速计算。
        
        Args:
            points: Points, 待计算的点集
            start: Points, 线段起始点
            end: Points, 线段结束点
        
        Returns:
            Vector: 每个点到线段的垂直距离
        """
        if np.all(start == end):
            diff = points - start
            return np.sqrt(np.sum(diff * diff, axis=1))
        
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        val = np.abs(dy*points[:, 0] - dx*points[:, 1] - start[0]*dy + start[1]*dx)
        return val / np.sqrt(dx*dx + dy*dy)
    
    def simplify(self, data: CurveData) -> CurveData:
        """简化曲线
        
        主要简化流程:
        1. 如果未指定epsilon,自动寻找最优值
        2. 使用Douglas-Peucker算法提取关键点
        3. 返回简化后的曲线数据
        
        Args:
            data: CurveData, 原始曲线数据
        
        Returns:
            CurveData: 简化后的曲线数据
        """
        if self.epsilon is None:
            self.epsilon = self._find_optimal_epsilon(data)
        
        return self._simplify_with_epsilon(data, self.epsilon)
    
    def _simplify_with_epsilon(self, data: CurveData, epsilon: float) -> CurveData:
        """使用指定epsilon值简化曲线
        
        Args:
            data: CurveData, 原始曲线数据
            epsilon: float, 简化阈值
        
        Returns:
            CurveData: 简化后的曲线数据
        """
        points = data.points
        key_points = self._douglas_peucker_iterative(points, epsilon)
        return CurveData(
            x=np.array([p[0] for p in key_points]),
            y=np.array([p[1] for p in key_points])
        )
    
    def _douglas_peucker_iterative(self, points: Points, epsilon: float) -> List[Points]:
        """Douglas-Peucker算法的迭代实现
        
        使用栈代替递归实现Douglas-Peucker算法,提高效率和避免栈溢出。
        算法步骤:
        1. 选择曲线首尾点作为初始线段
        2. 计算其他点到该线段的垂直距离
        3. 如果最大距离大于阈值,在该点处分割曲线
        4. 重复以上步骤直到所有分段的最大距离都小于阈值
        
        Args:
            points: Points, 待简化的点集
            epsilon: float, 简化阈值
        
        Returns:
            List[Points]: 简化后的关键点集
        """
        stack = [(0, len(points) - 1)]
        result = [0, len(points) - 1]
        
        while stack:
            start, end = stack.pop()
            if end - start <= 1:
                continue
            
            segment = points[start:end+1]
            if len(segment) <= 2:
                continue
            
            distances = self._perpendicular_distance(
                segment[1:-1], segment[0], segment[-1]
            )
            
            dmax = np.max(distances)
            index = np.argmax(distances) + start + 1
            
            if dmax > epsilon:
                stack.extend([(start, index), (index, end)])
                result.append(index)
        
        return [points[i] for i in sorted(set(result))]
    
    @staticmethod
    def calculate_ncc(curve1: CurveData, curve2: CurveData) -> float:
        """计算归一化互相关系数(NCC)
        
        用于评估两条曲线的相似度,值域为[-1,1]:
        1: 完全正相关
        0: 无相关
        -1: 完全负相关
        
        计算步骤:
        1. 将curve2插值到curve1的x坐标点
        2. 计算两组y值的归一化互相关系数
        
        Args:
            curve1: CurveData, 原始曲线数据
            curve2: CurveData, 对比曲线数据(通常是简化后的曲线)
        
        Returns:
            float: 归一化互相关系数
        """
        from scipy.interpolate import interp1d
        
        f = interp1d(curve2.x, curve2.y, fill_value="extrapolate")
        y2_interp = f(curve1.x)
        
        mean_y1 = np.mean(curve1.y)
        mean_y2 = np.mean(y2_interp)
        std_y1 = np.std(curve1.y)
        std_y2 = np.std(y2_interp)
        
        if std_y1 == 0 or std_y2 == 0:
            return 0
        
        ncc = np.sum((curve1.y - mean_y1) * (y2_interp - mean_y2)) / (
            std_y1 * std_y2 * len(curve1.y)
        )
        return ncc