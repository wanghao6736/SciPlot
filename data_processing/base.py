"""
数据处理模块的基础抽象类，定义了数据处理的标准接口和流程。
提供了数据处理器和文件处理器的基类，实现了基础的数据处理流程和验证机制。
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import pandas as pd

from data_processing.config import FileConfig, ProcessorConfig
from data_processing.exceptions import ProcessorError, ValidationError


class DataProcessor(ABC):
    """数据处理器基础抽象类
    
    定义了数据处理的标准接口，包括数据验证、处理和格式转换等功能。
    所有具体的数据处理器都应继承自此类并实现其抽象方法。
    
    Attributes:
        config (ProcessorConfig): 处理器配置对象
        _data (Optional[pd.DataFrame]): 处理后的数据，初始为None
        
    Example:
        ```python
        class MyProcessor(DataProcessor):
            def _validate_config(self):
                super()._validate_config()
                # 添加自定义验证
                
            def validate(self) -> bool:
                return True  # 实现具体的验证逻辑
                
            def process(self) -> pd.DataFrame:
                # 实现数据处理逻辑
                return pd.DataFrame()
                
            def to_standard_format(self) -> Dict[str, Any]:
                # 实现格式转换逻辑
                return {"data": self.data.to_dict()}
        ```
    """
    
    def __init__(self, config: ProcessorConfig):
        """初始化数据处理器
        
        Args:
            config: 处理器配置对象
            
        Raises:
            ValidationError: 配置验证失败时抛出
        """
        self.config = config
        self._data: Optional[pd.DataFrame] = None
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """验证配置有效性
        
        验证处理器配置是否满足要求。基类实现了基础的路径验证，
        子类应该重写此方法以添加特定的验证逻辑。
        
        Raises:
            ValidationError: 配置无效时抛出
        """
        if not self.config.input_path.exists():
            raise ValidationError(f"输入路径不存在: {self.config.input_path}")
    
    @abstractmethod
    def validate(self) -> bool:
        """验证数据有效性
        
        Returns:
            bool: 数据是否有效
        """
        pass
    
    @abstractmethod
    def process(self) -> pd.DataFrame:
        """处理数据
        
        Returns:
            pd.DataFrame: 处理后的数据框
            
        Raises:
            ProcessorError: 处理过程出错时抛出
        """
        pass
    
    @abstractmethod
    def to_standard_format(self) -> Dict[str, Any]:
        """转换为标准格式
        
        Returns:
            Dict[str, Any]: 标准格式的数据字典
            
        Raises:
            ProcessorError: 转换失败时抛出
        """
        pass
    
    @property
    def data(self) -> pd.DataFrame:
        """获取处理后的数据
        
        Returns:
            pd.DataFrame: 处理后的数据框
            
        Raises:
            ProcessorError: 数据未处理时抛出
        """
        if self._data is None:
            raise ProcessorError("数据未处理")
        return self._data

class FileProcessor(DataProcessor):
    """文件处理器基础抽象类
    
    继承自DataProcessor，专门用于处理文件类型的数据。
    实现了标准的文件处理流程，包括文件读取、预处理和后处理等步骤。
    
    Attributes:
        config (FileConfig): 文件处理配置对象
        
    Example:
        ```python
        class CSVProcessor(FileProcessor):
            def _read_file(self) -> pd.DataFrame:
                return pd.read_csv(self.config.input_path)
                
            def _preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
                return df.dropna()  # 简单的预处理
                
            def _postprocess(self, df: pd.DataFrame) -> pd.DataFrame:
                return df.reset_index()  # 简单的后处理
        ```
    """
    
    def __init__(self, config: FileConfig):
        """初始化文件处理器
        
        Args:
            config: 文件处理配置对象
            
        Raises:
            ValidationError: 配置验证失败时抛出
        """
        super().__init__(config)
        self.config: FileConfig = config  # 类型标注
    
    @abstractmethod
    def _read_file(self) -> pd.DataFrame:
        """读取文件
        
        Returns:
            pd.DataFrame: 读取的数据框
            
        Raises:
            ProcessorError: 文件读取失败时抛出
        """
        pass
    
    @abstractmethod
    def _preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """预处理数据
        
        Args:
            df: 输入数据框
            
        Returns:
            pd.DataFrame: 预处理后的数据框
        """
        pass
    
    @abstractmethod
    def _postprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """后处理数据
        
        Args:
            df: 输入数据框
            
        Returns:
            pd.DataFrame: 后处理后的数据框
        """
        pass
    
    def process(self) -> pd.DataFrame:
        """处理数据的标准流程
        
        实现了文件处理的标准流程：
        1. 读取文件
        2. 预处理数据
        3. 验证数据
        4. 后处理数据
        
        Returns:
            pd.DataFrame: 处理后的数据框
            
        Raises:
            ProcessorError: 处理过程出错时抛出
            ValidationError: 数据验证失败时抛出
        """
        # 读取文件
        df = self._read_file()
        
        # 预处理
        df = self._preprocess(df)
        
        # 验证数据
        self._data = df
        validation_result = self.validate()
        if not validation_result:
            raise ValidationError("数据验证失败")
        
        # 后处理
        df = self._postprocess(df)
        
        self._data = df
        return df
    
    def _validate_config(self) -> None:
        """验证文件处理器配置
        
        除了基础的路径验证，还验证了文件格式是否指定。
        
        Raises:
            ValidationError: 配置无效时抛出
        """
        super()._validate_config()
        if not self.config.file_format:
            raise ValidationError("文件格式未指定")
    
    def validate(self) -> bool:
        """验证数据的基础实现
        
        只进行最基本的非空验证，具体的验证逻辑应由子类实现。
        
        Returns:
            bool: 数据是否有效
        """
        return self._data is not None
    
    def to_standard_format(self) -> Dict[str, Any]:
        """转换为标准格式的默认实现
        
        将数据框转换为包含数据和元数据的标准字典格式。
        
        Returns:
            Dict[str, Any]: 标准格式的数据字典，包含：
                - data: 数据字典
                - metadata: 包含行数、列名和数据类型的元数据
                
        Raises:
            ProcessorError: 数据未处理时抛出
        """
        if self._data is None:
            raise ProcessorError("数据未处理")
        
        return {
            "data": self._data.to_dict(),
            "metadata": {
                "rows": len(self._data),
                "columns": list(self._data.columns),
                "dtypes": self._data.dtypes.to_dict()
            }
        } 