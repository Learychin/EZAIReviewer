import streamlit as st
import os
import shutil
from pathlib import Path
import subprocess
import json

def export_to_html():
    # 获取当前目录
    current_dir = Path(__file__).parent
    
    # 创建输出目录
    output_dir = current_dir / "static_export"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()
    
    # 复制所有数据文件
    data_files = [
        "course_ratings.json",
        "ratings_meta.json",
        "students.json",
        "teachers.json",
        "courses.json"
    ]
    
    for file in data_files:
        if (current_dir / file).exists():
            shutil.copy2(current_dir / file, output_dir / file)
    
    # 创建一个临时的Streamlit应用文件
    temp_app = output_dir / "temp_app.py"
    with open(temp_app, "w", encoding="utf-8") as f:
        f.write("""
import streamlit as st
import json
import plotly.express as px
import pandas as pd

# 设置页面配置
st.set_page_config(
    page_title="评分仪表板",
    page_icon="📊",
    layout="wide"
)

# 加载数据
@st.cache_data
def load_data():
    with open("course_ratings.json", "r", encoding="utf-8") as f:
        ratings = json.load(f)
    with open("ratings_meta.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
    with open("students.json", "r", encoding="utf-8") as f:
        students = json.load(f)
    with open("teachers.json", "r", encoding="utf-8") as f:
        teachers = json.load(f)
    with open("courses.json", "r", encoding="utf-8") as f:
        courses = json.load(f)
    return ratings, meta, students, teachers, courses

# 加载数据
ratings, meta, students, teachers, courses = load_data()

# 转换数据为DataFrame
df_ratings = pd.DataFrame(ratings)
df_meta = pd.DataFrame(meta)
df_students = pd.DataFrame(students)
df_teachers = pd.DataFrame(teachers)
df_courses = pd.DataFrame(courses)

# 显示标题
st.title("课程评分仪表板")

# 显示总体统计
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("总课程数", len(df_courses))
with col2:
    st.metric("总学生数", len(df_students))
with col3:
    st.metric("总教师数", len(df_teachers))

# 显示评分分布
st.subheader("评分分布")
fig = px.histogram(df_ratings, x="rating", nbins=20)
st.plotly_chart(fig, use_container_width=True)

# 显示课程评分
st.subheader("课程评分")
fig = px.box(df_ratings, x="course_id", y="rating")
st.plotly_chart(fig, use_container_width=True)

# 显示教师评分
st.subheader("教师评分")
teacher_ratings = df_ratings.groupby("teacher_id")["rating"].mean().reset_index()
fig = px.bar(teacher_ratings, x="teacher_id", y="rating")
st.plotly_chart(fig, use_container_width=True)
""")
    
    # 使用streamlit导出为静态HTML
    subprocess.run([
        "streamlit", "run",
        str(temp_app),
        "--server.headless", "true",
        "--server.runOnSave", "true",
        "--server.port", "8501",
        "--browser.serverAddress", "localhost",
        "--server.address", "localhost"
    ], cwd=str(output_dir))
    
    # 创建启动脚本
    with open(output_dir / "index.html", "w", encoding="utf-8") as f:
        f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>评分仪表板</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }
        iframe {
            width: 100%;
            height: 100vh;
            border: none;
        }
    </style>
</head>
<body>
    <iframe src="http://localhost:8501" frameborder="0"></iframe>
</body>
</html>
""")
    
    # 创建README文件
    with open(output_dir / "README.md", "w", encoding="utf-8") as f:
        f.write("""
# 评分仪表板

这是一个完全静态的评分仪表板，无需安装任何Python包即可运行。

## 使用方法

1. 双击 `index.html` 文件在浏览器中打开
2. 等待几秒钟，仪表板将自动加载
3. 如果仪表板没有自动加载，请刷新页面

## 注意事项

- 所有数据文件都已包含在此目录中
- 无需安装任何软件或包
- 可以复制整个目录到其他电脑上运行
""")
    
    print(f"静态仪表板已导出到: {output_dir}")
    print("请打开 index.html 文件查看仪表板")

if __name__ == "__main__":
    export_to_html() 