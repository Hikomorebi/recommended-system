import numpy as np
import  pandas as pd
user_table = []
movie_table = {}
average = 0
average_table = []
movie_average_table = {}
temp_count = 0
num = 0
n = 2
"""
读取 train.txt 数据至 user_table 中
同时计算每个用户平均给分的大小，记录在 average_table 中
"""
with open("data-202205/train.txt",'r') as f:
    while True:
        line = f.readline().strip()
        if not line:
            break
        str_list = line.split('|')
        user_id = eval(str_list[0])
        num += 1
        mark_count = eval(str_list[1])  #该用户打分的电影数量
        temp_count += mark_count
        user_table.append({})
        one_user_average = 0
        for _ in range(mark_count):
            str_list = f.readline().strip().split()
            temp_movie_id = eval(str_list[0])
            temp_mark = eval(str_list[1])
            if temp_mark == 0:
                temp_mark == 1
            user_table[user_id][temp_movie_id] = temp_mark
            one_user_average += temp_mark
            if temp_movie_id in movie_table.keys():
                movie_table[temp_movie_id][user_id] = temp_mark
            else:
                movie_table[temp_movie_id] = {user_id:temp_mark}
        average += one_user_average
        one_user_average = one_user_average / mark_count
        average_table.append(one_user_average)
average = average / temp_count
print('平均给分为：%d' %average)
total_len = len(user_table)

for movie in movie_table.keys():
    tmp_mark = 0
    for _ in movie_table[movie].keys():
        tmp_mark += movie_table[movie][_]
    movie_average_table[movie] = tmp_mark / len(movie_table[movie])


similarity_matrix = pd.DataFrame(np.zeros((total_len, total_len)), index=range(total_len), columns=range(total_len))
with open("data-202205/test.txt",'r') as f_test:
    with open("data-202205/myresult.txt",'w') as f_result:
        while True:
            line = f_test.readline().strip()
            if not line:
                break
            f_result.write(line+'\n')
            str_list = line.split('|')
            user_id = eval(str_list[0])
            mark_count = eval(str_list[1])
            for _ in range(mark_count):
                movie_number = eval(f_test.readline().strip())
                write_line = '%d' %movie_number
                if movie_number in movie_table.keys():
                    watched_user = movie_table[movie_number] #看过该电影的用户列表，我们将从中找出前n个与目标用户相似的用户
                else:
                    print("没有用户看过该部电影")
                    exit(1)
                for other_user in watched_user.keys():
                    if user_id == other_user:
                        print("目标用户已经为该电影打分")
                        exit(0)
                    if similarity_matrix[user_id][other_user] == 0:
                        user_list = []  #目标用户的打分向量
                        other_user_list = []    #看过该电影的用户的打分向量
                        for movie_id in movie_table.keys(): #遍历 movie_table ，得到目标用户与看过该电影的用户均打过分的电影以及打分的列表
                            marked_movie_list = movie_table[movie_id]
                            if user_id in marked_movie_list.keys() and other_user in marked_movie_list.keys():
                                user_list.append(marked_movie_list[user_id] - average_table[user_id])
                                other_user_list.append(marked_movie_list[other_user] - average_table[other_user])
                        if len(user_list) != 0:
                            similarity_matrix[user_id][other_user] = np.corrcoef(np.array(user_list), np.array(other_user_list))[0][1]   #得到每一个看过目标电影的用户与目标用户的 pearson相似度
                            similarity_matrix[other_user][user_id] = similarity_matrix[user_id][other_user]
                similarity_users = similarity_matrix[user_id].sort_values(ascending=False)[:n].index.tolist()

                weighted_scores = 0.
                corr_values_sum = 0.
                base_score = average_table[user_id] + movie_average_table[movie_number] - average_table
                for user in similarity_users:
                    corr_value = similarity_matrix[user_id][user]  # 两个用户之间的相似性
                    if corr_value <= 0:
                        break
                    weighted_scores += corr_value * (user_table[user][movie_number] + average - average_table[user] - movie_average_table[movie_number])  # 加权分数
                    corr_values_sum += corr_value
                if corr_values_sum == 0:
                    final_scores = base_score
                else:
                    final_scores = base_score + weighted_scores / corr_values_sum
                if final_scores > 100:
                    final_scores = 100
                elif final_scores < 0:
                    final_scores = 0
                write_line += ' %d\n' %final_scores
                f_result.write(write_line)
                print(user_id)
                print(movie_number)
                print(write_line)

