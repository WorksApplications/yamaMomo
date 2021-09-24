from typing import Text
import MeCab
import time
from sudachipy import tokenizer 
from sudachipy import dictionary

def main():
 
    cnt = 0
    # 解析対象テキストファイルを開く
    f =  open("train_learning.txt",'r')
    # ファイルを読み込む
    out_file_name = "train_learning_surface_sudachi.txt"
    with open(out_file_name, 'a') as file:
        for data in f:
            # mecab = MeCab.Tagger("-Owakati")
            # text = mecab.parse(data)
            # mecab.parse('')
            # file.write(text)

            tokenizer_obj = dictionary.Dictionary().create()
            mode = tokenizer.Tokenizer.SplitMode.A
            text = [m.surface() for m in tokenizer_obj.tokenize(data, mode)]
            file.write(str(text)+"\n")
            

if __name__ == '__main__':
    main()
