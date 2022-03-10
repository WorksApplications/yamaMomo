from collections import OrderedDict
import os
from gensim.models import KeyedVectors
import json
import itertools
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
import csv
import argparse
import tqdm


def main():
    parser = argparse.ArgumentParser(description='eval with outlier')
    parser.add_argument('-d', '--data_dir', help='directory containing the created data', default="data_eval")
    args = parser.parse_args()

    # ファイルの読み込み（idが文字列）
    with open(f'{args.data_dir}/field.json', 'r') as f:
        output_dict = json.load(f, object_pairs_hook=OrderedDict)
    
    models_path = output_dict["param"]["model_paths"]
    datas = output_dict["data"]

    # modelの読み込み
    print("loading...", models_path)
    models = [KeyedVectors.load(model_path) for model_path in models_path]

    # clustering
    # km = KMeans(n_clusters=2,        # クラスターの個数
    #         init='k-means++',        # セントロイドの初期値をランダムに設定  default: 'k-means++'
    #         n_init=10,               # 異なるセントロイドの初期値を用いたk-meansの実行回数 default: '10' 実行したうちもっとSSE値が小さいモデルを最終モデルとして選択
    #         max_iter=300,            # k-meansアルゴリズムの内部の最大イテレーション回数  default: '300'
    #         tol=1e-04,               # 収束と判定するための相対的な許容誤差 default: '1e-04'
    #         random_state=42)          # セントロイドの初期化に用いる乱数発生器の状態

    clt = AgglomerativeClustering(affinity='cosine',
            linkage='average', 
            n_clusters=2)

    os.makedirs("result/all_data", exist_ok=True)

    for i, model in enumerate(models):
        # pathの名前を処理
        name = models_path[i].rsplit('/', 1)[1].rsplit('.', 1)[0]
        print(name)
        cnt = 0

        with open(f'result/all_data/{name}_field_data.csv', 'w') as f:
            writer = csv.writer(f)
            for data in tqdm.tqdm(datas):
                data = list(itertools.chain.from_iterable(data["pair"]))
                X = [model[word] for word in data]
                # Z =  list(km.fit_predict(X))
                Z =  list(clt.fit_predict(X))
                res_bool = Z == [0, 0, 1, 1] or Z == [1, 1, 0, 0]
                if res_bool:
                    cnt += 1
                
                writer.writerow([data, Z, str(res_bool)[0]])

        # acc
        acc = cnt/len(datas)
        with open(f'result/{name}_field_result.csv', 'w') as result:
            result.write("data数 : "+str(len(datas))+"\n")
            result.write("正解数 : "+str(cnt)+"\n")
            print(f'acc：{acc}', file = result)

        print(f"{name}: {cnt}/{len(datas)} = {acc}")



if __name__ == '__main__':
    main()
