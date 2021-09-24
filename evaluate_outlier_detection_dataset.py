from collections import OrderedDict
from gensim.models import KeyedVectors
import json
import itertools
import csv
import create_outlier_detection_dataset as codd

def main():
    # je, jj, rt, ra, ro, rm, abb_ej, abb_others は適宜変更
    # file_nameの入力
    file_name = codd.name()

    # ファイルの読み込み（idが文字列）
    with open(f'{file_name}/data_abb_others.json', 'r') as f:
        output_dict = json.load(f, object_pairs_hook=OrderedDict)

    models_path = output_dict["param"]["model_paths"]
    data = output_dict["data"]
    words = []
    outliers = []
    for i in range(len(data)):
        words.append(data[i]["words"])
        outliers.append(data[i]["outliers"])


    # modelの読み込み
    models = []
    for model_path in models_path:
        model = KeyedVectors.load(model_path)
        models.append(model)  

    # cos類似度
    ans = []
    num = -1
    outliers_num = 10
    for model in models:
        num += 1
        independence_cnt = 0
        group_cnt = 0
        # pathの名前を処理
        name = models_path[num]
        name = name.rsplit('/', 1)[1]
        name = name.rsplit('.', 1)[0]
        order = -1
        for sim_word in words:
            order += 1
            sub_group_cnt = 0
            for i in range(outliers_num):
                word = sim_word
                data = word + [outliers[order][i]]
                word = list(itertools.combinations(data, 2))

                score = [0 for _ in range(len(word))]
                for word_a, word_b in word:
                    index_a = list(data).index(word_a)
                    index_b = list(data).index(word_b)
                    # cos類似度
                    score[index_a] += model.similarity(word_a, word_b)
                    score[index_b] += model.similarity(word_a, word_b) 
                    
                # 外れ値の結果と類似度の平均を記録
                ans.append(score.index(min(score)))
                score_ave = []
                for i in range(len(word)):
                    score_ave.append(score[i]/len(word))
                write_data = data + score_ave
                with open(f'{file_name}/{name}_abb_others_cos.csv', 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow(write_data)
                    
                if score.index(min(score)) == int( len(word) -1 ):
                    independence_cnt += 1
                    sub_group_cnt += 1

            if sub_group_cnt == outliers_num:
                group_cnt += 1

        # accuracy
        independence_length = len(words)*outliers_num
        independence_acc = independence_cnt / independence_length
        group_length = len(words)
        group_acc = group_cnt / group_length
        print(independence_cnt)
        print(independence_acc)
        print(group_cnt)
        print(group_acc)
        with open(f'{file_name}/{name}_abb_others_acc.csv', 'w') as f:
                print(f'independence_data数：{independence_length}', file = f)
                print(f'independence_正解数：{independence_cnt}', file = f)
                print(f'independence_acc：{independence_acc}', file = f)
                print(f'group_data数：{group_length}', file = f)
                print(f'group_正解数：{group_cnt}', file = f)
                print(f'group_acc：{group_acc}', file = f)


if __name__ == '__main__':
    main()
