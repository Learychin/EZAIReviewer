import json
import random
from datetime import datetime, timedelta
import pandas as pd

# 评分标准权重和细则索引
RATING_WEIGHTS = {
    "课程结构": 0.10,
    "课程内容完整度": 0.40,
    "授课逻辑": 0.20,
    "教学互动与反馈": 0.15,
    "教学语言表达": 0.15
}

RATING_CRITERIA = {
    "课程结构": [
        "开场活跃气氛，帮助学生进入上课状态",
        "开场确认声音设备，保证学生能听到声音、看到画面",
        "对之前内容进行回顾，对今日内容进行介绍，终场总结今日课程内容，预告下次课程安排",
        "超过2小时连续课程时间，中间设置5分钟休息时长"
    ],
    "课程内容完整度": [
        "教学方式为知识点紧接着搭配习题/知识点搭配概念填空",
        "所有题目必须标明或口播年份、出处/概念填空必须标明出处",
        "知识点有进行铺垫引入正题",
        "知识点有明确的定义/公式，辅助进行进行解释",
        "若能明确交代该知识点在考试中最可能会出现的形式",
        "讲解题目时有带着学生读题、审题确认考点，并强调踩分点",
        "几乎没有出现任何口误、笔误、课件Typo等问题"
    ],
    "授课逻辑": [
        "将与同一知识点相关的定义/公式、解释、推导、性质、举例、应用、对比、相关考题、总结等板块有充分的逻辑串联",
        "同一知识点的题目按由简单到复杂的顺序排列，不同知识点按由浅入深顺序排列",
        "不同知识点间，需要有语言提示，明确课程进度"
    ],
    "教学互动与反馈": [
        "对学生提出的有价值的具有普遍性的问题展开讲解",
        "授课具有引导性，通过设问等方式引导学生跟随导师逻辑思考",
        "通过必要的停顿给学生思考的时间",
        "导师有提问意识，时常关注学生状态"
    ],
    "教学语言表达": [
        "导师讲课声音够大、能听清楚；声音自信、富有活力、有明显起伏，语速保持适中",
        "无频繁网络卡顿，等造成的授课体验不佳情况",
        "口齿清楚，不吞字，不一语带过",
        "若语言幽默，学生互动性强则为加分项"
    ]
}

# 生成评分元数据表
criteria_meta = {}
for cat, criteria_list in RATING_CRITERIA.items():
    criteria_meta = {f"C{i+1}": desc for i, desc in enumerate(criteria_list)}
    criteria_meta['weight'] = RATING_WEIGHTS[cat]
    RATING_CRITERIA[cat] = list(criteria_meta.keys())[:-1]  # 只保留C1、C2...
    criteria_meta.pop('weight')
    criteria_meta['criteria_order'] = list(criteria_meta.keys())
    criteria_meta['category'] = cat
    criteria_meta['weight'] = RATING_WEIGHTS[cat]
    criteria_meta['criteria_desc'] = {k: v for k, v in criteria_meta.items() if k.startswith('C')}
    criteria_meta.pop('criteria_order')
    criteria_meta.pop('category')
    criteria_meta.pop('weight')
    criteria_meta.pop('criteria_desc')
criteria_meta_json = {
    cat: {
        'weight': RATING_WEIGHTS[cat],
        'criteria': {f"C{i+1}": desc for i, desc in enumerate(RATING_CRITERIA[cat])}
    }
    for cat, criteria_list in RATING_CRITERIA.items()
}
with open('ratings_meta.json', 'w', encoding='utf-8') as f:
    json.dump(criteria_meta_json, f, ensure_ascii=False, indent=4)

# 加载教师专业领域
with open('teachers.json', 'r', encoding='utf-8') as f:
    teachers_data = json.load(f)
teacher_expertise = {t['Teacher ID']: t['Expertise'] for t in teachers_data}

# 加载课程所属学科
with open('courses.json', 'r', encoding='utf-8') as f:
    courses_data = json.load(f)
course_department = {c['Course Code']: c['Department'] for c in courses_data}

