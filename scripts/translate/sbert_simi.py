from sentence_transformers import SentenceTransformer
import torch
import logging

# logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")



model = SentenceTransformer('../../models/paraphrase-multilingual-mpnet-base-v2')
model.to(device)


# compair the first sentence in sentences_1 with sentences in sentences_2
def getSimilarity(sentences_1, sentences_2):
    # print(sentences_1)
    # print(sentences_2)
    embeddings_1 = model.encode(sentences_1, normalize_embeddings=True)
    embeddings_2 = model.encode(sentences_2, normalize_embeddings=True)
    similarity = embeddings_1 @ embeddings_2.T
    return similarity

# sentence1 = "猫不在垫子上。"
# sentence2 = "猫在垫子上。"
# print(getSimilarity(sentence1, sentence2))