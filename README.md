# yamaMomo
yamaMomoは [Sudachi同義語辞書](https://github.com/WorksApplications/SudachiDict/blob/develop/docs/synonyms.md) を用いて分散表現の評価を行うためのソースコードです。

ここでは以下を評価しています。
- 表記揺れ情報を基に異表記、翻字、略称の関係を同義関係として学習できているか(Outlier Word Detection)
- 分野情報を基に各分野間でクラスターが形成されているか(Concept Categorization)

## 使用方法

### install
```
git clone https://github.com/WorksApplications/yamaMomo.git
cd yamaMomo
```
評価したい分散表現のモデルは適当なディレクトリを作ってまとめてください。

この例ではmodelを作ってその下にモデルが置いてある前提となります。

### Outlier Word Detectionの評価を行う場合
```
cd outlier
python create_outlier_dataset.py -m "../model/*/*.kv" && python evaluate_outlier_detection.py
```

### Concept Categorizationの評価を行う場合
```
cd concept
python create_concept_dataset.py -m "../model/*/*.kv" && python evaluate_concept_categorization_dataset.py
```

`create_*_dataset.py`
- `-s`: Sudachi同義語辞書を指定（ [最新版](https://github.com/WorksApplications/SudachiDict/blob/develop/src/main/text/synonyms.txt) を使いたい場合はダウンロードしてそちらを指定してください。）
- `-m`: 分散表現のモデルを指定
- `-o`: 出力ディレクトリを指定

`evaluate_*_detection.py`
- `-d`: create_*_dataset.pyの出力ディレクトリを指定

例ではmodelディレクトリ下にある [KeyedVectors](https://radimrehurek.com/gensim/models/keyedvectors.html) 形式のモデルを対象としています。
入力されるモデルは、gensimの`txt`及び`kv`フォーマットを想定しています。


## 実験結果
- 野口夏希, 勝田哲弘, 山村崇, 高岡一馬, 内田佳孝, yamaMomo : Sudachi同義語辞書による日本語分散表現の評価用データセットの作成. 言語処理学会第28回年次大会, 2022.

上記の発表における実験結果は [data](./data/) から確認できます。
実験に使用したSudachi同義語辞書のデータ及びその実験結果があります。
- data
  - ConceptCategorization
  - OutlierWordDetection
    - abbj: 略称
    - je: 翻字
    - jj: 異表記
  - synonyms.txt: Sudachi同義語辞書（2021/09/22時点の最新版）

## ライセンス
[Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0)の下で[株式会社ワークスアプリケーションズ](https://www.worksap.co.jp/)によって提供されています。

## yamaMomoの引用
yamaMomoについての論文を発表しています。
- 野口夏希, 勝田哲弘, 山村崇, 高岡一馬, 内田佳孝, yamaMomo : Sudachi同義語辞書による日本語分散表現の評価用データセットの作成. 言語処理学会第28回年次大会, 2022.

yamaMomoを論文や書籍、サービスなどで引用される際には、以下のBibTexをご利用ください。

```
@INPROCEEDINGS{noguchi2022yamamomo,
    author    = {野口夏希, 勝田哲弘, 山村崇, 高岡一馬, 内田佳孝},
    title     = {yamaMomo : Sudachi同義語辞書による日本語分散表現の評価用データセットの作成},
    booktitle = "言語処理学会第28回年次大会(NLP2022)",
    year      = "2022",
    pages     = "970-975",
    publisher = "言語処理学会",
}
```