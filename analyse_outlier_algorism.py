import csv
from collections import defaultdict
import csv
from gensim.models import KeyedVectors
from config import MODEL_PATHS
import create_outlier_detection_dataset as codd
import pandas as pd
from gensim.models import KeyedVectors, Word2Vec
import gensim

def main():

    
    _model = KeyedVectors.load_word2vec_format("cc.ja.300.vec")
    _model.save("cc.ja.300.kv") 
    model = KeyedVectors.load("cc.ja.300.kv")

    # # 保存先指定
    # file_name = codd.name()
 
    # # modelの読み込み
    # model = KeyedVectors.load("model/chive-1.0-mc5_gensim/chive-1.0-mc5.kv"