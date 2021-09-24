from collections import defaultdict
import argparse
import random
import json
import csv
from gensim.models import KeyedVectors
from data_loader import load_sudachi_synonym_dataset
from config import MODEL_PATHS
from function_create_jepair_outlier_detection_dataset import (
    remove_index_not_in_models, preprocessing, 
    create_je_pairs, create_jj_pairs, 
    create_rt_pairs, create_ra_pairs, create_ro_pairs, create_rm_pairs, 
    create_abb_je_pairs, create_abb_others_pairs
)


def name():
    # file_nameの入力
    file_name = 'add_data'
    return file_name

def main():
    random.seed(2)

    # 引数の準備
    parser = argparse.ArgumentParser(description='データと同義語数とmodelをinputする')  

    parser.add_argument('-s', '--synonym_path', help='同義語辞書の名前', default='synonyms.txt')   

    args = parser.parse_args()    #  引数を解析


    # 全データの入力
    data = load_sudachi_synonym_dataset(args.synonym_path)

    # データの前処理
    data = preprocessing(data)


    # 保存先指定
    file_name = name()
 
    # modelの読み込み
    models = []
    for model_path in MODEL_PATHS:
        model = KeyedVectors.load(model_path)
        models.append(model)


    # modelの名前を辞書化
    param = defaultdict(list)
    param.update([("model_paths", MODEL_PATHS)])
        
    # dropするデータの id 取得
    remove_index = remove_index_not_in_models(data, models)


    # model の中にはいっているものだけを抽出 
    data = data.drop(index = remove_index)

    # models の中にはいっているもので、同義語数が2もので形成されているものだけを抽出  + outlier
    je_pairs, je_outliers = create_je_pairs(data)
    jj_pairs, jj_outliers = create_jj_pairs(data)

    # models の中にはいっているもので、代表語と略語で形成されているものだけを抽出  + outlier
    # アルファベット表記：abb_je, アルファベット表記以外：abb_others
    abb_je_pairs, abb_je_outliers = create_abb_je_pairs(data)
    abb_others_pairs, abb_others_outliers = create_abb_others_pairs(data)

    # param と group_dict_je_pairs データをまとめる
    sub_je_dict = []
    for key in je_pairs:
        sub_je_dict.append({"words" : je_pairs[key], "outliers" : je_outliers[key]})
    output_je_dict = defaultdict(list)
    output_je_dict.update([("param", param), ["data", sub_je_dict]])

    # jsonファイルを作成
    with open(f'{file_name}/data_je.json', 'w') as f:
        json.dump(output_je_dict, f, indent=4, ensure_ascii=False)
    
    # param と group_dict_jj_pairs をまとめる
    sub_jj_dict = []
    for key in jj_pairs:
        sub_jj_dict.append({"words" : jj_pairs[key], "outliers" : jj_outliers[key]})
    output_jj_dict = defaultdict(list)
    output_jj_dict.update([("param", param), ["data", sub_jj_dict]])

    # jsonファイルを作成
    with open(f'{file_name}/data_jj.json', 'w') as f:
        json.dump(output_jj_dict, f, indent=4, ensure_ascii=False)

    # param とgroup_dict_abb_others_pairs をまとめる
    sub_abb_others_dict = []
    for key in abb_others_pairs:
        sub_abb_others_dict.append({"words" : abb_others_pairs[key], "outliers" : abb_others_outliers[key]})
    output_abb_others_dict = defaultdict(list)
    output_abb_others_dict.update([("param", param), ("data", sub_abb_others_dict)])

    # jsonファイルを作成
    with open(f'{file_name}/data_abb_others.json', 'w') as f:
        json.dump(output_abb_others_dict, f, indent=4, ensure_ascii=False)
 
if __name__ == '__main__':
    main()
