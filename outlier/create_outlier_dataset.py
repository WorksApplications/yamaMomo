from collections import defaultdict
import argparse
import random
import json
import csv
import glob
from gensim.models import KeyedVectors
import pandas as pd
import os


def load_w2v_model(model_path):
    if model_path.split(".")[-1] == "txt":
        model = KeyedVectors.load_word2vec_format(model_path)
    else:
        model = KeyedVectors.load(model_path)
    return model

def load_w2v_models(model_reg):
    models_path = glob.glob(model_reg)
    print("loading...", models_path)
    return {model_path: load_w2v_model(model_path) for model_path in models_path}


def load_sudachi_synonym_dataset(sudachi_synonym_path):
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
    ssd_data = []
    
    with open(sudachi_synonym_path) as f:
        for line in csv.reader(f):
            # print(line)
            if len(line) <= 1:
                continue
            if "/" in line[3]:
                for n in line[3].split("/"):
                    line[3] = n
                    ssd_data.append(line[:])
            else:
                ssd_data.append(line)

    sudachi_synonym_df = pd.DataFrame(ssd_data, columns=["id", "uninflected", "deployment", "numbers", "type", "information", "fluctuation", "field", "word", "9", "10"])
    return sudachi_synonym_df


def remove_index_not_in_models(df, models):
    return [index for index, row in df.iterrows()
           if any ([row.word not in model for model in models])]


def is_not_creatable(gid, words):
    return len(gid) <= 1 or (len(gid) == 2 and words[0][0] == words[1][0])

def create_outliers(df, rel, rel_num):
    print(f"create outliers... {rel}:{rel_num}")

    syno_relations = ["type", "information", "fluctuation"] 
    syno_relations.remove(rel)
    pairs = defaultdict(list)
    for index, row in df.groupby(["id", "numbers"] + syno_relations):
        if len(row) > 1:
            gid = row["id"].values.tolist()[0]
            orig_words = []
            other_words = []
            for sub_index, sub_row in row.iterrows():
                if int(sub_row[rel]) == 0:
                    orig_words.append(sub_row.word)
                if int(sub_row[rel]) == rel_num:
                    other_words.append(sub_row.word)
            for orig_word in orig_words:
                for other_word in other_words:
                    pairs[gid].append([orig_word, other_word])
    all_gid = set(pairs.keys())

    print(len(all_gid), len(pairs.values()))
    if is_not_creatable(all_gid, pairs.values()):
        raise ValueError("too few, do not create dataset")

    outliers_num = 10
    outliers = [[random.choice(random.choice(pairs[gid_outlier]))
                for gid_outlier in random.sample(list(all_gid - {gid}), outliers_num)]
                for gid in pairs.keys()]

    print("-----Sample-----")
    for s, o in zip(pairs.values(), outliers[:10]):
        print(s, o)
    print()
    
    return pairs, outliers

def main():
    random.seed(2)

    parser = argparse.ArgumentParser(description='同義語と分散表現modelから未知語を除いたデータセットを作成')  
    parser.add_argument('-s', '--synonym_path', help='path of synonym_dict', default='../data/synonyms.txt')   
    parser.add_argument('-m', '--model_reg', help='regular expressions of model path', default="../model/*/*.kv")   
    parser.add_argument('-o', '--output_dir', help='output directory', default="data_eval")
    args = parser.parse_args()

    model_set = load_w2v_models(args.model_reg)
    param = {"model_paths": list(model_set.keys())}
    
    syno_df = load_sudachi_synonym_dataset(args.synonym_path)
    syno_df = syno_df.drop(index=remove_index_not_in_models(syno_df, model_set.values()))


    ex_setting = {"je": ("fluctuation", 1), "jj": ("fluctuation", 2), "abbj": ("information", 2)}
    for key, value in ex_setting.items():
        syno_pairs_by_group, outliers = create_outliers(syno_df, *value)
        outlier_dataset = [{"synos": syno_pair, "outliers": outlier} for syno_pairs, outlier in zip(syno_pairs_by_group.values(), outliers) for syno_pair in syno_pairs]
        output = {"param": param, "data": outlier_dataset}

        os.makedirs(args.output_dir, exist_ok=True)
        with open(f"{args.output_dir}/{key}.json", "w") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
