from collections import OrderedDict
from gensim.models import KeyedVectors
import json
import itertools
from config import MODEL_PATHS
from sklearn.cluster import KMeans
import csv
import create_concept_categorization_dataset as cccd

def main():
    file_name = cccd.name()

    # ファイルの読み込み（idが文字列）
    with open(f'{file_name}/concept_set_field.json', 'r') as f:
        output_dict = json.load(f, object_pairs_hook=OrderedDict)

    models_path = output_dict["param"]["model_paths"]
    datas = output_dict["data"]

    # modelの読み込み
    models = []
    for model_path in MODEL_PATHS:
        model = KeyedVectors.load(model_path)
        models.append(model)

    # clustering
    km = KMeans(n_clusters=2,        # クラスターの個数
            init='k-means++',        # セントロイドの初期値をランダムに設定  default: 'k-means++'
            n_init=10,               # 異なるセントロイドの初期値を用いたk-meansの実行回数 default: '10' 実行したうちもっとSSE値が小さいモデルを最終モデルとして選択
            max_iter=300,            # k-meansアルゴリズムの内部の最大イテレーション回数  default: '300'
            tol=1e-04,               # 収束と判定するための相対的な許容誤差 default: '1e-04'
            random_state=42)          # セントロイドの初期化に用いる乱数発生器の状態

    ans = []
    cnts = []
    all_cnts = 0
    num = 0
    data_num = 0
    for model in models:
        # pathの名前を処理
        name = models_path[num]
        name = name.rsplit('/', 1)[1]
        name = name.rsplit('.', 1)[0]
        mini_ans = []
        cnt = 0
        with open(f'{file_name}/{name}_field_data.csv', 'a') as f:
            for data in datas:
                write_data = []
                data_num += 1
                kekka = "F"
                data = list(itertools.chain.from_iterable(data))
                write_data.append(data)
                X = [model[word] for word in data]
                kmeans =  km.fit_predict(X)
                write_data.append(kmeans)
                mini_ans.append(kmeans)
                if (kmeans[0] == 0 and kmeans[1] == 0 and kmeans[2] == 1 and kmeans[3] == 1) or (kmeans[0] == 1 and kmeans[1] == 1 and kmeans[2] == 0 and kmeans[3] == 0):
                    cnt += 1
                    kekka = "T"
                write_data.append(kekka)
                writer = csv.writer(f)
                writer.writerow(write_data)
        ans.append(mini_ans)
        cnts.append(cnt)
        all_cnts += cnt
        num += 1

        # acc
        acc = cnt/len(datas)
        with open(f'{file_name}/{name}_field_result.csv', 'w') as result:
            result.write("data数 : "+str(len(datas))+"\n")
            result.write("正解数 : "+str(cnt)+"\n")
            print(f'acc：{acc}', file = result)

        print(len(datas))
        print(cnt)
        print(acc)



if __name__ == '__main__':
    main()
