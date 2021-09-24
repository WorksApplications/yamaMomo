from collections import defaultdict
import itertools
import random
import pandas as pd
from tqdm import tqdm
import time

# 全データ読み込み
"""
"id": グループ番号
"uninflected": 体言/用言フラグ
"deployment": 展開制御フラグ
"numbers": グループ内の語彙番号
"type": 同一語彙素内での語形種別
"information": 同じ語形の語の中での略語情報
"fluctuation": 同じ語形の語の中での表記ゆれ情報
"field": 分野情報
"word": 見出し
"9": 予約
"10": 予約
"""
def load_sudachi_synonym_dataset(sudachi_synonym_path):
    sudachi_synonym_df = pd.read_csv(sudachi_synonym_path, names=["id", "uninflected", "deployment", "numbers", "type", "information", "fluctuation", "field", "word", "9", "10"], header=None)
    return sudachi_synonym_df


# preprocessing
def preprocessing(data):
    for index, row in data.iterrows(): 
        if row.numbers.count('/') != 0:
            mojis = row.numbers
            replace_row = row
            data = data.drop(index, axis=0)
            moji = mojis.split('/')
            for i in range(len(moji)):
                replace_row = replace_row.replace(replace_row.numbers, moji[i])
                data = data.append(replace_row)

    return data
    

# dropするデータの id 取得
def remove_index_not_in_models(data, models):
    remove_index = []
    for index, row in data.iterrows():            
        if any ([row.word not in model for model in models]):
            remove_index.append(index)
    return remove_index


# judge_create
def judge_create(gid, words):
    if len(gid) == 2 and words[0][0] == words[1][0]:
        return "No"
    elif len(gid) <= 1:
        return "No"
    else:
        return "Yes"



# je について
def create_mini_concept_set_je(data):
    mini_words_set_je = defaultdict(list)
    gid = []
    cnt = 0
    for index, row in data.groupby(['id', "numbers", "type", "information"]):
        mini_data = row.values.tolist()
        je_pair = []
        for i in range(len(mini_data)):
            gid.append(mini_data[i][0])
        if len(row) >= 2:
            j_lists = []
            e_lists = []
            for sub_index, sub_row in row.iterrows():
                if sub_row.fluctuation == 0:
                    j_lists.append(sub_row.word)
                if sub_row.fluctuation == 1:
                    e_lists.append(sub_row.word)
            for i in range(len(j_lists)):
                for j in range(len(e_lists)):
                    je_pair.append(j_lists[i])
                    je_pair.append(e_lists[j])
                    if len(je_pair) == 2:
                        mini_words_set_je[cnt] = je_pair
                    je_pair = []
                    cnt += 1

    # print(gid)
    # print(je_pairs)
        
    all_gids = set(mini_words_set_je.keys())
    is_create = judge_create(all_gids, list(mini_words_set_je.values()))
    if is_create == "No":
        print("mini_words_set_je does not create datasets")


    other_mini_words_sets_je = []
    num_concept_sample = 10
    for gid, pairs in sorted(mini_words_set_je.items()):
        other_gids = all_gids - {gid}
        gid_appends = random.sample(list(other_gids), num_concept_sample)
        other_mini_words_set_je = []
        for gid_append in gid_appends:
            other_mini_words_set_je.append(mini_words_set_je[gid_append])
        other_mini_words_sets_je.append(other_mini_words_set_je)

    return mini_words_set_je, other_mini_words_sets_je


# jj について
def create_mini_concept_set_jj(data):
    mini_words_set_jj = defaultdict(list)
    gid = []
    cnt = 0
    for index, row in data.groupby(['id', "numbers", "type", "information"]):
        mini_data = row.values.tolist()
        jj_pair = []
        for i in range(len(mini_data)):
            gid.append(mini_data[i][0])
        if len(row) >= 2:
            j_lists = []
            j_lists2 = []
            for sub_index, sub_row in row.iterrows():
                if sub_row.fluctuation == 0:
                    j_lists.append(sub_row.word)
                if sub_row.fluctuation == 2:
                    j_lists2.append(sub_row.word)
            for i in range(len(j_lists)):
                for j in range(len(j_lists2)):
                    jj_pair.append(j_lists[i])
                    jj_pair.append(j_lists2[j])
                    if len(jj_pair) == 2:
                        mini_words_set_jj[cnt] = jj_pair
                    jj_pair = []
                    cnt += 1

    # print(gid)
    # print(je_pairs)
        
    all_gids = set(mini_words_set_jj.keys())
    is_create = judge_create(all_gids, list(mini_words_set_jj.values()))
    if is_create == "No":
        print("mini_words_set_jj does not create datasets")


    other_mini_words_sets_jj = []
    num_concept_sample = 10
    for gid, pairs in sorted(mini_words_set_jj.items()):
        other_gids = all_gids - {gid}
        gid_appends = random.sample(list(other_gids), num_concept_sample)
        other_mini_words_set_jj = []
        for gid_append in gid_appends:
            other_mini_words_set_jj.append(mini_words_set_jj[gid_append])
        other_mini_words_sets_jj.append(other_mini_words_set_jj)


    return mini_words_set_jj, other_mini_words_sets_jj


