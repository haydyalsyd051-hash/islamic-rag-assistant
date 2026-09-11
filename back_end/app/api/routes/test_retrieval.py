# test_retrieval.py

from pathlib import Path

from app.services.vector_store import HybridVectorStore


store = HybridVectorStore(
    vector_store_dir=Path("data/faiss"),
    docs_pickle_path=Path("data/all_docs.pkl"),
    embedding_model_name="intfloat/multilingual-e5-base",
)

store.load()

questions = [
    "ما هي غزوة الأحزاب؟",
    "كم عدد الغزوات التي شارك فيها النبي بنفسه؟",
    "لماذا هاجر المسلمون إلى الحبشة؟",
    "صلاة الفجر كام ركعة؟",
]

for question in questions:
    print("\n" + "=" * 80)
    print("QUESTION:", question)
    print("=" * 80)

    results = store.retrieve(question, k=6)

    for i, item in enumerate(results, 1):
        print(f"\n--- RESULT {i} ---")
        print("METADATA:", item["metadata"])
        print("TEXT:")
        print(item["text"][:1000])