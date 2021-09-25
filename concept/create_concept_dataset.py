from collections import defaultdict
import argparse
import random
import json
import csv
import glob
from gensim.models import KeyedVectors
import pandas as pd
import os
import itertools


def load_w2v_models(model_reg):
    models_path = glob.glob(model_reg)
    print("loading...", models_path)
    return {model_path: KeyedVectors.load(model_path) for model_path in models_path}


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
            if line[7] != "()" and "/" not in line[7]:
                ssd_data.append(line)

    sudachi_synonym_df = pd.DataFrame(ssd_data, columns=["id", "uninflected", "deployment", "numbers", "type", "information", "fluctuation", "field", "word", "9", "10"])
    return sudachi_synonym_df


def remove_index_not_in_models(df, models):
    return [index for index, row in df.iterrows()
           if any ([row.word not in model for model in models])]


def is_not_creatable(words):
    return len(words) <= 1 or (len(words) == 2 and words[0][0][0] == words[1][0][0])

def create_concept_field(df):
    pairs_by_field = [(list(itertools.combinations(row.word.values.tolist(), 2)), row.field.values.tolist()[0])
                                for index, row in df.groupby("field") if len(row) > 1]

    print(len(pairs_by_field))
    if is_not_creatable(pairs_by_field):
        raise ValueError("too few, do not create dataset")

    print("-----Sample-----")
    for pairs, field in pairs_by_field:
        print(field, pairs[:5])

    return pairs_by_field

def concat_pair_between_field(pairs_by_field):
    min_len = min([len(pairs) for pairs, field in pairs_by_field])
    print(min_len)
    align_len_pairs_by_field = [(pairs[:min_len], field) for pairs, field in pairs_by_field]
    return [{"pair":pair, "fields": [pairs_and_field[0][1], pairs_and_field[1][1]]} 
            for pairs_and_field in itertools.combinations(align_len_pairs_by_field, 2)
            for pair in itertools.product(pairs_and_field[0][0], pairs_and_field[1][0])]


def main():
    random.seed(2)

    parser = argparse.ArgumentParser(description='同義語と分散表現modelから未知語を除いたデータセットを作成')  
    parser.add_argument('-s', '--synonym_path', help='path of synonym_dict', default='../data/synonyms.txt')   
    parser.add_argument('-m', '--model_reg', help='reg of model name', default="../model/*/*.kv")   
    parser.add_argument('-o', '--output_dir', help='output dir', default="data_eval")
    args = parser.parse_args()

    model_set = load_w2v_models(args.model_reg)
    param = {"model_paths": list(model_set.keys())}
    
    syno_df = load_sudachi_synonym_dataset(args.synonym_path)
    syno_df = syno_df.drop(index=remove_index_not_in_models(syno_df, model_set.values()))

    pairs_by_field = create_concept_field(syno_df)
    pairs_between_field = concat_pair_between_field(pairs_by_field)
    print(len(pairs_between_field))
    output = {"param": param, "data": pairs_between_field}

    os.makedirs(args.output_dir, exist_ok=True)
    with open(f"{args.output_dir}/field.json", "w") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
