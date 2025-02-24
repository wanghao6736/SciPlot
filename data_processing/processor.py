"""
数据处理器具体实现模块，提供了表格文件处理器的实现。
支持CSV和Excel格式的文件读取、处理和验证。
"""
from typing import Any, Dict, Optional

import pandas as pd

from data_processing.base import FileProcessor
from data_processing.config import TableConfig
from data_processing.exceptions import ProcessorError, ValidationError
from data_processing.utils.formatters import DataFormatter


class TableFileProcessor(FileProcessor):
    """表格文件处理器
    
    实现了对CSV和Excel格式表格文件的处理功能，支持数据的读取、
    预处理、验证和后处理等操作。可以通过配置控制数据处理的各个环节。
    
    Attributes:
        config (TableConfig): 表格处理配置对象
        _formatter (Optional[DataFormatter]): 数据格式化器，可选
        
    Example:
        ```python
        # 创建配置
        config = TableConfig(
            input_path="data.csv",
            validation_rules={"required_columns": ["A", "B"]},
            processing_params={"drop_duplicates": True}
        )
        
        # 创建处理器
        processor = TableFileProcessor(config)
        
        # 处理数据
        df = processor.process()
        
        # 获取标准格式
        result = processor.to_standard_format()
        ```
    """
    
    def __init__(self, config: TableConfig, formatter: Optional[DataFormatter] = None):
        """初始化表格文件处理器
        
        Args:
            config: 表格处理配置对象
            formatter: 数据格式化器，可选
            
        Raises:
            ValidationError: 配置验证失败时抛出
        """
        super().__init__(config)
        self.config: TableConfig = config  # 类型标注
        self._formatter = formatter
    
    def _validate_config(self) -> None:
        """验证表格配置
        
        验证表格特有的配置项，包括行列范围的有效性。
        
        Raises:
            ValidationError: 配置无效时抛出
        """
        super()._validate_config()
        
        # 验证行列范围
        if (self.config.start_row is not None and self.config.start_row < 0) or \
           (self.config.end_row is not None and self.config.end_row < 0) or \
           (self.config.start_col is not None and self.config.start_col < 0) or \
           (self.config.end_col is not None and self.config.end_col < 0):
            raise ValidationError("行列索引必须为非负数")
        
        if (self.config.start_row is not None and self.config.end_row is not None and 
            self.config.start_row > self.config.end_row):
            raise ValidationError("起始行必须小于或等于结束行")
        
        if (self.config.start_col is not None and self.config.end_col is not None and 
            self.config.start_col > self.config.end_col):
            raise ValidationError("起始列必须小于或等于结束列")
    
    def _read_file(self) -> pd.DataFrame:
        """读取表格文件
        
        根据文件格式调用相应的读取方法。
        
        Returns:
            pd.DataFrame: 读取的数据框
            
        Raises:
            ProcessorError: 文件读取失败时抛出
        """
        try:
            if self.config.file_format == 'csv':
                return self._read_csv()
            elif self.config.file_format == 'excel':
                return self._read_excel()
            else:
                raise ProcessorError(f"不支持的文件格式: {self.config.file_format}")
        except Exception as e:
            raise ProcessorError(f"文件读取错误: {str(e)}")
    
    def _read_csv(self) -> pd.DataFrame:
        """读取CSV文件
        
        根据配置读取CSV文件，支持设置读取范围、数据类型等。
        
        Returns:
            pd.DataFrame: 读取的数据框
            
        Raises:
            ProcessorError: 文件读取失败时抛出
        """
        read_params = {
            'filepath_or_buffer': self.config.input_path,
            'encoding': self.config.file_encoding,
            'header': self.config.header_row,
            'index_col': self.config.index_col
        }
        
        # 设置读取范围
        if self.config.start_row is not None:
            read_params['skiprows'] = range(1, self.config.start_row + 1)
        if self.config.end_row is not None:
            read_params['nrows'] = self.config.end_row - (self.config.start_row or 0)
            
        # 设置数据类型
        if self.config.dtype:
            read_params['dtype'] = self.config.dtype
        if self.config.parse_dates:
            read_params['parse_dates'] = self.config.parse_dates
        df = pd.read_csv(**read_params)
        return self._slice_columns(df)
    
    def _read_excel(self) -> pd.DataFrame:
        """读取Excel文件
        
        根据配置读取Excel文件，支持设置工作表、读取范围等。
        
        Returns:
            pd.DataFrame: 读取的数据框
            
        Raises:
            ProcessorError: 文件读取失败时抛出
        """
        read_params = {
            'io': self.config.input_path,
            'sheet_name': self.config.sheet_name,
            'header': self.config.header_row,
            'index_col': self.config.index_col
        }
        
        # 设置读取范围
        if self.config.start_row is not None:
            read_params['skiprows'] = range(1, self.config.start_row + 1)
        if self.config.end_row is not None:
            read_params['nrows'] = self.config.end_row - (self.config.start_row or 0)
            
        # 设置数据类型
        if self.config.dtype:
            read_params['dtype'] = self.config.dtype
        df = pd.read_excel(**read_params)
        return self._slice_columns(df)
    
    def _slice_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """切片数据框的列
        
        根据配置的列范围对数据框进行切片。
        
        Args:
            df: 输入数据框
            
        Returns:
            pd.DataFrame: 切片后的数据框
        """
        if self.config.start_col is not None or self.config.end_col is not None:
            start = self.config.start_col if self.config.start_col is not None else 0
            end = self.config.end_col if self.config.end_col is not None else len(df.columns)
            df = df.iloc[:, start:end]
        return df
    
    def _preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """预处理表格数据
        
        根据配置进行数据预处理，包括处理缺失值和重复值等。
        
        Args:
            df: 输入数据框
            
        Returns:
            pd.DataFrame: 预处理后的数据框
        """
        # 1. 处理缺失值
        if 'handle_missing' in self.config.processing_params:
            method = self.config.processing_params['handle_missing']
            if method == 'drop':
                df = df.dropna()
            elif method == 'fill':
                fill_value = self.config.processing_params.get('fill_value', 0)
                df = df.fillna(fill_value)
        
        # 2. 处理重复值
        if self.config.processing_params.get('drop_duplicates', False):
            df = df.drop_duplicates()
        
        return df
    
    def _postprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """后处理表格数据
        
        根据配置进行数据后处理，包括重置索引和重命名列等。
        
        Args:
            df: 输入数据框
            
        Returns:
            pd.DataFrame: 后处理后的数据框
        """
        # 1. 重置索引
        if self.config.processing_params.get('reset_index', False):
            df = df.reset_index(drop=True)
        
        # 2. 列重命名
        if 'rename_columns' in self.config.processing_params:
            df = df.rename(columns=self.config.processing_params['rename_columns'])
        
        return df
    
    def validate(self) -> bool:
        """验证表格数据
        
        验证数据是否满足配置的验证规则，包括检查必需列和数据类型等。
        
        Returns:
            bool: 数据是否有效
        """
        # 基础验证
        if not super().validate():
            return False
            
        # 空数据验证
        if self._data.empty:
            return False
            
        # 检查必需列
        if 'required_columns' in self.config.validation_rules:
            required = set(self.config.validation_rules['required_columns'])
            if not required.issubset(self._data.columns):
                return False
        
        # 检查数据类型
        if 'column_types' in self.config.validation_rules:
            for col, dtype in self.config.validation_rules['column_types'].items():
                if col in self._data.columns and not pd.api.types.is_dtype_equal(self._data[col].dtype, dtype):
                    return False
        
        return True
    
    def to_standard_format(self) -> Dict[str, Any]:
        """转换为标准格式
        
        将数据转换为标准格式，如果设置了格式化器则使用格式化器进行转换。
        
        Returns:
            Dict[str, Any]: 标准格式的数据字典
            
        Raises:
            ProcessorError: 数据未处理时抛出
        """
        if self._data is None:
            raise ProcessorError("数据尚未处理")
            
        # 获取基础格式
        base_format = {
            "data": self._data.to_dict(),
            "metadata": {
                "rows": len(self._data),
                "columns": list(self._data.columns),
                "dtypes": self._data.dtypes.to_dict()
            }
        }
        
        # 如果有格式化器，进行特定格式转换
        if self._formatter:
            return self._formatter.format(base_format)
        
        return base_format
