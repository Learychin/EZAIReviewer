import streamlit as st
import os
import shutil
from pathlib import Path

def export_dashboard():
    # 获取当前目录
    current_dir = Path(__file__).parent
    
    # 创建输出目录
    output_dir = current_dir / "static_export"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()
    
    # 复制所有必要的文件
    files_to_copy = [
        "rating_dashboard.py",
        "course_ratings.json",
        "ratings_meta.json",
        "students.json",
        "teachers.json",
        "courses.json"
    ]
    
    for file in files_to_copy:
        if (current_dir / file).exists():
            shutil.copy2(current_dir / file, output_dir / file)
    
    # 创建启动脚本
    with open(output_dir / "run_dashboard.py", "w", encoding="utf-8") as f:
        f.write("""
import streamlit as st
import os

# 设置页面配置
st.set_page_config(
    page_title="评分仪表板",
    page_icon="📊",
    layout="wide"
)

# 运行主仪表板
with open("rating_dashboard.py", "r", encoding="utf-8") as f:
    exec(f.read())
""")
    
    # 创建README文件
    with open(output_dir / "README.md", "w", encoding="utf-8") as f:
        f.write("""
# 离线评分仪表板

这是一个可以离线运行的评分仪表板。

## 运行方法

1. 确保已安装所需的Python包：
   ```
   pip install streamlit pandas plotly
   ```

2. 运行仪表板：
   ```
   streamlit run run_dashboard.py
   ```

3. 在浏览器中打开显示的地址（通常是 http://localhost:8501）

## 注意事项

- 所有数据文件都已包含在此目录中
- 无需网络连接即可运行
- 可以复制整个目录到其他电脑上运行
""")
    
    print(f"仪表板已导出到: {output_dir}")
    print("请按照 README.md 中的说明运行仪表板")

if __name__ == "__main__":
    export_dashboard() 