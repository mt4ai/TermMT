from sentence_transformers import SentenceTransformer
import torch
import logging

logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")



model = SentenceTransformer('../models/bge-base-en-v1.5')
# model = SentenceTransformer('../../models/bge-base-en-v1.5')
model.to(device)



def getSimilarity(sentences_1, sentences_2):
    # print(sentences_1)
    # print(sentences_2)
    embeddings_1 = model.encode(sentences_1, normalize_embeddings=True)
    embeddings_2 = model.encode(sentences_2, normalize_embeddings=True)
    similarity = embeddings_1 @ embeddings_2.T
    similarity = similarity[0]
    return [float(s) for s in similarity]

