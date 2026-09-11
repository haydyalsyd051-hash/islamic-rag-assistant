def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_with_valid_question_returns_answer_and_sources(client):
    response = client.post("/query", json={"question": "من هم ملوك اليمن قبل الإسلام؟"})
    assert response.status_code == 200
    body = response.json()
    assert "answer" in body
    assert "sources" in body
    assert isinstance(body["answer"], str)
    assert isinstance(body["sources"], list)


def test_query_with_invalid_payload_returns_422(client):
    # إرسال جسم بدون حقل "question" المطلوب -> يجب أن يرجع FastAPI خطأ التحقق 422
    response = client.post("/query", json={"wrong_field": "hello"})
    assert response.status_code == 422


def test_query_with_empty_question_returns_422(client):
    # question فارغ ينتهك min_length=1 في الـ schema
    response = client.post("/query", json={"question": ""})
    assert response.status_code == 422
