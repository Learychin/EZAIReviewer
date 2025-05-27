import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import hashlib
import re

# 设置页面配置
st.set_page_config(
    page_title="课程评分分析看板",
    page_icon="📊",
    layout="wide"
)

def get_avatar_url(name):
    # 使用 Dicebear Micah 风格头像，基于姓名hash生成唯一头像
    seed = hashlib.md5(name.encode('utf-8')).hexdigest()
    return f"https://api.dicebear.com/7.x/micah/svg?seed={seed}"

# 加载评分元数据
with open('ratings_meta.json', 'r', encoding='utf-8') as f:
    ratings_meta = json.load(f)

# 加载数据
@st.cache_data
def load_data():
    with open('course_ratings_compact.json', 'r', encoding='utf-8') as f:
        ratings_compact = json.load(f)
    with open('teachers.json', 'r', encoding='utf-8') as f:
        teachers = json.load(f)
    return ratings_compact, teachers

ratings_compact, teachers_data = load_data()

# 将数据转换为DataFrame
# 解析评分细则索引为列

def flatten_ratings_compact(ratings):
    flattened_data = []
    for rating in ratings:
        base_data = {
            'session_id': rating['session_id'],
            'student_id': rating['student_id'],
            'teacher_id': rating['teacher_id'],
            'course_code': rating['course_code'],
            'schedule': rating['schedule'],
            'total_score': rating['ratings']['total_score'],
        }
        # 展开各维度分
        for cat, cat_info in rating['ratings']['ratings'].items():
            base_data[f'{cat}_score'] = cat_info['score']
            # 展开细则分
            for cidx, score in cat_info['criteria'].items():
                base_data[f'{cat}_{cidx}'] = score
        flattened_data.append(base_data)
    return pd.DataFrame(flattened_data)

df = flatten_ratings_compact(ratings_compact)

# 合并教师信息
teachers_df = pd.DataFrame(teachers_data)
df = df.merge(teachers_df[['Teacher ID', 'Expertise', 'Teacher Name']], 
              left_on='teacher_id', 
              right_on='Teacher ID', 
              how='left')
# 合并学生信息
students_df = pd.read_json('students.json')
df = df.merge(students_df[['Student ID', 'Student Name']],
              left_on='student_id',
              right_on='Student ID',
              how='left')
# 合并课程信息，添加Department字段（唯一业务分类）
courses_df = pd.read_json('courses.json')
df = df.merge(courses_df[['Course Code', 'Department']],
              left_on='course_code',
              right_on='Course Code',
              how='left')
df = df.rename(columns={'Department': 'Business Category'})

# 解析schedule为多列
schedule_df = pd.json_normalize(df['schedule'])
schedule_df.columns = [f'schedule_{col}' for col in schedule_df.columns]
df = pd.concat([df.drop(columns=['schedule']), schedule_df], axis=1)

# 页面标题
st.title("📊 课程评分分析看板")

# 创建筛选器
st.sidebar.header("🔍 筛选条件")

# 日期范围筛选
min_date = datetime.strptime(df['schedule_start_date'].min(), '%Y-%m-%d')
max_date = datetime.strptime(df['schedule_start_date'].max(), '%Y-%m-%d')

date_range = st.sidebar.date_input(
    "选择日期范围",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

filtered_df = df.copy()
if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['schedule_start_date'] >= date_range[0].strftime('%Y-%m-%d')) &
        (filtered_df['schedule_start_date'] <= date_range[1].strftime('%Y-%m-%d'))
    ]

# 教师业务分类筛选
available_categories = sorted(df['Business Category'].dropna().unique())
selected_category = st.sidebar.selectbox(
    "选择业务分类（课程所属学科）",
    options=["全部"] + available_categories,
    index=0
)
if selected_category != "全部":
    filtered_df = filtered_df[filtered_df['Business Category'] == selected_category]

# 课程代码筛选
available_courses = sorted(filtered_df['course_code'].unique())
selected_course = st.sidebar.selectbox(
    "选择课程",
    options=["全部"] + available_courses,
    index=0
)
if selected_course != "全部":
    filtered_df = filtered_df[filtered_df['course_code'] == selected_course]

# 教师筛选
available_teachers = sorted(filtered_df['Teacher Name'].unique())
selected_teacher = st.sidebar.selectbox(
    "选择教师",
    options=["全部"] + available_teachers,
    index=0
)
if selected_teacher != "全部":
    filtered_df = filtered_df[filtered_df['Teacher Name'] == selected_teacher]

