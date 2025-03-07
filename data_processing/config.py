"""
数据处理模块的配置类定义，提供了处理器配置的数据结构和验证机制。
包含了基础处理器配置、文件处理配置和表格处理配置等类。
"""
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from data_processing.exceptions import ValidationError


class FileFormat(Enum):
    """文件格式枚举
    
    支持的文件格式类型及其后缀名映射。
    """
    CSV = 'csv'
    EXCEL = 'excel'
    
    @classmethod
    def from_suffix(cls, suffix: str) -> 'FileFormat':
        """从文件后缀名确定文件格式
        
        Args:
            suffix: 文件后缀名
            
        Returns:
            FileFormat: 对应的文件格式枚举值
            
        Raises:
            ValueError: 不支持的文件格式
        """
        suffix = suffix.lower()
        if suffix == '.csv':
            return cls.CSV
        elif suffix in ['.xls', '.xlsx', '.xlsm']:
            return cls.EXCEL
        raise ValueError(f"不支持的文件格式: {suffix}")


@dataclass
class ProcessorConfig:
    """处理器基础配置类
    
    定义了数据处理器的基本配置项，包括输入输出路径、验证规则和处理参数等。
    
    Attributes:
        input_path (Path): 输入文件路径
        output_path (Optional[Path]): 输出文件路径，可选
        validation_rules (Dict[str, Any]): 数据验证规则
        processing_params (Dict[str, Any]): 处理参数
        
    Example:
        ```python
        config = ProcessorConfig(
            input_path="data.csv",
            validation_rules={"required_columns": ["A", "B"]},
            processing_params={"drop_na": True}
        )
        ```
    """
    # 输入输出配置
    input_path: Path
    output_path: Optional[Path] = None
    
    # 验证规则
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    
    # 处理参数
    processing_params: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """配置后处理
        
        将字符串路径转换为Path对象。
        """
        # 确保路径是Path对象
        self.input_path = Path(self.input_path)
        if self.output_path:
            self.output_path = Path(self.output_path)

@dataclass
class FileConfig(ProcessorConfig):
    """文件处理配置类
    
    继承自ProcessorConfig，添加了文件处理相关的配置项。
    
    Attributes:
        file_encoding (str): 文件编码，默认utf-8
        file_format (Optional[FileFormat]): 文件格式，可选值：auto, csv, excel等
        chunk_size (Optional[int]): 分块读取大小，可选，建议大文件设置为10000-50000
        use_cache (bool): 是否使用缓存
        read_only (bool): 是否以只读模式打开Excel文件，大文件建议启用
        
    Example:
        ```python
        config = FileConfig(
            input_path="data.csv",
            file_format="csv",
            chunk_size=10000,
            read_only=True
        )
        ```
    """
    # 文件格式配置
    file_encoding: str = 'utf-8'
    file_format: Optional[FileFormat] = None
    
    # 文件读取配置
    chunk_size: Optional[int] = None  # 分块读取大小
    use_cache: bool = False  # 是否使用缓存
    read_only: bool = True  # Excel文件是否只读模式
    
    def __post_init__(self):
        """配置后处理
        
        除了基类的路径处理，还进行文件格式的自动检测。
        """
        super().__post_init__()
        # 自动检测文件格式
        if self.file_format is None:
            self.file_format = FileFormat.from_suffix(self.input_path.suffix)

@dataclass
class TableConfig(FileConfig):
    """表格文件配置类
    
    继承自FileConfig，添加了表格处理相关的配置项。
    
    Attributes:
        sheet_name (Optional[str]): Excel工作表名，可选
        sheet_names (Optional[List[str]]): 支持多个工作表，可选
        header_row (Optional[int]): 表头行号，默认0
        index_col (Optional[int]): 索引列号，可选
        start_row (Optional[int]): 起始行号，可选
        end_row (Optional[int]): 结束行号，可选
        start_col (Optional[int]): 起始列号，可选
        end_col (Optional[int]): 结束列号，可选
        dtype (Optional[Dict[str, Any]]): 列数据类型，可选
        parse_dates (Optional[List[str]]): 需要解析为日期的列，可选
        
    Example:
        ```python
        config = TableConfig(
            input_path="data.xlsx",
            sheet_name="Sheet1",
            header_row=0,
            parse_dates=["date_column"]
        )
        ```
    """
    # 表格特定配置
    sheet_name: Optional[str] = None  # Excel工作表名
    sheet_names: Optional[List[str]] = None  # 支持多个工作表
    header_row: Optional[int] = 0  # 表头行号
    index_col: Optional[int] = None  # 索引列号
    
    # 数据范围配置
    start_row: Optional[int] = None
    end_row: Optional[int] = None
    start_col: Optional[int] = None
    end_col: Optional[int] = None
    
    # 数据类型配置
    dtype: Optional[Dict[str, Any]] = None  # 列数据类型
    parse_dates: Optional[List[str]] = None  # 需要解析为日期的列 

    def _validate_range(self, start: Optional[int], end: Optional[int], name: str) -> None:
        """验证行列范围
        Args:
            start: 起始索引
            end: 结束索引
            name: 范围名称（行或列）
        Raises:
            ValidationError: 范围无效时抛出
        """
        if (start is not None and start < 0) or (end is not None and end < 0):
            raise ValidationError(f"{name}索引必须为非负数");
        if (start is not None and end is not None and start > end):
            raise ValidationError(f"{name}起始索引必须小于或等于结束索引");

    def _validate_config(self) -> None:
        """验证表格配置
        验证表格特有的配置项，包括行列范围的有效性。
        Raises:
            ValidationError: 配置无效时抛出
        """
        super()._validate_config();
        self._validate_range(self.start_row, self.end_row, "行");
        self._validate_range(self.start_col, self.end_col, "列"); 