def generate_rating_compact():
    """生成评分明细表（紧凑版，含完整课程时间信息）"""
    with open('tutoring_sessions.json', 'r', encoding='utf-8') as f:
        tutoring_sessions = json.load(f)
    course_ratings = []
    for idx, session in enumerate(tutoring_sessions):
        session_id = f"EZ{idx+1:06d}"
        ratings = {}
        total_score = 0
        for cat, criteria_keys in RATING_CRITERIA.items():
            cat_score = round(random.uniform(6.0, 9.5), 1)
            criteria_scores = {k: round(random.uniform(cat_score-0.5, cat_score+0.5), 1) for k in criteria_keys}
            ratings[cat] = {
                'score': cat_score,
                'criteria': criteria_scores
            }
            total_score += cat_score * RATING_WEIGHTS[cat]
        # schedule字段优先用原始数据的完整时间，否则随机生成
        if 'schedule' in session and all(k in session['schedule'] for k in ['start_date','start_time','end_time','duration_minutes']):
            schedule = session['schedule']
        else:
            schedule = generate_course_schedule()
        course_ratings.append({
            'session_id': session_id,
            'student_id': session['Student ID'],
            'teacher_id': session['Teacher ID'],
            'course_code': session['Course Code'],
            'schedule': schedule,
            'ratings': {
                'ratings': ratings,
                'total_score': round(total_score, 1)
            }
        })
    # 再生成500节课程评分，老师不跨专业领域
    students = list(set([s['student_id'] for s in course_ratings]))
    teachers = list(set([s['teacher_id'] for s in course_ratings]))
    for i in range(500):
        student_id = random.choice(students)
        teacher_id = random.choice(teachers)
        possible_courses = [c for c, d in course_department.items() if d in teacher_expertise[teacher_id]]
        if not possible_courses:
            continue
        course_code = random.choice(possible_courses)
        session_id = f"EZ{len(course_ratings)+1:06d}"
        ratings = {}
        total_score = 0
        for cat, criteria_keys in RATING_CRITERIA.items():
            cat_score = round(random.uniform(6.0, 9.5), 1)
            criteria_scores = {k: round(random.uniform(cat_score-0.5, cat_score+0.5), 1) for k in criteria_keys}
            ratings[cat] = {
                'score': cat_score,
                'criteria': criteria_scores
            }
            total_score += cat_score * RATING_WEIGHTS[cat]
        schedule = generate_course_schedule()
        course_ratings.append({
            'session_id': session_id,
            'student_id': student_id,
            'teacher_id': teacher_id,
            'course_code': course_code,
            'schedule': schedule,
            'ratings': {
                'ratings': ratings,
                'total_score': round(total_score, 1)
            }
        })
    with open('course_ratings_compact.json', 'w', encoding='utf-8') as f:
        json.dump(course_ratings, f, ensure_ascii=False, indent=4)
    print(f"已生成紧凑评分明细表，共{len(course_ratings)}条")

def generate_rating(category):
    """生成某个类别的评分，80%的概率生成高于平均分的分数，但整体分数降低到原来的50%左右"""
    if random.random() < 0.8:  # 80%的概率生成高于平均分的分数
        return round(random.uniform(3.75, 5.0), 1)  # 原来是7.5-10.0
    else:
        return round(random.uniform(2.5, 3.7), 1)  # 原来是5.0-7.4

def generate_course_schedule():
    """生成课程时间表"""
    # 生成一个随机的开始日期（2024年）
    start_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 180))
    
    # 课程时长（90-180分钟）
    duration = random.randint(90, 180)
    
    # 生成开始时间（8:00-20:00之间）
    start_hour = random.randint(8, 20)
    start_minute = random.choice([0, 15, 30, 45])
    start_time = datetime.combine(start_date.date(), datetime.min.time().replace(hour=start_hour, minute=start_minute))
    
    # 计算结束时间
    end_time = start_time + timedelta(minutes=duration)
    
    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "start_time": start_time.strftime("%H:%M"),
        "end_time": end_time.strftime("%H:%M"),
        "duration_minutes": duration
    }

def generate_course_ratings():
    """生成课程评分"""
    ratings = {}
    for category, weight in RATING_WEIGHTS.items():
        category_score = generate_rating(category)
        criteria_scores = {
            criterion: round(random.uniform(category_score - 0.5, category_score + 0.5), 1)
            for criterion in RATING_CRITERIA[category]
        }
        ratings[category] = {
            "weight": weight,
            "score": category_score,
            "criteria": criteria_scores
        }
    
    # 计算总分
    total_score = sum(rating["score"] * rating["weight"] for rating in ratings.values())
    
    return {
        "ratings": ratings,
        "total_score": round(total_score, 1)
    }

def generate_low_score_ratings_from_high():
    """以高分组为基准，生成低分组数据，老师不跨学科，学生可随机分配，分数整体下调"""
    # 读取高分组数据
    with open('course_ratings.json', 'r', encoding='utf-8') as f:
        high_ratings = json.load(f)
    # 读取学生列表
    with open('students.json', 'r', encoding='utf-8') as f:
        students = json.load(f)
    student_ids = [s['Student ID'] for s in students]

    low_ratings = []
    for i, high in enumerate(high_ratings):
        # 保持老师、课程、学科不变，学生可随机分配
        student_id = random.choice(student_ids)
        teacher_id = high['teacher_id']
        course_code = high['course_code']
        schedule = high['schedule']
        # 生成低分评分（3~6分区间，细则分数也下调）
        ratings = {}
        for category, cat_info in high['ratings']['ratings'].items():
            weight = cat_info['weight']
            # 低分主分数
            category_score = round(random.uniform(3.0, 6.0), 1)
            # 细则分数在主分数±0.5区间
            criteria_scores = {
                criterion: max(1.0, min(6.0, round(random.uniform(category_score-0.5, category_score+0.5), 1)))
                for criterion in cat_info['criteria']
            }
            ratings[category] = {
                'weight': weight,
                'score': category_score,
                'criteria': criteria_scores
            }
        total_score = sum(r['score'] * r['weight'] for r in ratings.values())
        low_ratings.append({
            'session_id': f"LS{i+1:06d}",
            'student_id': student_id,
            'teacher_id': teacher_id,
            'course_code': course_code,
            'schedule': schedule,
            'ratings': {
                'ratings': ratings,
                'total_score': round(total_score, 1)
            }
        })
    with open('course_ratings_low.json', 'w', encoding='utf-8') as f:
        json.dump(low_ratings, f, ensure_ascii=False, indent=4)
    print(f"已生成低分组数据，共{len(low_ratings)}条")

if __name__ == "__main__":
    generate_rating_compact()
    generate_low_score_ratings_from_high() 