# 学生筛选
students_df_for_filter = pd.read_json('students.json')
all_student_names = sorted(students_df_for_filter['Student Name'].unique())
selected_student = st.sidebar.selectbox(
    "选择学生",
    options=["全部"] + all_student_names,
    index=0
)
if selected_student != "全部":
    filtered_df = filtered_df[filtered_df['Student Name'] == selected_student]

# 分数范围筛选
if not filtered_df.empty:
    min_score = float(filtered_df['total_score'].min())
    max_score = float(filtered_df['total_score'].max())
    if min_score > max_score:
        min_score = max_score
else:
    min_score = 0.0
    max_score = 10.0
score_range = st.sidebar.slider(
    "选择总分范围",
    min_value=min_score,
    max_value=max_score,
    value=(min_score, max_score)  # 默认全范围
)
if not filtered_df.empty:
    filtered_df = filtered_df[
        (filtered_df['total_score'] >= score_range[0]) &
        (filtered_df['total_score'] <= score_range[1])
    ]

# 在所有筛选器之后，检查 filtered_df 是否为空
if filtered_df.empty:
    st.warning("⚠️ 没有找到符合筛选条件的数据。请调整筛选器。")
    st.stop() # 如果没有数据，停止执行后续代码

# 修改为更合理的分栏比例，统计数据更宽，老师卡片更紧凑
left_col, right_col = st.columns([5, 2], gap="medium")

with left_col:
    st.markdown('''
    <div style="display: flex; justify-content: center; align-items: flex-start; gap: 40px; margin-top: 8px; margin-bottom: 4px;">
        <div style="text-align:center; min-width:90px;">
            <div style="font-size:15px;color:#888;">总课程数</div>
            <div style="font-size:2.4rem;font-weight:700;line-height:1.1;">{}</div>
        </div>
        <div style="text-align:center; min-width:90px;">
            <div style="font-size:15px;color:#888;">平均总分</div>
            <div style="font-size:2.4rem;font-weight:700;line-height:1.1;">{:.1f}</div>
        </div>
        <div style="text-align:center; min-width:90px;">
            <div style="font-size:15px;color:#888;">最高分</div>
            <div style="font-size:2.4rem;font-weight:700;line-height:1.1;">{:.1f}</div>
        </div>
        <div style="text-align:center; min-width:90px;">
            <div style="font-size:15px;color:#888;">最低分</div>
            <div style="font-size:2.4rem;font-weight:700;line-height:1.1;">{:.1f}</div>
        </div>
    </div>
    '''.format(
        len(filtered_df),
        filtered_df['total_score'].mean(),
        filtered_df['total_score'].max(),
        filtered_df['total_score'].min()
    ), unsafe_allow_html=True)

