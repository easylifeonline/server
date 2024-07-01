import os
from transformers import DPRContextEncoder, DPRContextEncoderTokenizer, DPRQuestionEncoder, DPRQuestionEncoderTokenizer
import torch
import faiss
import numpy as np
from .models import ProductDatabase

# Set environment variable to avoid OpenMP error
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Load DPR context encoder and tokenizer
context_tokenizer = DPRContextEncoderTokenizer.from_pretrained("facebook/dpr-ctx_encoder-single-nq-base")
context_encoder = DPRContextEncoder.from_pretrained("facebook/dpr-ctx_encoder-single-nq-base")

# Load DPR question encoder and tokenizer
question_tokenizer = DPRQuestionEncoderTokenizer.from_pretrained("facebook/dpr-question_encoder-single-nq-base")
question_encoder = DPRQuestionEncoder.from_pretrained("facebook/dpr-question_encoder-single-nq-base")

# Encode product titles and descriptions
def encode_products(products):
    embeddings = []
    for product in products:
        text = f"{product.title} {product.description}"
        inputs = context_tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            embedding = context_encoder(**inputs).pooler_output.numpy()
        embeddings.append(embedding)
    embeddings = np.vstack(embeddings)
    return embeddings

# Fetch all products from the database
products = ProductDatabase.objects.all()
product_embeddings = encode_products(products)

# Index embeddings with Faiss
index = faiss.IndexFlatL2(product_embeddings.shape[1])
index.add(product_embeddings)

def retrieve_products(query, top_k=3):
    products = list(ProductDatabase.objects.all())
    top_k = min(top_k, len(products))

    inputs = question_tokenizer(query, return_tensors="pt")
    with torch.no_grad():
        query_embedding = question_encoder(**inputs).pooler_output.numpy()

    distances, indices = index.search(query_embedding, top_k)

    results_available = [products[idx] for idx in indices[0] if idx != -1 and idx < len(products)]
    
    return results_available



