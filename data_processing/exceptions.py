"""
数据处理模块的异常类定义，提供了处理过程中可能出现的各类异常。
包括基础异常类和特定类型的异常，用于精确的错误处理。
"""

class ProcessorError(Exception):
    """数据处理器基础异常类
    
    所有数据处理相关的异常的基类。
    
    Example:
        ```python
        try:
            processor.process()
        except ProcessorError as e:
            print(f"处理错误: {str(e)}")
        ```
    """
    pass

class ValidationError(ProcessorError):
    """数据验证异常
    
    当数据或配置验证失败时抛出。
    
    Example:
        ```python
        try:
            processor.validate()
        except ValidationError as e:
            print(f"验证失败: {str(e)}")
        ```
    """
    pass

class FormatError(ProcessorError):
    """格式转换异常
    
    当数据格式转换失败时抛出。
    
    Example:
        ```python
        try:
            processor.to_standard_format()
        except FormatError as e:
            print(f"格式转换失败: {str(e)}")
        ```
    """
    pass

class ConfigError(ProcessorError):
    """配置错误异常
    
    当配置参数无效或配置操作失败时抛出。
    
    Example:
        ```python
        try:
            processor._validate_config()
        except ConfigError as e:
            print(f"配置错误: {str(e)}")
        ```
    """
    pass 