# rt について
def create_mini_concept_set_rt(data):
    # models の中にはいっているもので、代表語と対訳で形成されているものだけを抽出
    mini_words_set_rt = defaultdict(list)
    gid = []
    cnt = 0
    for index, row in data.groupby(['id', "uninflected", "numbers", "information"]):
        mini_data = row.values.tolist()
        for i in range(len(mini_data)):
            gid.append(mini_data[i][0])
        rt_pair = []
        if len(row) >= 2:
            r_lists = []
            t_lists = []
            for sub_index, sub_row in row.iterrows():
                if sub_row.type == 0:
                    r_lists.append(sub_row.word)
                if sub_row.type == 1:
                    t_lists.append(sub_row.word)
            for i in range(len(r_lists)):
                for j in range(len(t_lists)):
                    rt_pair.append(r_lists[i])
                    rt_pair.append(t_lists[j])
                    if len(rt_pair) == 2:
                        mini_words_set_rt[cnt] = rt_pair
                    rt_pair = []
                    cnt += 1

    # print(gid)
    # print(rt_pairs)
        
    all_gids = set(mini_words_set_rt.keys())
    is_create = judge_create(all_gids, list(mini_words_set_rt.values()))
    if is_create == "No":
        print("mini_words_set_rt does not create datasets")

    other_mini_words_sets_rt = []
    num_outlier_sample = 10
    for gid, words in sorted(mini_words_set_rt.items()):
        other_gids = all_gids - {gid}
        gid_appends = random.sample(list(other_gids), num_outlier_sample)
        other_mini_words_set_rt = []
        for gid_append in gid_appends:
            other_mini_words_set_rt.append(mini_words_set_rt[gid_append])
        other_mini_words_sets_rt.append(other_mini_words_set_rt)
    
    return mini_words_set_rt, other_mini_words_sets_rt


# ra について
def create_mini_concept_set_ra(data):
    # models の中にはいっているもので、代表語と別称 (通称・愛称等)で形成されているものだけを抽出
    mini_words_set_ra = defaultdict(list)
    gid = []
    cnt = 0
    for index, row in data.groupby(['id', "uninflected", "numbers", "information"]):
        mini_data = row.values.tolist()
        for i in range(len(mini_data)):
            gid.append(mini_data[i][0])
        ra_pair = []
        if len(row) >= 2:
            r_lists = []
            a_lists = []
            for sub_index, sub_row in row.iterrows():
                if sub_row.type == 0:
                    r_lists.append(sub_row.word)
                if sub_row.type == 2:
                    a_lists.append(sub_row.word)
            for i in range(len(r_lists)):
                for j in range(len(a_lists)):
                    ra_pair.append(r_lists[i])
                    ra_pair.append(a_lists[j])
                    if len(ra_pair) == 2:
                        mini_words_set_ra[cnt] = ra_pair
                    ra_pair = []
                    cnt += 1

    # print(gid)
    # print(ra_pairs)
        
    all_gids = set(mini_words_set_ra.keys())
    is_create = judge_create(all_gids, list(mini_words_set_ra.values()))
    if is_create == "No":
        print("mini_words_set_ra does not create datasets")

    other_mini_words_sets_ra = []
    num_outlier_sample = 10
    for gid, words in sorted(mini_words_set_ra.items()):
        other_gids = all_gids - {gid}
        gid_appends = random.sample(list(other_gids), num_outlier_sample)
        other_mini_words_set_ra = []
        for gid_append in gid_appends:
            other_mini_words_set_ra.append(mini_words_set_ra[gid_append])
        other_mini_words_sets_ra.append(other_mini_words_set_ra)
    
    return mini_words_set_ra, other_mini_words_sets_ra

