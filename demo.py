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