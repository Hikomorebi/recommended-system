# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import numpy as np
import random
import math
import time

user_table = []  # 列表元素为字典，每个字典对应一个用户对电影的打分情况
movie_table = {}  # 字典每个 item 的 value 也为字典，对应每部电影的打分情况
average = 0  # 总的平均值
user_average_table = []  # 列表元素对应每个用户的电影打分平均值
movie_average_table = {}  # 对应每部电影被用户打分的平均值
temp_count = 0  # 用于计算总平均值
user_set = []  # 列表元素为集合，对应每个用户打过分的电影的集合
n = 6  # 取相似用户的个数
diffsum = 0
RMSEnum = 0  # RMSE中的N
"""
读取 train.txt 数据，完成 user_table，movie_table，user_average_table
并求出总的平均值： average
"""
with open("data-202205/train.txt", 'r') as f:
    with open("data-202205/ourtest.txt", 'w') as o_test:
        with open("data-202205/ouranswer.txt", 'w') as o_answer:
            while True:
                line = f.readline().strip()
                if not line:
                    break
                str_list = line.split('|')
                user_id = eval(str_list[0])  # 用户id
                mark_count = eval(str_list[1])  # 该用户打分的电影数量
                temp_count += mark_count
                user_table.append({})
                one_user_average = 0
                testlist = []  # 该用户作为test集的数据
                testanswerlist = []  # 该用户作为test集的数据答案
                for _ in range(mark_count):
                    str_list = f.readline().strip().split()
                    temp_movie_id = eval(str_list[0])
                    temp_mark = eval(str_list[1])
                    probablity = random.random()  # 抽取10%的train data作为test data
                    if probablity < 0.001:
                        # write_line = '%d' % temp_movie_id
                        # o_test.write(write_line + '\n')
                        # write_line += ' %d\n' % temp_mark
                        # o_answer.write(write_line + '\n')
                        testlist.append(temp_movie_id)
                        testanswerlist.append(temp_mark)
                        continue  # 从train中抽取出的test数据不进入train的过程
                    user_table[user_id][temp_movie_id] = temp_mark
                    one_user_average += temp_mark
                    if temp_movie_id in movie_table.keys():
                        movie_table[temp_movie_id][user_id] = temp_mark
                    else:
                        movie_table[temp_movie_id] = {user_id: temp_mark}
                if len(testlist) > 0:  # 写入单个用户抽取的test数据
                    length = len(testlist)
                    o_test.write(str(user_id) + '|' + str(length) + '\n')
                    o_answer.write(str(user_id) + '|' + str(length) + '\n')
                    for _ in range(length):
                        o_test.write(str(testlist[_]) + '\n')
                        o_answer.write(str(testlist[_]) + ' ' + str(testanswerlist[_]) + '\n')
                average += one_user_average
                one_user_average = one_user_average / mark_count
                user_average_table.append(one_user_average)
average = average / temp_count
print('平均给分为：%d' % average)

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

attribute_table = {}  # 以属性为key，包含某一属性的所有电影
movie_attribute_table = {}  # 存放每个movie的attribute，key为movie，value为attribute（是个list）
"""
读取 itemAttribute.txt 数据，完成字典attribute_table，
attribute_table中key是属性，value是一个list，记录着所有有该属性的电影
"""
with open("data-202205/itemAttribute.txt", 'r') as f:
    while True:
        line = f.readline().strip()
        if not line:
            break
        str_list = line.split('|')
        movie_id = eval(str_list[0])
        attribute1 = eval(str_list[1])
        if attribute1 is not None:
            if attribute1 in attribute_table.keys():
                attribute_table[attribute1].append(movie_id)
            else:
                attribute_table[attribute1] = []
                attribute_table[attribute1].append(movie_id)
        attribute2 = eval(str_list[2])
        if attribute2 is not None:
            if attribute2 in attribute_table.keys():
                attribute_table[attribute2].append(movie_id)
            else:
                attribute_table[attribute2] = []
                attribute_table[attribute2].append(movie_id)
        movie_attribute_table[movie_id] = [attribute1, attribute2]

'''
类似于item_item的协同过滤，但用attribute去衡量movie之间的相似度
'''