# ro について
def create_mini_concept_set_ro(data):
    # models の中にはいっているもので、代表語と旧称で形成されているものだけを抽出
    mini_words_set_ro = defaultdict(list)
    gid = []
    cnt = 0
    for index, row in data.groupby(['id', "uninflected", "numbers", "information"]):
        mini_data = row.values.tolist()
        for i in range(len(mini_data)):
            gid.append(mini_data[i][0])
        ro_pair = []
        if len(row) >= 2:
            r_lists = []
            o_lists = []
            for sub_index, sub_row in row.iterrows():
                if sub_row.type == 0:
                    r_lists.append(sub_row.word)
                if sub_row.type == 3:
                    o_lists.append(sub_row.word)
            for i in range(len(r_lists)):
                for j in range(len(o_lists)):
                    ro_pair.append(r_lists[i])
                    ro_pair.append(o_lists[j])
                    if len(ro_pair) == 2:
                        mini_words_set_ro[cnt] = ro_pair
                    ro_pair = []
                    cnt += 1

    # print(gid)
    # print(ro_pairs)
        
    all_gids = set(mini_words_set_ro.keys())
    is_create = judge_create(all_gids, list(mini_words_set_ro.values()))
    if is_create == "No":
        print("mini_words_set_ro does not create datasets")

    other_mini_words_sets_ro = []
    num_outlier_sample = 10
    for gid, words in sorted(mini_words_set_ro.items()):
        other_gids = all_gids - {gid}
        gid_appends = random.sample(list(other_gids), num_outlier_sample)
        other_mini_words_set_ro = []
        for gid_append in gid_appends:
            other_mini_words_set_ro.append(mini_words_set_ro[gid_append])
        other_mini_words_sets_ro.append(other_mini_words_set_ro)
    
    return mini_words_set_ro, other_mini_words_sets_ro

# rm について
def create_mini_concept_set_rm(data):
    # models の中にはいっているもので、代表語と旧称で形成されているものだけを抽出
    mini_words_set_rm = defaultdict(list)
    gid = []
    cnt = 0
    for index, row in data.groupby(['id', "uninflected", "numbers", "information"]):
        mini_data = row.values.tolist()
        for i in range(len(mini_data)):
            gid.append(mini_data[i][0])
        rm_pair = []
        if len(row) >= 2:
            r_lists = []
            m_lists = []
            for sub_index, sub_row in row.iterrows():
                if sub_row.type == 0:
                    r_lists.append(sub_row.word)
                if sub_row.type == 4:
                    m_lists.append(sub_row.word)
            for i in range(len(r_lists)):
                for j in range(len(m_lists)):
                    rm_pair.append(r_lists[i])
                    rm_pair.append(m_lists[j])
                    if len(rm_pair) == 2:
                        mini_words_set_rm[cnt] = rm_pair
                    rm_pair = []
                    cnt += 1

    
    all_gids = set(mini_words_set_rm.keys())
    is_create = judge_create(all_gids, list(mini_words_set_rm.values()))
    if is_create == "No":
        print("mini_words_set_rm does not create datasets")

    other_mini_words_sets_rm = []
    num_outlier_sample = 10
    for gid, words in sorted(mini_words_set_rm.items()):
        other_gids = all_gids - {gid}
        gid_appends = random.sample(list(other_gids), num_outlier_sample)
        other_mini_word_sets_rm = []
        for gid_append in gid_appends:
            other_mini_word_sets_rm.append(mini_words_set_rm[gid_append])
        other_mini_words_sets_rm.append(other_mini_word_sets_rm)
    
    return mini_words_set_rm, other_mini_words_sets_rm

# abb_je について
def create_mini_concept_set_abb_je(data):
# models の中にはいっているもので、代表語と旧称で形成されているものだけを抽出
    mini_words_set_abb_je = defaultdict(list)
    gid = []
    cnt = 0
    for index, row in data.groupby(['id', "deployment", "uninflected", "numbers", "fluctuation"]):
        mini_data = row.values.tolist()
        for i in range(len(mini_data)):
            gid.append(mini_data[i][0])
        abb_je_pair = []
        if len(row) >= 2:
            r_lists = []
            e_lists = []
            for sub_index, sub_row in row.iterrows():
                if sub_row.information == 0:
                    r_lists.append(sub_row.word)
                if sub_row.information == 1:
                    e_lists.append(sub_row.word)
            for i in range(len(r_lists)):
                for j in range(len(e_lists)):
                    abb_je_pair.append(r_lists[i])
                    abb_je_pair.append(e_lists[j])
                    if len(abb_je_pair) == 2:
                        mini_words_set_abb_je[cnt] = abb_je_pair
                    mini_words_set_abb_je = []
                    cnt += 1

    all_gids = set(mini_words_set_abb_je.keys())
    is_create = judge_create(all_gids, list(mini_words_set_abb_je.values()))
    if is_create == "No":
        print("mini_words_set_abb_je does not create datasets")

    other_mini_words_sets_abb_je = []
    num_outlier_sample = 10
    for gid, words in sorted(mini_words_set_abb_je.items()):
        other_gids = all_gids - {gid}
        gid_appends = random.sample(list(other_gids), num_outlier_sample)
        other_mini_words_set_abb_je = []
        for gid_append in gid_appends:
            other_mini_words_set_abb_je.append(mini_words_set_abb_je[gid_append])
        other_mini_words_sets_abb_je.append(other_mini_words_set_abb_je)
    
    return mini_words_set_abb_je, other_mini_words_sets_abb_je

