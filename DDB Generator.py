import random
import pandas as pd
import json

# 1. 定义课程列表 (至少 60 门)
courses_data = [
    {'Course Code': 'CS101', 'Course Title': '计算机科学导论', 'Description': '介绍计算机科学基本概念、编程基础和问题解决。', 'Level': '本科一年级', 'Department': '计算机科学', 'Difficulty': '入门'},
    {'Course Code': 'MATH151', 'Course Title': '微积分 I', 'Description': '单变量微积分入门，极限、导数、积分及其应用。', 'Level': '本科一年级', 'Department': '数学', 'Difficulty': '入门'},
    {'Course Code': 'ENG110', 'Course Title': '大学写作', 'Description': '培养学术写作能力，包括论文结构、论证和引用。', 'Level': '本科一年级', 'Department': '英语', 'Difficulty': '入门'},
    {'Course Code': 'HIST105', 'Course Title': '世界文明史', 'Description': '探讨人类文明的起源、发展和演变。', 'Level': '本科一年级', 'Department': '历史', 'Difficulty': '入门'},
    {'Course Code': 'PHYS201', 'Course Title': '普通物理学 I', 'Description': '力学、热学和振动与波的基础介绍。', 'Level': '本科二年级', 'Department': '物理学', 'Difficulty': '中级'},
    {'Course Code': 'ECON201', 'Course Title': '微观经济学原理', 'Description': '个体和企业的经济行为分析。', 'Level': '本科二年级', 'Department': '经济学', 'Difficulty': '中级'},
    {'Course Code': 'CS202', 'Course Title': '数据结构与算法', 'Description': '常用数据结构及其算法分析。', 'Level': '本科二年级', 'Department': '计算机科学', 'Difficulty': '中级'},
    {'Course Code': 'SOCY210', 'Course Title': '社会学导论', 'Description': '社会学的基本理论、概念和研究方法。', 'Level': '本科二年级', 'Department': '社会学', 'Difficulty': '中级'},
    {'Course Code': 'BIOL301', 'Course Title': '遗传学', 'Description': '遗传物质的结构、功能、变异和遗传规律。', 'Level': '本科三年级', 'Department': '生物学', 'Difficulty': '高级'},
    {'Course Code': 'CHEM320', 'Course Title': '有机化学 I', 'Description': '有机化合物的结构、性质、反应和合成。', 'Level': '本科三年级', 'Department': '化学', 'Difficulty': '高级'},
    {'Course Code': 'CS350', 'Course Title': '操作系统', 'Description': '操作系统的原理、设计和实现。', 'Level': '本科三年级', 'Department': '计算机科学', 'Difficulty': '高级'},
    {'Course Code': 'PSYC315', 'Course Title': '认知心理学', 'Description': '人类思维过程的研究，包括感知、记忆、语言和问题解决。', 'Level': '本科三年级', 'Department': '心理学', 'Difficulty': '高级'},
    {'Course Code': 'ENG401', 'Course Title': '莎士比亚', 'Description': '莎士比亚戏剧和诗歌的深入研究。', 'Level': '本科四年级', 'Department': '英语', 'Difficulty': '高级'},
    {'Course Code': 'MATH410', 'Course Title': '抽象代数', 'Description': '群、环、域等抽象代数结构及其性质。', 'Level': '本科四年级', 'Department': '数学', 'Difficulty': '高级'},
    {'Course Code': 'GRAD501', 'Course Title': '高级计算机视觉', 'Description': '计算机视觉领域的前沿理论和技术。', 'Level': '研究生', 'Department': '计算机科学', 'Difficulty': '高级'},
    {'Course Code': 'GRAD620', 'Course Title': '量子场论', 'Description': '粒子物理理论的基础。', 'Level': '研究生', 'Department': '物理学', 'Difficulty': '高级'},
    {'Course Code': 'MATH152', 'Course Title': '微积分 II', 'Description': '单变量微积分的进阶内容。', 'Level': '本科一年级', 'Department': '数学', 'Difficulty': '入门'},
    {'Course Code': 'PHYS202', 'Course Title': '普通物理学 II', 'Description': '电磁学、光学的基础介绍。', 'Level': '本科二年级', 'Department': '物理学', 'Difficulty': '中级'},
    {'Course Code': 'ECON202', 'Course Title': '宏观经济学原理', 'Description': '经济总量的运行规律分析。', 'Level': '本科二年级', 'Department': '经济学', 'Difficulty': '中级'},
    {'Course Code': 'CS250', 'Course Title': '离散数学', 'Description': '计算机科学中的数学基础。', 'Level': '本科二年级', 'Department': '计算机科学', 'Difficulty': '中级'},
    {'Course Code': 'BIOL101', 'Course Title': '生物学导论', 'Description': '生命科学的基本原理。', 'Level': '本科一年级', 'Department': '生物学', 'Difficulty': '入门'},
    {'Course Code': 'CHEM101', 'Course Title': '普通化学 I', 'Description': '化学的基本概念和原理。', 'Level': '本科一年级', 'Department': '化学', 'Difficulty': '入门'},
    {'Course Code': 'PHIL101', 'Course Title': '哲学导论', 'Description': '哲学的主要领域和基本问题。', 'Level': '本科一年级', 'Department': '哲学', 'Difficulty': '入门'},
    {'Course Code': 'POLS101', 'Course Title': '政治学导论', 'Description': '政治学的基本概念和理论。', 'Level': '本科一年级', 'Department': '政治学', 'Difficulty': '入门'},
    {'Course Code': 'ART101', 'Course Title': '艺术史导论', 'Description': '西方艺术史的概览。', 'Level': '本科一年级', 'Department': '艺术', 'Difficulty': '入门'},
    {'Course Code': 'MUS101', 'Course Title': '音乐史导论', 'Description': '西方音乐史的概览。', 'Level': '本科一年级', 'Department': '音乐', 'Difficulty': '入门'},
    {'Course Code': 'CS305', 'Course Title': '数据库系统', 'Description': '数据库的设计、实现和应用。', 'Level': '本科三年级', 'Department': '计算机科学', 'Difficulty': '高级'},
    {'Course Code': 'MATH320', 'Course Title': '概率论与数理统计', 'Description': '概率论的基本概念和统计推断方法。', 'Level': '本科三年级', 'Department': '数学', 'Difficulty': '高级'},
    {'Course Code': 'ENG320', 'Course Title': '美国文学', 'Description': '美国文学的主要时期和代表作家。', 'Level': '本科三年级', 'Department': '英语', 'Difficulty': '高级'},
    {'Course Code': 'HIST310', 'Course Title': '美国史', 'Description': '美国的历史发展和重要事件。', 'Level': '本科三年级', 'Department': '历史', 'Difficulty': '高级'},
    {'Course Code': 'PHYS310', 'Course Title': '电动力学', 'Description': '电场、磁场及其相互作用的理论。', 'Level': '本科三年级', 'Department': '物理学', 'Difficulty': '高级'},
    {'Course Code': 'ECON305', 'Course Title': '计量经济学', 'Description': '经济数据的统计分析方法。', 'Level': '本科三年级', 'Department': '经济学', 'Difficulty': '高级'},
    {'Course Code': 'SOCY320', 'Course Title': '社会研究方法', 'Description': '社会学研究的设计和实施。', 'Level': '本科三年级', 'Department': '社会学', 'Difficulty': '高级'},
    {'Course Code': 'BIOL410', 'Course Title': '分子生物学', 'Description': '细胞和分子水平的生命过程研究。', 'Level': '本科四年级', 'Department': '生物学', 'Difficulty': '高级'},
    {'Course Code': 'CHEM430', 'Course Title': '物理化学', 'Description': '化学原理在物理系统中的应用。', 'Level': '本科四年级', 'Department': '化学', 'Difficulty': '高级'},
    {'Course Code': 'PHIL305', 'Course Title': '伦理学', 'Description': '道德原则和伦理理论的研究。', 'Level': '本科三年级', 'Department': '哲学', 'Difficulty': '高级'},
    {'Course Code': 'POLS310', 'Course Title': '比较政治学', 'Description': '不同政治制度和过程的比较分析。', 'Level': '本科三年级', 'Department': '政治学', 'Difficulty': '高级'},
    {'Course Code': 'ART301', 'Course Title': '现代艺术', 'Description': '19世纪以来的西方艺术发展。', 'Level': '本科三年级', 'Department': '艺术', 'Difficulty': '高级'},
    {'Course Code': 'MUS301', 'Course Title': '和声学', 'Description': '西方音乐的和声理论与实践。', 'Level': '本科三年级', 'Department': '音乐', 'Difficulty': '高级'},
    {'Course Code': 'CS480', 'Course Title': '人工智能', 'Description': '智能系统的设计和开发。', 'Level': '本科四年级', 'Department': '计算机科学', 'Difficulty': '高级'},
    {'Course Code': 'MATH450', 'Course Title': '数值分析', 'Description': '求解数学问题的数值方法。', 'Level': '本科四年级', 'Department': '数学', 'Difficulty': '高级'},
    {'Course Code': 'ENG450', 'Course Title': '文学理论', 'Description': '文学批评和理论的主要流派。', 'Level': '本科四年级', 'Department': '英语', 'Difficulty': '高级'},
    {'Course Code': 'HIST420', 'Course Title': '近现代中国史', 'Description': '中国近现代历史的发展和变革。', 'Level': '本科四年级', 'Department': '历史', 'Difficulty': '高级'},
    {'Course Code': 'PHYS420', 'Course Title': '统计力学', 'Description': '从微观粒子行为理解宏观物理现象。', 'Level': '本科四年级', 'Department': '物理学', 'Difficulty': '高级'},
    {'Course Code': 'ECON410', 'Course Title': '国际贸易', 'Description': '国家间的货物和服务交换分析。', 'Level': '本科四年级', 'Department': '经济学', 'Difficulty': '高级'},
    {'Course Code': 'SOCY410', 'Course Title': '人口学', 'Description': '人口规模、结构、分布及其变化的研究。', 'Level': '本科四年级', 'Department': '社会学', 'Difficulty': '高级'},
    {'Course Code': 'BIOL510', 'Course Title': '生态学', 'Description': '生物及其环境之间的相互作用研究。', 'Level': '研究生', 'Department': '生物学', 'Difficulty': '高级'},
    {'Course Code': 'CHEM520', 'Course Title': '高级有机化学', 'Description': '有机化学的深入研究。', 'Level': '研究生', 'Department': '化学', 'Difficulty': '高级'},
    {'Course Code': 'PHIL501', 'Course Title': '形而上学', 'Description': '存在、实在和基本范畴的研究。', 'Level': '研究生', 'Department': '哲学', 'Difficulty': '高级'},
    {'Course Code': 'POLS510', 'Course Title': '政治哲学', 'Description': '政治思想的基本问题和理论。', 'Level': '研究生', 'Department': '政治学', 'Difficulty': '高级'},
    {'Course Code': 'ART501', 'Course Title': '艺术批评理论', 'Description': '艺术作品的分析和评价理论。', 'Level': '研究生', 'Department': '艺术', 'Difficulty': '高级'},
    {'Course Code': 'MUS501', 'Course Title': '作曲理论', 'Description': '音乐创作的理论和技巧。', 'Level': '研究生', 'Department': '音乐', 'Difficulty': '高级'},
    {'Course Code': 'CS650', 'Course Title': '机器学习', 'Description': '使计算机系统具有学习能力的理论和方法。', 'Level': '研究生', 'Department': '计算机科学', 'Difficulty': '高级'},
    {'Course Code': 'MATH610', 'Course Title': '偏微分方程', 'Description': '涉及多元函数及其偏导数的方程研究。', 'Level': '研究生', 'Department': '数学', 'Difficulty': '高级'},
    {'Course Code': 'ENG610', 'Course Title': '后殖民文学', 'Description': '后殖民语境下的文学研究。', 'Level': '研究生', 'Department': '英语', 'Difficulty': '高级'},
    {'Course Code': 'HIST601', 'Course Title': '史学理论', 'Description': '历史研究的方法和解释。', 'Level': '研究生', 'Department': '历史', 'Difficulty': '高级'},
    {'Course Code': 'PHYS610', 'Course Title': '广义相对论', 'Description': '引力的几何理论。', 'Level': '研究生', 'Department': '物理学', 'Difficulty': '高级'},
    {'Course Code': 'ECON601', 'Course Title': '高级微观经济学', 'Description': '微观经济学的深入分析。', 'Level': '研究生', 'Department': '经济学', 'Difficulty': '高级'},
    {'Course Code': 'SOCY601', 'Course Title': '社会理论', 'Description': '社会学的主要理论流派和思想家。', 'Level': '研究生', 'Department': '社会学', 'Difficulty': '高级'},
    {'Course Code': 'BIOL205', 'Course Title': '细胞生物学', 'Description': '...', 'Level': '本科二年级', 'Department': '生物学', 'Difficulty': '中级'},
    {'Course Code': 'CHEM210', 'Course Title': '定量分析化学', 'Description': '...', 'Level': '本科二年级', 'Department': '化学', 'Difficulty': '中级'},
    {'Course Code': 'PHIL220', 'Course Title': '逻辑学', 'Description': '...', 'Level': '本科二年级', 'Department': '哲学', 'Difficulty': '中级'},
    {'Course Code': 'POLS230', 'Course Title': '国际关系', 'Description': '...', 'Level': '本科二年级', 'Department': '政治学', 'Difficulty': '中级'},
    {'Course Code': 'ART250', 'Course Title': '文艺复兴艺术', 'Description': '...', 'Level': '本科二年级', 'Department': '艺术', 'Difficulty': '中级'},
    {'Course Code': 'MUS240', 'Course Title': '音乐理论', 'Description': '...', 'Level': '本科二年级', 'Department': '音乐', 'Difficulty': '中级'},
]
courses_df = pd.DataFrame(courses_data)
num_courses = len(courses_df)
print(f"已创建 {num_courses} 门课程。")

