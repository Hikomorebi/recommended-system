# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import numpy as np

user_table = []     #列表元素为字典，每个字典对应一个用户对电影的打分情况
movie_table = {}    #字典每个 item 的 value 也为字典，对应每部电影的打分情况
average = 0         #总的平均值
user_average_table = []  #列表元素对应每个用户的电影打分平均值
movie_average_table = {}    #对应每部电影被用户打分的平均值
temp_count = 0      #用于计算总平均值
user_set = []       #列表元素为集合，对应每个用户打过分的电影的集合
n = 10               #取相似用户的个数
"""
读取 train.txt 数据，完成 user_table，movie_table，user_average_table
并求出总的平均值： average
"""
with open("data-202205/train.txt",'r') as f:
    while True:
        line = f.readline().strip()
        if not line:
            break
        str_list = line.split('|')
        user_id = eval(str_list[0])     #用户id
        mark_count = eval(str_list[1])  #该用户打分的电影数量
        temp_count += mark_count
        user_table.append({})
        one_user_average = 0
        for _ in range(mark_count):
            str_list = f.readline().strip().split()
            temp_movie_id = eval(str_list[0])
            temp_mark = eval(str_list[1])
            user_table[user_id][temp_movie_id] = temp_mark
            one_user_average += temp_mark
            if temp_movie_id in movie_table.keys():
                movie_table[temp_movie_id][user_id] = temp_mark
            else:
                movie_table[temp_movie_id] = {user_id:temp_mark}
        average += one_user_average
        one_user_average = one_user_average / mark_count
        user_average_table.append(one_user_average)
average = average / temp_count
print('平均给分为：%d' %average)

total_len = len(user_table)
"""
生成 user_set
"""
for _ in range(total_len):
    user_set.append(set([x for x in user_table[_].keys()]))

"""
计算 movie_average_table
"""
for movie in movie_table.keys():
    tmp_mark = 0
    for _ in movie_table[movie].keys():
        tmp_mark += movie_table[movie][_]
    movie_average_table[movie] = tmp_mark / len(movie_table[movie])

"""
开始预测
"""
with open("data-202205/test.txt",'r') as f_test:
    with open("data-202205/myresult.txt",'w') as f_result:
        while True:
            line = f_test.readline().strip()
            if not line:
                break
            f_result.write(line+'\n')
            print(line)
            str_list = line.split('|')
            user_id = eval(str_list[0])
            mark_count = eval(str_list[1])
            for _ in range(mark_count):
                similarity_matrix = {}
                movie_number = eval(f_test.readline().strip())  #需要预测的 movie 的 id
                write_line = '%d' %movie_number
                if movie_number not in movie_table: #电影列表中没有该电影
                    base_score = user_average_table[user_id]
                    write_line += ' %f\n' % base_score
                    f_result.write(write_line)
                    continue
                base_score = user_average_table[user_id] + movie_average_table[movie_number] - average
                #if movie_number in movie_table.keys():
                watched_user = movie_table[movie_number] #看过该电影的用户列表，我们将从中找出前n个与目标用户相似的用户
                for other_user in watched_user.keys():
                    collective_movie = user_set[user_id].intersection(user_set[other_user]) #求交集
                    user_list = []  #目标用户的打分向量
                    other_user_list = []    #看过该电影的用户的打分向量
                    for _movie in collective_movie:
                        user_list.append(user_table[user_id][_movie] - user_average_table[user_id])
                        other_user_list.append(user_table[other_user][_movie] - user_average_table[other_user])
                    if len(user_list) != 0: #若两者之间有都看过的电影
                        corr = np.corrcoef(np.array(user_list), np.array(other_user_list))[0][1]
                        if not math.isnan(corr):
                            similarity_matrix[other_user] = corr  #得到每一个看过目标电影的用户与目标用户的 pearson相似度
                sorted_similarity_matrix = sorted(similarity_matrix.items(), key=lambda x: x[1], reverse=True)
                #similarity_users = [x[0] for x in sorted_similarity_matrix[:n]] #获取前 n 个最相似用户的 id


                weighted_scores = 0.
                corr_values_sum = 0.
                tmp_cnt = 0
                for user in sorted_similarity_matrix:
                    if tmp_cnt >= n:
                        break
                    tmp_cnt += 1
                    corr_value = user[1]  # 两个用户之间的相似性
                    if corr_value <= 0:
                        break
                    weighted_scores += corr_value * (user_table[user[0]][movie_number] + average - user_average_table[user[0]] - movie_average_table[movie_number])  # 加权分数
                    corr_values_sum += corr_value

                if corr_values_sum == 0:
                    final_scores = base_score
                else:
                    final_scores = base_score + weighted_scores / corr_values_sum
                if final_scores > 100:
                    final_scores = 100
                elif final_scores < 0:
                    final_scores = 0
                write_line += ' %f\n' %final_scores
                f_result.write(write_line)
                print(write_line)

