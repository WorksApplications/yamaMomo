from collections import defaultdict
import argparse
import random
import json
from gensim.models import KeyedVectors
from config import MODEL_PATHS
from function_create_concept_categorization_dataset import (
    load_sudachi_synonym_dataset, preprocessing, remove_index_not_in_models, delete_field_NULL,
    create_mini_concept_set_je, create_mini_concept_set_jj,
    create_mini_concept_set_rt, create_mini_concept_set_ra, create_mini_concept_set_ro, create_mini_concept_set_rm,
    create_mini_concept_set_abb_je , create_mini_concept_set_abb_others,
    create_mini_concept_field, select_mini_concept_field
)

def name():
    # file_nameの入力
    file_name = 'sub_data'
    return file_name

def def_length_data():
    # file_nameの入力
    length_data = 10
    return length_data

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

    # # je, jj, rt, ra, ro, rm, abb_je, abb_others について
    # # models の中にはいっているもので、同義語のpairを作成
    # mini_concept_set, other_mini_concept_sets = create_mini_concept_set_abb_others(data)

    # # # param と concept_set データをまとめる
    # sub_output_concept_set = []
    # for key in mini_concept_set:
    #     sub_output_concept_set.append({"mini_concept_set" : mini_concept_set[key], "other_mini_concept_sets" : other_mini_concept_sets[key]})
    # output_concept_set = defaultdict(list)
    # output_concept_set.update([("param", param), ["data", sub_output_concept_set]])

    # # # jsonファイルを作成
    # with open(f'{file_name}/concept_set_abb_others.json', 'w') as f:
    #     json.dump(output_concept_set, f, indent=4, ensure_ascii=False)


    # fieldについて
    # (field == NULL) を drop
    data = delete_field_NULL(data)
    # print(data)
    
    print("make_data")

    # je, jj, rt, ra, ro, rm, abb_je, abb_others, field について
    # models の中にはいっているもので、同義語のpairを作成
    mini_concept_set = create_mini_concept_field(data)

    print(mini_concept_set)

    print("select_data")
    
    exit()
    # データ数を調節し組み合わせる
    mini_concept_field, length_data = select_mini_concept_field(mini_concept_set)
    # def_length_data(length_data)

    
    # パラメタとデータを組み合わせる（field）
    output_concept_set = defaultdict(list)
    output_concept_set.update([("param", param), ["data", mini_concept_field]])

    # jsonファイルを作成
    with open(f'{file_name}/concept_set_field.json', 'w') as f:
        json.dump(output_concept_set, f, indent=4, ensure_ascii=False)

    
if __name__ == '__main__':
    main()