# 2. 创建学生列表 (100 名)
num_students = 100
students = [f'S{i+1:03d}' for i in range(num_students)]
print(f"已创建 {num_students} 名学生。")

# 3. 创建教师列表并分配专业 (40 名)
num_teachers = 40
teachers = [f'T{i+1:03d}' for i in range(num_teachers)]
# 假设每个老师随机分配 1-3 个专业领域 (简化模型)
departments = courses_df['Department'].unique().tolist()
teacher_expertise = {teacher: random.sample(departments, random.randint(1, 3)) for teacher in teachers}
print(f"已创建 {num_teachers} 名教师，并随机分配了专业领域。")

# 为每个老师分配他们可以教授的课程 (基于专业)
teacher_courses = {teacher: [] for teacher in teachers}
for teacher, expertise in teacher_expertise.items():
    possible_courses = courses_df[courses_df['Department'].isin(expertise)]['Course Code'].tolist()
    num_assign = min(random.randint(1, 5), len(possible_courses))
    # 确保教师只教授其专业领域的课程
    teacher_courses[teacher] = random.sample(possible_courses, num_assign)

# 4. 分配学生选课 (每人 1-5 门，每门至少 3 人)
student_courses = {student: [] for student in students}
course_enrollment = {code: 0 for code in courses_df['Course Code']}