with right_col:
    selected_teachers_info = (
        filtered_df.groupby('Teacher Name', as_index=False)
        .agg({'Business Category': lambda x: x.iloc[0] if isinstance(x.iloc[0], list) else x, 'teacher_id': 'first'})
        .head(5)
    )
    if not selected_teachers_info.empty:
        card_cols = st.columns(len(selected_teachers_info))
        for idx, (_, row) in enumerate(selected_teachers_info.iterrows()):
            with card_cols[idx]:
                btn = st.button(
                    label=f"\n\n{row['Teacher Name']}\n{row['Business Category'] if isinstance(row['Business Category'], str) else row['Business Category'][0]}",
                    key=f"teacher_card_{row['teacher_id']}",
                    help=row['Teacher Name'],
                )
                st.markdown(
                    f'<div style="background:#fff;border-radius:12px;box-shadow:0 1px 6px #ccc;padding:10px 8px;min-width:72px;max-width:90px;display:flex;flex-direction:column;align-items:center;margin:0 4px;cursor:pointer;">'
                    f'<img src="{get_avatar_url(row["Teacher Name"])}" style="width:40px;height:40px;border-radius:50%;margin-bottom:4px;">'
                    f'<div style="margin-top:2px;font-weight:bold;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:80px;">{row["Teacher Name"]}</div>'
                    f'<div style="margin-top:2px;font-size:12px;color:#666;">{row["Business Category"] if isinstance(row["Business Category"], str) else row["Business Category"][0]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                if btn:
                    st.session_state['selected_teacher_id'] = row['teacher_id']

# 教师详细信息弹出区
if 'selected_teacher_id' in st.session_state:
    teacher_id = st.session_state['selected_teacher_id']
    teacher_info = teachers_df[teachers_df['Teacher ID'] == teacher_id].iloc[0]
    teacher_name = teacher_info['Teacher Name']
    teacher_avatar = get_avatar_url(teacher_name)
    teacher_exp = ', '.join(teacher_info['Expertise']) if isinstance(teacher_info['Expertise'], list) else teacher_info['Expertise']
    teacher_courses = df[df['teacher_id'] == teacher_id]['course_code'].unique().tolist()
    total_sessions = len(df[df['teacher_id'] == teacher_id])
    avg_score = df[df['teacher_id'] == teacher_id]['total_score'].mean()
    # 维度分数
    radar_cats = [cat for cat in ratings_meta.keys()]
    radar_scores = [df[df['teacher_id'] == teacher_id][f'{cat}_score'].mean() for cat in radar_cats]
    radar_fig = go.Figure()
    radar_fig.add_trace(go.Scatterpolar(
        r=radar_scores + [radar_scores[0]],
        theta=radar_cats + [radar_cats[0]],
        fill='toself',
        name='教师维度分'
    ))
    radar_fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=False,
        height=350,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    with st.sidebar:
        st.markdown(f"### 👨‍🏫 教师详情")
        st.image(teacher_avatar, width=80)
        st.markdown(f"**姓名：**{teacher_name}")
        st.markdown(f"**业务分类：**{teacher_exp}")
        st.markdown(f"**总计课时：**{total_sessions}")
        st.markdown(f"**历史课程：**{'，'.join(teacher_courses)}")
        st.markdown(f"**综合评分：**{avg_score:.2f}")
        st.plotly_chart(radar_fig, use_container_width=True)

# 图表区Bento Box
chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    st.subheader("📈 评分维度对比")
    category_scores = filtered_df[[col for col in filtered_df.columns if col.endswith('_score')]]
    category_scores = category_scores.mean().reset_index()
    category_scores.columns = ['Category', 'Score']
    category_scores['Category'] = category_scores['Category'].str.replace('_score', '')
    y_min = category_scores['Score'].min()
    y_max = category_scores['Score'].max()
    y_margin = (y_max - y_min) * 0.15 if y_max > y_min else 1
    fig = px.bar(
        category_scores,
        x='Category',
        y='Score',
        title="各维度平均分对比",
        color='Category'
    )
    fig.update_layout(yaxis=dict(range=[y_min - y_margin, y_max + y_margin]))
    st.plotly_chart(fig, use_container_width=True)

with chart_col2:
    st.subheader("📊 总分分布")
    y_min = filtered_df['total_score'].min()
    y_max = filtered_df['total_score'].max()
    y_margin = (y_max - y_min) * 0.15 if y_max > y_min else 1
    unique_scores = sorted(filtered_df['total_score'].unique())
    nbins = max(len(unique_scores), 10)
    fig = px.histogram(
        filtered_df,
        x='total_score',
        nbins=nbins,
        title="课程总分分布",
        barmode='overlay',
        opacity=0.7
    )
    fig.update_layout(
        xaxis=dict(range=[min(unique_scores), max(unique_scores)]),
        yaxis=dict(range=[y_min - y_margin, y_max + y_margin]),
        bargap=0.08,
        height=420,
        margin=dict(l=20, r=20, t=50, b=30)
    )
    st.plotly_chart(fig, use_container_width=True)

# 数据表区Bento Box
st.subheader("📋 详细数据")
columns_to_show = [
    'session_id', 'Student Name', 'Teacher Name', 'course_code',
    'schedule_start_date', 'total_score', 'Business Category'
]
rating_columns = [col for col in df.columns if col.endswith('_score') and col not in columns_to_show]
columns_to_show.extend(rating_columns)
st.dataframe(
    df[columns_to_show],
    use_container_width=True
)
if st.button("导出全部数据"):
    csv = df[columns_to_show].to_csv(index=False)
    st.download_button(
        label="下载CSV文件",
        data=csv,
        file_name="course_ratings_all.csv",
        mime="text/csv"
    )

# 教师评分排名
st.subheader("👨‍🏫 教师评分排名")

# 计算教师评分（显示所有教师）
teacher_scores = filtered_df.groupby(['teacher_id', 'Teacher Name']).agg({
    'total_score': ['mean', 'count'],
    'Business Category': 'first'
}).reset_index()
teacher_scores.columns = ['教师ID', '教师姓名', '平均分', '课程数', '业务分类']
teacher_scores = teacher_scores.sort_values(['平均分'], ascending=[False])

# 只保留每个教师的第一个业务分类（避免重复显示）
teacher_scores['主业务分类'] = teacher_scores['业务分类'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else "未知")

unique_expertise = teacher_scores['主业务分类'].unique()
color_map = {exp: px.colors.qualitative.Set3[i % len(px.colors.qualitative.Set3)] for i, exp in enumerate(unique_expertise)}

min_y = teacher_scores['平均分'].min()
max_y = teacher_scores['平均分'].max()
y_margin = (max_y - min_y) * 0.15 if max_y > min_y else 1

fig = go.Figure()
for exp in unique_expertise:
    mask = teacher_scores['主业务分类'] == exp
    if mask.any():
        fig.add_trace(go.Bar(
            x=teacher_scores[mask]['教师姓名'],
            y=teacher_scores[mask]['平均分'],
            name=exp,
            marker_color=color_map[exp],
            text=teacher_scores[mask]['平均分'].round(1),
            textposition='outside'
        ))
fig.update_layout(
    title="教师评分排名（全部教师）",
    xaxis_title="教师姓名",
    yaxis_title="平均分",
    barmode='group',
    showlegend=True,
    yaxis=dict(range=[min_y - y_margin, max_y + y_margin])
)
st.plotly_chart(fig, use_container_width=True)

# 课程评分趋势
st.subheader("📅 评分趋势")
daily_scores = filtered_df.groupby(['schedule_start_date'])['total_score'].mean().reset_index()
y_min = daily_scores['total_score'].min()
y_max = daily_scores['total_score'].max()
y_margin = (y_max - y_min) * 0.15 if y_max > y_min else 1
fig = px.line(
    daily_scores,
    x='schedule_start_date',
    y='total_score',
    title="每日平均分趋势"
)
fig.update_layout(yaxis=dict(range=[y_min - y_margin, y_max + y_margin]))
st.plotly_chart(fig, use_container_width=True)

# =========================
# 商业分析可视化模块
# =========================

# 1. 教师相关分析
with st.container():
    st.markdown("## 👨‍🏫 教师相关分析")
    st.markdown("教师业务能力画像、评分分布、趋势等。")
    # 只用教师姓名分组，主业务分类用Business Category
    teacher_exp_scores = df.groupby('Teacher Name').agg({'total_score':'mean', 'Business Category':'first'}).reset_index()
    fig = px.box(
        teacher_exp_scores,
        x='Business Category',
        y='total_score',
        points='all',
        title="各业务分类下教师平均分分布",
        color='Business Category',
        height=380
    )
    st.plotly_chart(fig, use_container_width=True)
    # 教师评分趋势
    teacher_trend = df.groupby(['schedule_start_date', 'Teacher Name'])['total_score'].mean().reset_index()
    fig2 = px.line(
        teacher_trend,
        x='schedule_start_date',
        y='total_score',
        color='Teacher Name',
        title="教师评分随时间变化趋势",
        height=320
    )
    st.plotly_chart(fig2, use_container_width=True)

# 2. 课程与学科分析
with st.container():
    st.markdown("## 📚 课程与学科分析")
    st.markdown("课程满意度、受欢迎度、分布等。")
    # 课程满意度分布
    course_scores = df.groupby('course_code')['total_score'].mean().reset_index()
    fig3 = px.bar(
        course_scores,
        x='course_code',
        y='total_score',
        title="各课程平均满意度",
        color='total_score',
        color_continuous_scale='Blues',
        height=320
    )
    st.plotly_chart(fig3, use_container_width=True)
    # 课程受欢迎度（选课人数）
    course_pop = df.groupby('course_code')['student_id'].nunique().reset_index().rename(columns={'student_id':'选课人数'})
    fig4 = px.bar(
        course_pop,
        x='course_code',
        y='选课人数',
        title="各课程受欢迎度（选课人数）",
        color='选课人数',
        color_continuous_scale='Oranges',
        height=320
    )
    st.plotly_chart(fig4, use_container_width=True)
# ... 其余模块后续补充 ... 