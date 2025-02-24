"""
字体配置测试模块

本模块用于测试matplotlib中文字体配置的有效性，包括：
- 基础配置测试
- 不同字体族测试
- 各类图形元素的中文显示测试
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import matplotlib

matplotlib.use('Agg')  # 设置后端为Agg
import matplotlib.pyplot as plt
import numpy as np

from static_plot.config import BasePlotConfig, StyleConfig


def test_basic_font():
    """基础字体配置测试"""
    # 创建配置
    style_config = StyleConfig()
    
    # 更新matplotlib配置
    plt.rcParams.update(style_config.rc_params)
    
    # 创建测试数据
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    
    # 创建图形
    plt.figure(figsize=style_config.figsize, dpi=style_config.dpi)
    plt.plot(x, y)
    
    # 添加中文文本
    plt.title("中文标题测试")
    plt.xlabel("横轴标签（测试）")
    plt.ylabel("纵轴标签（测试）")
    
    # 添加中文注释
    plt.annotate("重要点", xy=(5, 0.5), xytext=(6, 0.7),
                arrowprops=dict(arrowstyle="->"))
    
    # 保存图形
    plt.savefig("output/font_test_basic.pdf")
    plt.close()

def test_font_families():
    """不同字体族测试"""
    # 创建基础配置
    style_config = StyleConfig()
    plt.rcParams.update(style_config.rc_params)
    
    # 测试数据
    x = np.arange(5)
    y = x ** 2
    
    # 测试不同字体族
    fonts = [
        ("sans-serif", "Heiti TC"),
        ("serif", "Songti SC"),
        ("sans-serif", "STHeiti"),
    ]
    
    fig, axes = plt.subplots(len(fonts), 1, figsize=(6, 8), dpi=style_config.dpi)
    if not isinstance(axes, np.ndarray):
        axes = [axes]
    
    for ax, (family, font) in zip(axes, fonts):
        ax.plot(x, y)
        ax.set_title(f"字体测试 - {font}", fontfamily=family, fontname=font)
        ax.set_xlabel("横轴", fontfamily=family, fontname=font)
        ax.set_ylabel("纵轴", fontfamily=family, fontname=font)
    
    plt.tight_layout()
    plt.savefig("output/font_test_families.pdf")
    plt.close()

def test_with_config():
    """使用完整配置类测试"""
    # 创建完整配置
    config = BasePlotConfig()
    config.style.font_params["size"] = 10  # 增大字号以便观察
    
    # 更新配置
    plt.rcParams.update(config.style.rc_params)
    
    # 创建数据
    categories = ["类别A", "类别B", "类别C", "类别D"]
    values = [15, 25, 10, 30]
    
    # 创建图形
    plt.figure(figsize=config.style.figsize, dpi=config.style.dpi)
    plt.bar(categories, values)
    
    # 设置标题和标签
    plt.title("完整配置测试 - 中文显示", pad=20)
    plt.xlabel("分类变量")
    plt.ylabel("数值变量")
    
    # 添加注释
    plt.annotate("最大值", xy=(3, 30), xytext=(3.2, 32),
                arrowprops=dict(arrowstyle="->"))
    
    # 添加图例
    plt.legend(["数据系列"], loc="upper right")
    
    # 保存图形
    plt.savefig("output/font_test_full_config.pdf")
    plt.close()

if __name__ == "__main__":
    # 运行所有测试
    test_basic_font()
    test_font_families()
    test_with_config()
    print("字体测试完成，请检查生成的PDF文件。") 