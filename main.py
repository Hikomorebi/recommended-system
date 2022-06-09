import numpy as np
user_table = []
movie_table = {}
average = 0
temp_count = 0
"""
读取 train.txt 数据至 user_table 中
同时计算平均给分的大小
"""
with open("data-202205/train.txt",'r') as f:
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
            temp_mark = eval(str_list[1])
            temp_movie_id = eval(str_list[0])
            user_table[user_id][temp_movie_id] = temp_mark
            average += temp_mark

            if temp_movie_id in movie_table.keys():
                movie_table[temp_movie_id][user_id] = temp_mark
            else:
                movie_table[temp_movie_id] = {user_id:temp_mark}
average = average / temp_count
print('平均给分为：%d' %average)

#total_len = len(user_table)
#similarity_matrix = pd.DataFrame(np.zeros((total_len, total_len)), index=range(total_len), columns=range(total_len))

# for user in range(total_len):
#     for other_user in range(total_len):
#         user_list = []
#         other_user_list = []
#         if user != other_user:
#             for movie in movie_table:
#                 watched_user = movie_table[movie]
#                 if user in watched_user and other_user in watched_user:
#                     user_list.append(watched_user[user])
#                     other_user_list.append(watched_user[other_user])
#             similarity_matrix[user][other_user] = np.corrcoef(np.array(user_list), np.array(other_user_list))[0][1]
#
# print(similarity_matrix)
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


similarity_matrix = {}
with open("data-202205/test.txt",'r') as f_test:
    with open("data-202205/myresult.txt",'w') as f_result:
        while True:
            line = f_test.readline().strip()
            if not line:
                break
            f_result.writelines(line+'\n')

            str_list = line.split('|')
            user_id = eval(str_list[0])
            mark_count = eval(str_list[1])
            for _ in range(mark_count):
                movie_number = eval(f_test.readline().strip())
                write_line = '%d' %movie_number
                n = 2
                watched_user = movie_table[movie_number] #看过该电影的用户列表，我们将从中找出前n个与目标用户相似的用户
                for other_user in watched_user.keys():
                    if user_id == other_user:
                        print("目标用户已经为该电影打分")
                        exit(0)
                    user_list = []  #目标用户的打分向量
                    other_user_list = []    #看过该电影的用户的打分向量
                    for movie_id in movie_table.keys(): #遍历 movie_table ，得到目标用户与看过该电影的用户均打过分的电影以及打分的列表
                        marked_movie_list = movie_table[movie_id]
                        if user_id in marked_movie_list.keys() and other_user in marked_movie_list.keys():
                            user_list.append(marked_movie_list[user_id])
                            other_user_list.append(marked_movie_list[other_user])
                    similarity_matrix[other_user] = np.corrcoef(np.array(user_list), np.array(other_user_list))[0][1]   #得到每一个看过目标电影的用户与目标用户的 pearson相似度
                    sorted_similarity_matrix = sorted(similarity_matrix.items(), key=lambda x: x[1], reverse=True)  #排序，将相似度高的用户排在前面

                n = max(n,len(sorted_similarity_matrix))
                similarity_users = [x[0] for x in sorted_similarity_matrix[:n]] #获取前 n 个最相似用户的 id
                base_score = np.mean(np.array([value for value in user_table[user_id].values()]))
                weighted_scores = 0.
                corr_values_sum = 0.
                for user in similarity_users:
                    corr_value = similarity_matrix[user]  # 两个用户之间的相似性
                    if corr_value <= 0:
                        break
                    mean_user_score = np.mean(np.array([value for value in user_table[user].values()]))  # 每个用户的打分平均值
                    weighted_scores += corr_value * (user_table[user][movie_number] - mean_user_score)  # 加权分数
                    corr_values_sum += corr_value
                if corr_value <= 0:
                    final_scores = base_score
                else:
                    final_scores = base_score + weighted_scores / corr_values_sum
                if final_scores > 100:
                    final_scores = 100
                elif final_scores < 0:
                    final_scores = 0
                write_line += ' %d\n' %final_scores
                f_result.write(write_line)

