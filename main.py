# # Instal LIWC
# #!pip install liwc

# # Setup
# from collections import Counter
# import liwc
# import collections
# from nltk.corpus import stopwords
# import numpy as np
# import pandas as pd
# import re
# import matplotlib.pyplot as plt
# import nltk
# import warnings
# warnings.filterwarnings("ignore", category=DeprecationWarning)


# # Read text dataset
# df_train = pd.read_csv("training_data.csv")

# # Cleaning
# df_train['text'].astype(str)
# df_train['clean_text'] = df_train['text'].str.replace(
#     'http\S+|www.\S+', '', case=False)  # Removing urls
# df_train['clean_text'] = df_train['clean_text'].str.replace(
#     '[^A-Za-z0-9]+', ' ')  # Removing Punctuations, Numbers, and Special Character
# df_train['clean_text'] = df_train['clean_text'].map(
#     lambda x: x if type(x) != str else x.lower())  # lowercase
# df_train['clean_text'].dropna()  # drop NaN values


# # Tokenize and drop NaN tokens
# split_data = df_train['clean_text'].str.split(" ")
# df_train['tokens'] = split_data
# nan_value = float("NaN")
# df_train.replace("", nan_value, inplace=True)
# df_train.dropna(subset=["tokens"], inplace=True)


# # Download "LIWC2015_English.dic" in your system and read as below
# parse, category_names = liwc.load_token_parser('LIWCdic.dic')


# # LIWC Features Extraction
# liwc = []
# for item in df_train.tokens:
#     gettysburg_counts = list(collections.Counter(category for token in item for category in parse(
#         token) if category == 'family (Family)').items())
#     liwc.append(gettysburg_counts)
# liwc_ = np.array(liwc)
# df_train['family'] = liwc_

# # likewise you can get features for other categories like "achieve (Achievement)","work (Work)", "certain (Certainty)" etc
# # in the above for loop , change the "category" == "achieve (Achievement)" etc
# # import re
# # import liwc
# # from collections import Counter

# # # Função para tokenizar o texto


# # def tokenize(text):
# #     for match in re.finditer(r'\w+', text, re.UNICODE):
# #         yield match.group(0)


# # # Carregar o parser do LIWC
# # parse, category_names = liwc.load_token_parser('LIWC2007_English100131.dic')

# # # Texto de exemplo (Gettysburg Address)
# # gettysburg = '''Four score and seven years ago our fathers brought forth on
# # this continent a new nation, conceived in liberty, and dedicated to the
# # proposition that all men are created equal. Now we are engaged in a great
# # civil war, testing whether that nation, or any nation so conceived and so
# # dedicated, can long endure. We are met on a great battlefield of that war.
# # We have come to dedicate a portion of that field, as a final resting place
# # for those who here gave their lives that that nation might live. It is
# # altogether fitting and proper that we should do this.'''.lower()

# # # Tokenizar o texto
# # gettysburg_tokens = list(tokenize(gettysburg))

# # # Contar categorias do LIWC
# # gettysburg_counts = Counter(
# #     category for token in gettysburg_tokens for category in parse(token)
# # )

# # # Exibir resultados
# # print(gettysburg_counts)
