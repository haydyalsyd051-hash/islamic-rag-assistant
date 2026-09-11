"""
Backend loader - run this in your API/backend code, NOT in the notebook.
Loads the persisted FAISS index and documents without re-running
PDF loading, cleaning, chunking, or embedding.
"""

import pickle

from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.embeddings import HuggingFaceEmbeddings


VECTOR_STORE_PATH = r"C:\Users\DELL\OneDrive\Desktop\rag-assistant-project\data\processed\faiss_index"
DOCS_PATH = r"C:\Users\DELL\OneDrive\Desktop\rag-assistant-project\data\processed\all_docs.pkl"


# --- Recreate the same embedding class used at index-build time ---
# NOTE: this class definition must be IDENTICAL to the one used when
# building the index (same query/passage prefixes), otherwise similarity
# search results will be inconsistent.
class E5Embeddings(HuggingFaceEmbeddings):
    def embed_documents(self, texts):
        texts = [f"passage: {text}" for text in texts]
        return super().embed_documents(texts)

    def embed_query(self, text):
        text = f"query: {text}"
        return super().embed_query(text)


embedding_model = E5Embeddings(
    model_name="intfloat/multilingual-e5-base",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

# --- Load FAISS index from disk (no re-embedding needed) ---
vector_store = FAISS.load_local(
    VECTOR_STORE_PATH,
    embeddings=embedding_model,
    allow_dangerous_deserialization=True,  # required by LangChain for local pickle-based loads
)
print(f"FAISS index loaded: {vector_store.index.ntotal:,} vectors")

# --- Load documents (needed to rebuild BM25, which has no native save/load) ---
with open(DOCS_PATH, "rb") as f:
    all_docs = pickle.load(f)
print(f"Documents loaded: {len(all_docs):,}")

# --- Rebuild retrievers (BM25 has no persistence API, so it's rebuilt from all_docs - this is fast) ---
bm25_retriever = BM25Retriever.from_documents(all_docs)
bm25_retriever.k = 8

vector_retriever = vector_store.as_retriever(search_kwargs={"k": 8})

hybrid_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.45, 0.55],
)


def retrieve(question: str, k: int = 6):
    internal_k = max(k, 8)
    bm25_retriever.k = internal_k
    vector_retriever.search_kwargs["k"] = internal_k
    results = hybrid_retriever.invoke(question)
    return results[:k]


if __name__ == "__main__":
    results = retrieve("متى فُتحت مكة؟", k=6)
    for doc in results:
        print(doc.metadata.get("source"), doc.metadata.get("page"))
