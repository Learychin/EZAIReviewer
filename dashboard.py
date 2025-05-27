import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go

# 设置页面配置
st.set_page_config(
    page_title="教育数据分析看板",
    page_icon="📚",
    layout="wide"
)

# 加载数据
@st.cache_data
def load_data():
    with open('courses.json', 'r', encoding='utf-8') as f:
        courses = json.load(f)
    with open('students.json', 'r', encoding='utf-8') as f:
        students = json.load(f)
    with open('teachers.json', 'r', encoding='utf-8') as f:
        teachers = json.load(f)
    with open('course_enrollment.json', 'r', encoding='utf-8') as f:
        enrollment = json.load(f)
    return courses, students, teachers, enrollment

# 加载数据
courses, students, teachers, enrollment = load_data()

# 转换为DataFrame
courses_df = pd.DataFrame(courses)
students_df = pd.DataFrame(students)
teachers_df = pd.DataFrame(teachers)
enrollment_df = pd.DataFrame(list(enrollment.items()), columns=['Course Code', 'Enrollment'])

# 页面标题
st.title("📚 教育数据分析看板")

# 创建三列布局
col1, col2, col3 = st.columns(3)

# 第一列：基本统计信息
with col1:
    st.subheader("📊 基本统计")
    st.metric("总课程数", len(courses))
    st.metric("总学生数", len(students))
    st.metric("总教师数", len(teachers))

# 第二列：课程难度分布
with col2:
    st.subheader("📈 课程难度分布")
    difficulty_counts = courses_df['Difficulty'].value_counts()
    fig_difficulty = px.pie(
        values=difficulty_counts.values,
        names=difficulty_counts.index,
        title="课程难度分布"
    )
    st.plotly_chart(fig_difficulty, use_container_width=True)

# 第三列：院系分布
with col3:
    st.subheader("🏫 院系分布")
    dept_counts = courses_df['Department'].value_counts()
    fig_dept = px.bar(
        x=dept_counts.index,
        y=dept_counts.values,
        title="各院系课程数量"
    )
    fig_dept.update_layout(xaxis_title="院系", yaxis_title="课程数量")
    st.plotly_chart(fig_dept, use_container_width=True)

# 创建两列布局用于详细分析
col4, col5 = st.columns(2)

# 第四列：课程选修人数分布
with col4:
    st.subheader("👥 课程选修人数分布")
    fig_enrollment = px.histogram(
        enrollment_df,
        x='Enrollment',
        title="课程选修人数分布",
        nbins=20
    )
    fig_enrollment.update_layout(xaxis_title="选修人数", yaxis_title="课程数量")
    st.plotly_chart(fig_enrollment, use_container_width=True)

# 第五列：学生选课数量分布
with col5:
    st.subheader("📚 学生选课数量分布")
    student_course_counts = [len(student['Courses']) for student in students]
    fig_student = px.histogram(
        x=student_course_counts,
        title="学生选课数量分布",
        nbins=5
    )
    fig_student.update_layout(xaxis_title="选课数量", yaxis_title="学生数量")
    st.plotly_chart(fig_student, use_container_width=True)

# 添加详细数据表格
st.subheader("📋 课程详细信息")
st.dataframe(
    courses_df[['Course Code', 'Course Title', 'Department', 'Level', 'Difficulty']],
    use_container_width=True
)

# 添加交互式筛选器
st.subheader("🔍 课程筛选")
selected_department = st.selectbox(
    "选择院系",
    options=['全部'] + sorted(courses_df['Department'].unique().tolist())
)

selected_level = st.selectbox(
    "选择课程级别",
    options=['全部'] + sorted(courses_df['Level'].unique().tolist())
)

# 根据筛选条件过滤数据
filtered_courses = courses_df.copy()
if selected_department != '全部':
    filtered_courses = filtered_courses[filtered_courses['Department'] == selected_department]
if selected_level != '全部':
    filtered_courses = filtered_courses[filtered_courses['Level'] == selected_level]

# 显示筛选后的数据
st.dataframe(
    filtered_courses[['Course Code', 'Course Title', 'Department', 'Level', 'Difficulty']],
    use_container_width=True
) 