# 初始随机分配
for student in students:
    num_courses_to_enroll = random.randint(1, 5)
    possible_courses = courses_df['Course Code'].tolist()
    enrolled_courses = random.sample(possible_courses, min(num_courses_to_enroll, len(possible_courses)))
    student_courses[student] = enrolled_courses
    for course_code in enrolled_courses:
        course_enrollment[course_code] += 1

# 迭代调整以满足每门课程至少 3 人选修
max_iterations = 100  # 设置最大迭代次数以防止无限循环
iteration = 0
while any(count < 3 for count in course_enrollment.values()) and iteration < max_iterations:
    iteration += 1
    unmet_courses = [code for code, count in course_enrollment.items() if count < 3]
    if not unmet_courses:
        break

    # 找到一个选课较多且有未满足课程的学生进行调整
    eligible_students = [s for s in students if len(student_courses[s]) > 1]
    if not eligible_students:
        print("警告：无法满足所有课程至少 3 人选修的要求。")
        break

    student_to_adjust = random.choice(eligible_students)
    course_to_drop = random.choice(student_courses[student_to_adjust])
    course_to_add = random.choice(unmet_courses)

    if course_to_add not in student_courses[student_to_adjust]:
        student_courses[student_to_adjust].remove(course_to_drop)
        student_courses[student_to_adjust].append(course_to_add)
        course_enrollment[course_to_drop] -= 1
        course_enrollment[course_to_add] += 1

