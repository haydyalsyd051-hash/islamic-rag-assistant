import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="نظام أسئلة وأجوبة — كتب السيرة النبوية", page_icon="📖", layout="centered")

st.title("📖 اسأل عن السيرة النبوية")
st.caption(
    "نظام RAG يجيب فقط من محتوى كتابين: **مختصر السيرة النبوية** و**الرحيق المختوم**، "
    "مع إظهار المصادر لكل إجابة."
)

with st.sidebar:
    st.header("الإعدادات")
    backend_url = st.text_input("عنوان الـ Backend (API)", value=BACKEND_URL)
    st.markdown("---")
    if st.button("🩺 فحص حالة الخادم (Health Check)"):
        try:
            r = requests.get(f"{backend_url}/health", timeout=5)
            if r.status_code == 200:
                st.success(f"الخادم يعمل ✅  ({r.json()})")
            else:
                st.error(f"استجابة غير متوقعة: {r.status_code}")
        except requests.RequestException as e:
            st.error(f"تعذّر الاتصال بالخادم: {e}")

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("📚 المصادر"):
                for s in msg["sources"]:
                    st.markdown(f"- {s}")

question = st.chat_input("اكتب سؤالك هنا عن السيرة النبوية...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("⏳ جاري البحث في المصادر وتوليد الإجابة...")

        try:
            response = requests.post(
                f"{backend_url}/query",
                json={"question": question},
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            answer = data.get("answer", "")
            sources = data.get("sources", [])

            placeholder.markdown(answer)
            if sources:
                with st.expander("📚 المصادر"):
                    for s in sources:
                        st.markdown(f"- {s}")

            st.session_state.messages.append(
                {"role": "assistant", "content": answer, "sources": sources}
            )

        except requests.exceptions.Timeout:
            error_msg = "⏱️ انتهت مهلة الانتظار. حاول مرة أخرى."
            placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        except requests.exceptions.ConnectionError:
            error_msg = f"❌ تعذّر الاتصال بالخادم على {backend_url}. تأكد أن الـ Backend يعمل."
            placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        except requests.exceptions.HTTPError as e:
            error_msg = f"❌ خطأ من الخادم ({response.status_code}): {response.text}"
            placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        except Exception as e:  # noqa: BLE001
            error_msg = f"❌ حدث خطأ غير متوقع: {e}"
            placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
