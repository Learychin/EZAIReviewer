import json

with open('course_ratings_low.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    ratings = item['ratings']['ratings']
    # 各维度分和细则分提升50%，最高不超过10分
    for cat, cat_info in ratings.items():
        cat_info['score'] = round(min(cat_info['score'] * 1.5, 10.0), 1)
        for k in cat_info['criteria']:
            cat_info['criteria'][k] = round(min(cat_info['criteria'][k] * 1.5, 10.0), 1)
    # 重新计算总分
    total = 0
    for cat, cat_info in ratings.items():
        total += cat_info['score'] * cat_info['weight']
    item['ratings']['total_score'] = round(total, 1)

with open('course_ratings_low.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print('已将低分组所有分数提升50%，最高不超过10分。') 