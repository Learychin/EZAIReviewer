import os
import shutil
from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import hashlib

def get_avatar_url(name):
    seed = hashlib.md5(name.encode('utf-8')).hexdigest()
    return f"https://api.dicebear.com/7.x/micah/svg?seed={seed}"

def build_static():
    # 获取当前目录
    current_dir = Path(__file__).parent
    
    # 创建输出目录
    output_dir = current_dir / "static_export"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()
    
    # 复制所有数据文件
    data_files = [
        "course_ratings_compact.json",
        "ratings_meta.json",
        "students.json",
        "teachers.json",
        "courses.json"
    ]
    
    for file in data_files:
        if (current_dir / file).exists():
            shutil.copy2(current_dir / file, output_dir / file)
    
    # 加载数据
    with open(current_dir / 'ratings_meta.json', 'r', encoding='utf-8') as f:
        ratings_meta = json.load(f)
    
    with open(current_dir / 'course_ratings_compact.json', 'r', encoding='utf-8') as f:
        ratings_compact = json.load(f)
    
    with open(current_dir / 'teachers.json', 'r', encoding='utf-8') as f:
        teachers_data = json.load(f)
    
    with open(current_dir / 'students.json', 'r', encoding='utf-8') as f:
        students_data = json.load(f)
    
    with open(current_dir / 'courses.json', 'r', encoding='utf-8') as f:
        courses_data = json.load(f)
    
    # 将数据转换为DataFrame
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
            for cat, cat_info in rating['ratings']['ratings'].items():
                base_data[f'{cat}_score'] = cat_info['score']
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
    students_df = pd.DataFrame(students_data)
    df = df.merge(students_df[['Student ID', 'Student Name']],
                  left_on='student_id',
                  right_on='Student ID',
                  how='left')
    
    # 合并课程信息
    courses_df = pd.DataFrame(courses_data)
    df = df.merge(courses_df[['Course Code', 'Department']],
                  left_on='course_code',
                  right_on='Course Code',
                  how='left')
    df = df.rename(columns={'Department': 'Business Category'})
    
    # 解析schedule为多列
    schedule_df = pd.json_normalize(df['schedule'])
    schedule_df.columns = [f'schedule_{col}' for col in schedule_df.columns]
    df = pd.concat([df.drop(columns=['schedule']), schedule_df], axis=1)
    
    # 创建HTML文件
    with open(output_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <title>课程评分分析看板</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ padding: 20px; }}
        .chart {{ margin-bottom: 30px; }}
        .teacher-card {{
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 1px 6px #ccc;
            padding: 10px 8px;
            min-width: 72px;
            max-width: 90px;
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 0 4px;
            cursor: pointer;
        }}
        .teacher-avatar {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-bottom: 4px;
        }}
        .teacher-name {{
            margin-top: 2px;
            font-weight: bold;
            font-size: 13px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 80px;
        }}
        .teacher-category {{
            margin-top: 2px;
            font-size: 12px;
            color: #666;
        }}
        .filter-section {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .stats-card {{
            text-align: center;
            min-width: 90px;
        }}
        .stats-value {{
            font-size: 2.4rem;
            font-weight: 700;
            line-height: 1.1;
        }}
        .stats-label {{
            font-size: 15px;
            color: #888;
        }}
        .sidebar {{
            position: fixed;
            top: 0;
            left: 0;
            bottom: 0;
            width: 300px;
            background: #fff;
            padding: 20px;
            box-shadow: 2px 0 5px rgba(0,0,0,0.1);
            z-index: 1000;
            overflow-y: auto;
        }}
        .main-content {{
            margin-left: 320px;
        }}
    </style>
</head>
<body>
    <!-- 侧边栏 -->
    <div class="sidebar">
        <h4>🔍 筛选条件</h4>
        
        <!-- 日期范围筛选 -->
        <div class="mb-3">
            <label class="form-label">选择日期范围</label>
            <input type="date" class="form-control" id="start-date" value="{df['schedule_start_date'].min()}">
            <input type="date" class="form-control mt-2" id="end-date" value="{df['schedule_start_date'].max()}">
        </div>
        
        <!-- 业务分类筛选 -->
        <div class="mb-3">
            <label class="form-label">选择业务分类（课程所属学科）</label>
            <select class="form-select" id="category-filter">
                <option value="">全部</option>
                {''.join(f'<option value="{cat}">{cat}</option>' for cat in sorted(df['Business Category'].dropna().unique()))}
            </select>
        </div>
        
        <!-- 课程筛选 -->
        <div class="mb-3">
            <label class="form-label">选择课程</label>
            <select class="form-select" id="course-filter">
                <option value="">全部</option>
                {''.join(f'<option value="{code}">{code}</option>' for code in sorted(df['course_code'].unique()))}
            </select>
        </div>
        
        <!-- 教师筛选 -->
        <div class="mb-3">
            <label class="form-label">选择教师</label>
            <select class="form-select" id="teacher-filter">
                <option value="">全部</option>
                {''.join(f'<option value="{name}">{name}</option>' for name in sorted(df['Teacher Name'].unique()))}
            </select>
        </div>
        
        <!-- 学生筛选 -->
        <div class="mb-3">
            <label class="form-label">选择学生</label>
            <select class="form-select" id="student-filter">
                <option value="">全部</option>
                {''.join(f'<option value="{name}">{name}</option>' for name in sorted(df['Student Name'].unique()))}
            </select>
        </div>
        
        <!-- 分数范围筛选 -->
        <div class="mb-3">
            <label class="form-label">选择总分范围</label>
            <input type="range" class="form-range" id="score-range" 
                   min="{df['total_score'].min()}" 
                   max="{df['total_score'].max()}" 
                   step="0.1"
                   value="{df['total_score'].min()}">
            <div class="d-flex justify-content-between">
                <span id="min-score-display">{df['total_score'].min():.1f}</span>
                <span id="max-score-display">{df['total_score'].max():.1f}</span>
            </div>
        </div>
    </div>

    <!-- 主要内容 -->
    <div class="main-content">
        <h1 class="mb-4">📊 课程评分分析看板</h1>
        
        <!-- 统计信息 -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="stats-card">
                    <div class="stats-label">总课程数</div>
                    <div class="stats-value" id="total-courses">{len(df)}</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stats-card">
                    <div class="stats-label">平均总分</div>
                    <div class="stats-value" id="avg-score">{df['total_score'].mean():.1f}</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stats-card">
                    <div class="stats-label">最高分</div>
                    <div class="stats-value" id="max-score">{df['total_score'].max():.1f}</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stats-card">
                    <div class="stats-label">最低分</div>
                    <div class="stats-value" id="min-score">{df['total_score'].min():.1f}</div>
                </div>
            </div>
        </div>

        <!-- 教师卡片 -->
        <div class="row mb-4">
            <div class="col-12">
                <h5>教师概览</h5>
                <div id="teacher-cards" class="d-flex flex-wrap"></div>
            </div>
        </div>

        <!-- 图表部分 -->
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">评分分布</h5>
                        <div id="rating-distribution" class="chart"></div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">课程评分</h5>
                        <div id="course-ratings" class="chart"></div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">教师评分雷达图</h5>
                        <div id="teacher-radar" class="chart"></div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">评分维度分析</h5>
                        <div id="rating-dimensions" class="chart"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // 加载数据
        async function loadData() {{
            const [ratings, meta, students, teachers, courses] = await Promise.all([
                fetch('course_ratings_compact.json').then(r => r.json()),
                fetch('ratings_meta.json').then(r => r.json()),
                fetch('students.json').then(r => r.json()),
                fetch('teachers.json').then(r => r.json()),
                fetch('courses.json').then(r => r.json())
            ]);

            // 应用筛选条件
            const filteredRatings = applyFilters(ratings);
            
            // 更新统计信息
            updateStats(filteredRatings);
            
            // 更新教师卡片
            updateTeacherCards(filteredRatings, teachers);
            
            // 绘制图表
            drawCharts(filteredRatings, meta);
        }}

        function applyFilters(ratings) {{
            const startDate = document.getElementById('start-date').value;
            const endDate = document.getElementById('end-date').value;
            const category = document.getElementById('category-filter').value;
            const course = document.getElementById('course-filter').value;
            const teacher = document.getElementById('teacher-filter').value;
            const student = document.getElementById('student-filter').value;
            const minScore = parseFloat(document.getElementById('score-range').value);

            return ratings.filter(rating => {{
                // 日期筛选
                if (startDate && rating.schedule.start_date < startDate) return false;
                if (endDate && rating.schedule.start_date > endDate) return false;
                
                // 业务分类筛选
                if (category && rating.business_category !== category) return false;
                
                // 课程筛选
                if (course && rating.course_code !== course) return false;
                
                // 教师筛选
                if (teacher && rating.teacher_name !== teacher) return false;
                
                // 学生筛选
                if (student && rating.student_name !== student) return false;
                
                // 分数筛选
                if (rating.ratings.total_score < minScore) return false;
                
                return true;
            }});
        }}

        function updateStats(ratings) {{
            const totalScore = ratings.reduce((sum, r) => sum + r.ratings.total_score, 0);
            const avgScore = totalScore / ratings.length;
            const maxScore = Math.max(...ratings.map(r => r.ratings.total_score));
            const minScore = Math.min(...ratings.map(r => r.ratings.total_score));

            document.getElementById('total-courses').textContent = ratings.length;
            document.getElementById('avg-score').textContent = avgScore.toFixed(1);
            document.getElementById('max-score').textContent = maxScore.toFixed(1);
            document.getElementById('min-score').textContent = minScore.toFixed(1);
        }}

        function updateTeacherCards(ratings, teachers) {{
            // 获取筛选后的教师评分
            const teacherScores = {{}};
            ratings.forEach(r => {{
                if (!teacherScores[r.teacher_id]) {{
                    teacherScores[r.teacher_id] = {{
                        total: 0,
                        count: 0,
                        name: r.teacher_name,
                        category: r.business_category
                    }};
                }}
                teacherScores[r.teacher_id].total += r.ratings.total_score;
                teacherScores[r.teacher_id].count += 1;
            }});

            // 计算平均分并排序
            const teacherList = Object.entries(teacherScores)
                .map(([id, data]) => ({{
                    id,
                    name: data.name,
                    category: data.category,
                    avgScore: data.total / data.count
                }}))
                .sort((a, b) => b.avgScore - a.avgScore)
                .slice(0, 5);

            // 更新教师卡片
            const cardsContainer = document.getElementById('teacher-cards');
            cardsContainer.innerHTML = teacherList.map(teacher => `
                <div class="teacher-card" onclick="showTeacherDetails('${teacher.id}')">
                    <img src="https://api.dicebear.com/7.x/micah/svg?seed=${teacher.name}" 
                         class="teacher-avatar" alt="${teacher.name}">
                    <div class="teacher-name">${teacher.name}</div>
                    <div class="teacher-category">${teacher.category}</div>
                </div>
            `).join('');
        }}

        function drawCharts(ratings, meta) {{
            // 绘制评分分布图
            const ratingCounts = {{}};
            ratings.forEach(r => {{
                const score = r.ratings.total_score;
                ratingCounts[score] = (ratingCounts[score] || 0) + 1;
            }});

            Plotly.newPlot('rating-distribution', [{{
                x: Object.keys(ratingCounts),
                y: Object.values(ratingCounts),
                type: 'bar'
            }}], {{
                title: '评分分布',
                xaxis: {{ title: '评分' }},
                yaxis: {{ title: '数量' }}
            }});

            // 绘制课程评分图
            const courseRatings = {{}};
            ratings.forEach(r => {{
                if (!courseRatings[r.course_code]) {{
                    courseRatings[r.course_code] = [];
                }}
                courseRatings[r.course_code].push(r.ratings.total_score);
            }});

            const courseData = Object.entries(courseRatings).map(([courseCode, scores]) => ({{
                y: scores,
                type: 'box',
                name: courseCode
            }}));

            Plotly.newPlot('course-ratings', courseData, {{
                title: '课程评分分布',
                xaxis: {{ title: '课程代码' }},
                yaxis: {{ title: '评分' }}
            }});

            // 绘制教师评分雷达图
            const teacherRatings = {{}};
            ratings.forEach(r => {{
                if (!teacherRatings[r.teacher_id]) {{
                    teacherRatings[r.teacher_id] = {{}};
                    Object.keys(meta).forEach(cat => {{
                        teacherRatings[r.teacher_id][cat] = [];
                    }});
                }}
                Object.entries(r.ratings.ratings).forEach(([cat, info]) => {{
                    teacherRatings[r.teacher_id][cat].push(info.score);
                }});
            }});

            const teacherId = Object.keys(teacherRatings)[0];
            const categories = Object.keys(meta);
            const scores = categories.map(cat => 
                teacherRatings[teacherId][cat].reduce((a, b) => a + b, 0) / 
                teacherRatings[teacherId][cat].length
            );

            Plotly.newPlot('teacher-radar', [{{
                r: scores,
                theta: categories,
                type: 'scatterpolar',
                fill: 'toself'
            }}], {{
                polar: {{
                    radialaxis: {{
                        visible: true,
                        range: [0, 10]
                    }}
                }}
            }});

            // 绘制评分维度分析图
            const dimensionScores = {{}};
            categories.forEach(cat => {{
                dimensionScores[cat] = ratings.reduce((sum, r) => 
                    sum + r.ratings.ratings[cat].score, 0) / ratings.length;
            }});

            Plotly.newPlot('rating-dimensions', [{{
                x: categories,
                y: Object.values(dimensionScores),
                type: 'bar'
            }}], {{
                title: '各维度平均分',
                xaxis: {{ title: '评分维度' }},
                yaxis: {{ title: '平均分' }}
            }});
        }}

        // 页面加载完成后加载数据
        window.onload = loadData;

        // 筛选器事件处理
        document.getElementById('category-filter').addEventListener('change', updateFilters);
        document.getElementById('course-filter').addEventListener('change', updateFilters);
        document.getElementById('teacher-filter').addEventListener('change', updateFilters);
        document.getElementById('student-filter').addEventListener('change', updateFilters);
        document.getElementById('score-range').addEventListener('input', function(e) {{
            document.getElementById('min-score-display').textContent = e.target.value;
            updateFilters();
        }});
        document.getElementById('start-date').addEventListener('change', updateFilters);
        document.getElementById('end-date').addEventListener('change', updateFilters);

        function updateFilters() {{
            // 重新加载数据并更新图表
            loadData();
        }}

        function showTeacherDetails(teacherId) {{
            // 显示教师详细信息
            console.log('Showing details for teacher:', teacherId);
            // TODO: 实现教师详情弹窗
        }}
    </script>
</body>
</html>
""")
    
    print(f"静态仪表板已导出到: {output_dir}")
    print("请打开 index.html 文件查看仪表板")

if __name__ == "__main__":
    build_static() 