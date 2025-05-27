import json
import random

# 常用英文名和拼音姓氏
english_first_names = [
    "Leary", "Kevin", "Amy", "Linda", "Eric", "Lucy", "Tom", "Anna", "David", "Cindy",
    "Jason", "Helen", "Jack", "Sandy", "Peter", "Grace", "Tony", "Daisy", "Leo", "Maggie",
    "Jerry", "Betty", "Frank", "Ivy", "Sam", "Nina", "Andy", "Lily", "Henry", "Vivian"
]
pinyin_surnames = [
    "Wang", "Li", "Zhang", "Liu", "Chen", "Yang", "Zhao", "Huang", "Zhou", "Wu",
    "Xu", "Sun", "Hu", "Zhu", "Gao", "Lin", "He", "Guo", "Ma", "Luo"
]

def random_english_chinese_name(used):
    while True:
        name = random.choice(english_first_names) + ' ' + random.choice(pinyin_surnames)
        if name not in used:
            return name

# 教师
with open('teachers.json', 'r', encoding='utf-8') as f:
    teachers = json.load(f)
# 不修改教师名
with open('teachers.json', 'w', encoding='utf-8') as f:
    json.dump(teachers, f, ensure_ascii=False, indent=4)

# 学生
with open('students.json', 'r', encoding='utf-8') as f:
    students = json.load(f)
used_names = set()
for s in students:
    name = random_english_chinese_name(used_names)
    s['Student Name'] = name
    used_names.add(name)
with open('students.json', 'w', encoding='utf-8') as f:
    json.dump(students, f, ensure_ascii=False, indent=4)
print('已为所有学生分配英文+拼音姓氏名字') 