# abb_others について
def create_mini_concept_set_abb_others(data):
# models の中にはいっているもので、代表語と旧称で形成されているものだけを抽出
    mini_words_set_abb_others = defaultdict(list)
    gid = []
    cnt = 0
    for index, row in data.groupby(['id',"deployment", "uninflected", "numbers", "fluctuation"]):
        mini_data = row.values.tolist()
        for i in range(len(mini_data)):
            gid.append(mini_data[i][0])
        abb_others_pair = []
        if len(row) >= 2:
            r_lists = []
            other_lists = []
            for sub_index, sub_row in row.iterrows():
                if sub_row.information == 0:
                    r_lists.append(sub_row.word)
                if sub_row.information == 2:
                    other_lists.append(sub_row.word)
            for i in range(len(r_lists)):
                for j in range(len(other_lists)):
                    abb_others_pair.append(r_lists[i])
                    abb_others_pair.append(other_lists[j])
                    if len(abb_others_pair) == 2:
                        mini_words_set_abb_others[cnt] = abb_others_pair
                    abb_others_pair = []
                    cnt += 1
        
    all_gids = set(mini_words_set_abb_others.keys())
    is_create = judge_create(all_gids, list(mini_words_set_abb_others.values()))
    if is_create == "No":
        print("mini_words_set_abb_others does not create datasets")

    other_mini_words_sets_abb_others = []
    num_outlier_sample = 10
    for gid, words in sorted(mini_words_set_abb_others.items()):
        other_gids = all_gids - {gid}
        gid_appends = random.sample(list(other_gids), num_outlier_sample)
        other_mini_words_set_abb_other = []
        for gid_append in gid_appends:
            word_append =  mini_words_set_abb_others[gid_append]
            other_mini_words_set_abb_other.append(word_append)
        other_mini_words_sets_abb_others.append(other_mini_words_set_abb_other)
    
    return mini_words_set_abb_others, other_mini_words_sets_abb_others


# field について
# models の中にはいっているもので、分野情報があるものだけを抽出
def delete_field_NULL(data):
    data = data[data['field'] != '()']
    data = data[~data['field'].str.contains('/')]    
    return data

def create_mini_concept_field(data):
# models の中にはいっているもので、分野情報毎にデータのペアを作成
    mini_words_set_field = defaultdict(list)
    mini_data = []
    cnt = 0
    for index, row in data.groupby(['field']):
        mini_data = row.word
        mini_data = mini_data.values.tolist()
        if len(mini_data) < 2:
            continue
        field_pair = list(itertools.combinations(mini_data, 2)) + list(data.field)
        mini_words_set_field[cnt] = field_pair
        cnt += 1
        
    all_gids = set(mini_words_set_field.keys())
    is_create = judge_create(all_gids, list(mini_words_set_field.values()))
    if is_create == "No":
        print("mini_words_set_field does not create datasets")

    return mini_words_set_field


# データを抽出
def select_mini_concept_field(mini_concept_field):
    data = []
    data_size = []
    for element in mini_concept_field.values():
        if len(element) == 1:
            continue
        data.append(element)
        data_size.append(len(element))
        
    length_sub_data = min(data_size)
    length_data = min(length_sub_data, 10)

    select_data = []
    for k, sub_data in enumerate(itertools.combinations(data, 2)):
        mini_sub_data = []
        sub_data_1 = sub_data[0]
        sub_data_2 = sub_data[1]
        for i in range(length_data):
            mini_sub_data.append(sub_data_1[i])
            mini_sub_data.append(sub_data_2[i])
            select_data.append(mini_sub_data)
            print(mini_sub_data)
            mini_sub_data = []
        # print(k)

    return select_data, length_data