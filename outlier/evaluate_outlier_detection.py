from collections import OrderedDict
from gensim.models import KeyedVectors
import json
import itertools
import csv
import argparse
import glob
import os

def load_w2v_model(model_path):
    if model_path.split(".")[-1] == "txt":
        model = KeyedVectors.load_word2vec_format(model_path)
    else:
        model = KeyedVectors.load(model_path)
    return model

def main():
    parser = argparse.ArgumentParser(description='eval with outlier')
    parser.add_argument('-d', '--data_dir', help='directory containing the created data', default="data_eval")
    args = parser.parse_args()

    # ファイルの読み込み（idが文字列）
    file_list = glob.glob(f'{args.data_dir}/*.json')
    print("evaluate...", file_list)

    for file_path in file_list:
        data_name = file_path.rsplit("/")[-1].split(".")[0]
        print(data_name)
        with open(file_path) as f:
            output_dict = json.load(f, object_pairs_hook=OrderedDict)

        data = output_dict["data"]
        words = []
        outliers = []
        for i in range(len(data)):
            words.append(data[i]["synos"])
            outliers.append(data[i]["outliers"])

        # modelの読み込み
        if "models_path" in locals() and models_path == output_dict["param"]["model_paths"]:
            print("reuse...", models_path)
        else:
            models_path = output_dict["param"]["model_paths"]
            print("loading...", models_path)
            models = [load_w2v_model(model_path) for model_path in models_path]
        

        # cos類似度
        ans = []
        outliers_num = 10
        for i, model in enumerate(models):
            name = models_path[i].rsplit('/', 1)[1].rsplit('.', 1)[0]

            os.makedirs(f"result/{data_name}/all_data", exist_ok=True)
            with open(f'result/{data_name}/all_data/{name}_cos.csv', 'w') as f:
                independence_cnt = 0
                group_cnt = 0
                # pathの名前を処理
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
            print(name, independence_cnt, independence_acc, group_cnt, group_acc)
            with open(f'result/{data_name}/{name}_acc.csv', 'w') as f:
                    print(f'independence_data数：{independence_length}', file = f)
                    print(f'independence_正解数：{independence_cnt}', file = f)
                    print(f'independence_acc：{independence_acc}', file = f)
                    print(f'group_data数：{group_length}', file = f)
                    print(f'group_正解数：{group_cnt}', file = f)
                    print(f'group_acc：{group_acc}', file = f)


if __name__ == '__main__':
    main()