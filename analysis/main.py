import MeCab
import itertools
import collections
import os
import sys

def debug(content):
    print(type(content), content)

class Analysis():
    def __init__(self, dir=u'./dic/mecab-ipadic-neologd'):
        # 辞書を選択
        # self.mecab = MeCab.Tagger(u'-d' + os.path.join(os.path.dirname(__file__), dir))
        self.mecab = MeCab.Tagger('-d ' + dir)

    def main(self, text_list):
        # 単語に分解
        words = list(map(self.slice_text, text_list))
        # print(words)
        # 二次元配列を平坦にする
        words = list(itertools.chain.from_iterable(words))
        # print(words)
        # 単語の出現回数でソート
        most_words = self.sort_most_word(words)
        # print(most_words)

        return most_words


    def slice_text(self, word):
        node = self.mecab.parseToNode(word)
        result = []
        while node:
            # 名詞のとき配列に追加
            if node.feature.split(',')[0] == '名詞':
                result.append(node.surface)
            # イテレーターを移動
            node = node.next

        return result

    def sort_most_word(self, words):
        c = collections.Counter(words)
        c = c.most_common()
        most_array = list(map(lambda x: x[0], c))

        return most_array

if __name__ == '__main__':
    # sample_text_list = ['庭には庭庭がいる', '齋藤飛鳥は俺の齋藤飛鳥', '俺の嫁！俺の嫁！']
    sample_text_list = sys.argv[1:]

    analysis = Analysis()
    result = analysis.main(sample_text_list)

    debug(result) # => ['庭', '齋藤飛鳥', '俺の嫁', '俺']