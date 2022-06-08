import numpy as np
import pandas as pd
user_table = []
movie_table = {}
average = 0
temp_count = 0
"""
读取 train.txt 数据至 user_table 中
同时计算平均给分的大小
"""
with open("data-202205/mydemo.txt",'r') as f:
    while True:
        line = f.readline().strip()
        if not line:
            break
        str_list = line.split('|')
        assert(len(str_list) == 2)
        user_id = eval(str_list[0])
        mark_count = eval(str_list[1])  #该用户打分的电影数量
        temp_count += mark_count
        user_table.append({})
        for _ in range(mark_count):
            str_list = f.readline().strip().split()
            assert(len(str_list) == 2)
            temp_number = eval(str_list[1])
            temp_movie_number = eval(str_list[0])
            user_table[user_id][temp_movie_number] = temp_number
            average += temp_number

            if temp_movie_number in movie_table.keys():
                movie_table[temp_movie_number][user_id] = temp_number
            else:
                movie_table[temp_movie_number] = {user_id:temp_number}
average = average / temp_count
print(average)

total_len = len(user_table)
similarity_matrix = pd.DataFrame(np.zeros((total_len, total_len)), index=range(total_len), columns=range(total_len))

for user in range(total_len):
    for other_user in range(total_len):
        user_list = []
        other_user_list = []
        if user != other_user:
            for movie in movie_table:
                movie_rating = movie_table[movie]
                if user in movie_rating and other_user in movie_rating:
                    user_list.append(movie_rating[user])
                    other_user_list.append(movie_rating[other_user])
            similarity_matrix[user][other_user] = np.corrcoef(np.array(user_list), np.array(other_user_list))[0][1]

print(similarity_matrix)
"""
转换为 Pearson 矩阵
"""

# temp_average = 0
# for user in user_table:
#     temp_average = 0
#     for movie in user.keys():
#         temp_average += user[movie]
#     temp_average = temp_average / len(user)
#     print(temp_average)
#     for movie in user.keys():
#         user[movie] -= temp_average



with open("data-202205/mytest.txt",'r') as f_test:
    with open("data-202205/myresult.txt",'w') as f_result:
        while True:
            line = f_test.readline().strip()
            if not line:
                break
            str_list = line.split('|')
            user_id = eval(str_list[0])
            mark_count = eval(str_list[1])
            for _ in range(mark_count):
                movie_number = eval(f_test.readline().strip())
                n = 2
                similarity_users = similarity_matrix[user_id].sort_values(ascending=False)[:n].index.tolist()
                print(similarity_users)
                base_score = np.mean(np.array([value for value in user_table[user_id].values()]))
                weighted_scores = 0.
                corr_values_sum = 0.
                for user in similarity_users:
                    corr_value = similarity_matrix[user_id][user]  # 两个用户之间的相似性
                    mean_user_score = np.mean(np.array([value for value in user_table[user].values()]))  # 每个用户的打分平均值
                    weighted_scores += corr_value * (user_table[user][movie_number] - mean_user_score)  # 加权分数
                    corr_values_sum += corr_value
                final_scores = base_score + weighted_scores / corr_values_sum
                print(final_scores)