def item_item(score, movie_id, user_id):
    if movie_id not in movie_attribute_table.keys():
        return score
    attribute_list = movie_attribute_table[movie_id]
    isUse1 = False  # 第一个属性有没有被用上
    isUse2 = False  # 第二个属性有没有被用上
    attribute1_score = 0
    attribute2_score = 0
    if attribute_list[0] is not None:
        isUse1 = True
        movie_list = attribute_table[attribute_list[0]]  # 所有有第一个属性的movie
        num = 0
        sum = 0
        for movie in movie_list:
            if movie in user_table[user_id].keys():
                num += 1
                sum += user_table[user_id][movie]
        if num != 0:
            attribute1_score = sum / num
        else:
            isUse1 = False
    if attribute_list[1] is not None:
        isUse2 = True
        movie_list = attribute_table[attribute_list[1]]  # 所有有第二个属性的movie
        num = 0
        sum = 0
        for movie in movie_list:
            if movie in user_table[user_id].keys():
                num += 1
                sum += user_table[user_id][movie]
        if num != 0:
            attribute2_score = sum / num
        else:
            isUse2 = False
    if isUse1 and isUse2:
        return 0.6 * score + 0.4 * (0.5*attribute1_score + 0.5*attribute2_score)  # 此时两个属性的权重是55开，可以改成不均等的（主属性、副属性）
    elif isUse1:
        return 0.6 * score + 0.4 * attribute1_score
    elif isUse2:
        return 0.6 * score + 0.4 * attribute2_score
    else:
        return score


"""
开始预测
"""
num = 0
tic = time.time()
istest = False
with open("data-202205/test.txt", 'r') as f_test:
    with open("data-202205/ouranswer.txt", 'r') as f_answer:
        with open("data-202205/myresult.txt", 'w') as f_result:
            while True:
                line = f_test.readline().strip()
                if istest:
                    f_answer.readline()
                if not line:
                    break
                f_result.write(line + '\n')
                # print(line)
                str_list = line.split('|')
                user_id = eval(str_list[0])
                mark_count = eval(str_list[1])
                for _ in range(mark_count):
                    num += 1
                    similarity_matrix = {}
                    movie_number = eval(f_test.readline().strip())  # 需要预测的 movie 的 id
                    if istest:
                        answerlist = f_answer.readline().strip().split()
                        answer = float(answerlist[1])  # 正确答案，用于求RMSE
                    write_line = '%d' % movie_number
                    if movie_number not in movie_table:  # 电影列表中没有该电影
                        base_score = user_average_table[user_id]
                        final_scores = item_item(base_score, movie_number, user_id)
                        write_line += ' %f\n' % final_scores
                        if istest:
                            diffsum += (final_scores - answer) ** 2
                            RMSEnum += 1
                        f_result.write(write_line)
                        continue
                    base_score = user_average_table[user_id] + movie_average_table[movie_number] - average
                    # if movie_number in movie_table.keys():
                    watched_user = movie_table[movie_number]  # 看过该电影的用户列表，我们将从中找出前n个与目标用户相似的用户
                    for other_user in watched_user.keys():
                        collective_movie = user_set[user_id].intersection(user_set[other_user])  # 求交集
                        user_list = []  # 目标用户的打分向量
                        other_user_list = []  # 看过该电影的用户的打分向量
                        for _movie in collective_movie:
                            user_list.append(user_table[user_id][_movie] - user_average_table[user_id])
                            other_user_list.append(user_table[other_user][_movie] - user_average_table[other_user])
                        if len(user_list) != 0:  # 若两者之间有都看过的电影
                            corr = np.corrcoef(np.array(user_list), np.array(other_user_list))[0][1]
                            if not math.isnan(corr):
                                similarity_matrix[other_user] = corr  # 得到每一个看过目标电影的用户与目标用户的 pearson相似度
                    sorted_similarity_matrix = sorted(similarity_matrix.items(), key=lambda x: x[1], reverse=True)
                    # similarity_users = [x[0] for x in sorted_similarity_matrix[:n]] #获取前 n 个最相似用户的 id

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
                        weighted_scores += corr_value * (
                                user_table[user[0]][movie_number] + average - user_average_table[user[0]] -
                                movie_average_table[movie_number])  # 加权分数
                        corr_values_sum += corr_value

                    if corr_values_sum == 0:
                        final_scores = base_score
                    else:
                        final_scores = base_score + weighted_scores / corr_values_sum
                    final_scores = item_item(final_scores, movie_number, user_id)
                    if final_scores > 100:
                        final_scores = 100
                    elif final_scores < 0:
                        final_scores = 0
                    write_line += ' %f\n' % final_scores
                    if istest:
                        diffsum += ((final_scores - answer) ** 2)
                        RMSEnum += 1
                    f_result.write(write_line)
                    #print(write_line)
                    if num % 1000 == 0:
                        print("finish %d" % num)
                        toc = time.time()
                        print("目前用时：%f" % (toc-tic))
print("RMSE：%f" % math.sqrt(diffsum / RMSEnum))