print("\n学生选课情况：")
for student, courses in student_courses.items():
    print(f"{student}: {courses}")

print("\n课程选修人数：")
for course, count in course_enrollment.items():
    print(f"{course}: {count} 人")

# 5. 记录辅导关系 (假设每位选课学生在每门课都有 1-3 次辅导)
tutoring_sessions = []
for student, enrolled_courses in student_courses.items():
    for course_code in enrolled_courses:
        # 找到教授这门课的老师
        possible_teachers = [teacher for teacher, courses_taught in teacher_courses.items() if course_code in courses_taught]
        if possible_teachers:
            teacher_for_course = random.choice(possible_teachers)
            num_sessions = random.randint(1, 3)
            tutoring_sessions.extend([
                {'Student ID': student, 'Teacher ID': teacher_for_course, 'Course Code': course_code}
                for _ in range(num_sessions)
            ])

# 将数据转换为字典，准备输出为 JSON
data_to_output = {
    "courses": courses_data,
    "students": [{"Student ID": student, "Courses": courses} for student, courses in student_courses.items()],
    "teachers": [{"Teacher ID": teacher, "Expertise": expertise, "Courses Taught": courses}
                 for teacher, expertise, courses in zip(teachers, teacher_expertise.values(), teacher_courses.values())],
    "tutoring_sessions": tutoring_sessions,
    "course_enrollment": course_enrollment
}

# 定义输出文件名
output_files = {
    "courses": "courses.json",
    "students": "students.json",
    "teachers": "teachers.json",
    "tutoring_sessions": "tutoring_sessions.json",
    "course_enrollment": "course_enrollment.json"
}

# 将数据输出到 JSON 文件
for key, filename in output_files.items():
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data_to_output[key], f, ensure_ascii=False, indent=4)
    print(f"数据已保存到 {filename}")

