import os
import requests
import streamlit as st

# =========================================================
# Configuration
# =========================================================

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://localhost:8000"
)

st.set_page_config(
    page_title="سِراج | المساعد الذكي للسيرة النبوية",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# Custom CSS
# =========================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 85% 5%,
                rgba(30, 120, 100, 0.10),
                transparent 30%
            ),
            radial-gradient(
                circle at 10% 20%,
                rgba(70, 90, 150, 0.08),
                transparent 25%
            ),
            #f7f9fc;
    }

    /* Main container */
    .block-container {
        max-width: 1250px;
        padding-top: 1.5rem;
        padding-bottom: 5rem;
    }

    /* Header */
    .hero {
        background: linear-gradient(
            135deg,
            #102a43 0%,
            #164e63 55%,
            #176b68 100%
        );
        padding: 2.2rem 2.5rem;
        border-radius: 24px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 12px 35px rgba(16, 42, 67, 0.18);
        direction: rtl;
        text-align: right;
        position: relative;
        overflow: hidden;
    }

    .hero:after {
        content: "﷽";
        position: absolute;
        left: 35px;
        top: 18px;
        font-size: 4rem;
        opacity: 0.10;
    }

    .hero-title {
        font-size: 2.25rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
    }

    .hero-subtitle {
        font-size: 1rem;
        opacity: 0.88;
        line-height: 1.9;
        max-width: 750px;
    }

    .status-pill {
        display: inline-block;
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.22);
        border-radius: 30px;
        padding: 0.35rem 0.9rem;
        margin-top: 1rem;
        font-size: 0.85rem;
    }

    /* Cards */
    .info-card {
        background: white;
        border: 1px solid #e8edf3;
        border-radius: 18px;
        padding: 1.2rem;
        box-shadow: 0 5px 18px rgba(16, 42, 67, 0.045);
        direction: rtl;
        text-align: right;
        height: 100%;
    }

    .info-card-icon {
        font-size: 1.7rem;
        margin-bottom: 0.4rem;
    }

    .info-card-title {
        font-size: 1rem;
        font-weight: 700;
        color: #102a43;
        margin-bottom: 0.25rem;
    }

    .info-card-text {
        color: #627d98;
        font-size: 0.85rem;
        line-height: 1.8;
    }

    /* Section headings */
    .section-title {
        color: #102a43;
        font-size: 1.15rem;
        font-weight: 800;
        margin: 1.5rem 0 0.8rem 0;
        direction: rtl;
        text-align: right;
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        border-radius: 18px;
        margin-bottom: 0.8rem;
        padding: 0.7rem;
    }

    [data-testid="stChatMessageContent"] {
        direction: rtl;
        text-align: right;
        line-height: 2;
    }

    /* Sources */
    .source-card {
        background: #f8fafc;
        border: 1px solid #e5eaf0;
        border-right: 4px solid #2f855a;
        border-radius: 10px;
        padding: 0.65rem 0.9rem;
        margin: 0.45rem 0;
        direction: rtl;
        text-align: right;
        color: #334e68;
        font-size: 0.84rem;
    }

    .source-label {
        color: #2f855a;
        font-weight: 700;
        font-size: 0.75rem;
        margin-bottom: 0.2rem;
    }

    /* Welcome box */
    .welcome-box {
        background: white;
        border: 1px solid #e5eaf0;
        border-radius: 22px;
        padding: 2rem;
        text-align: center;
        direction: rtl;
        box-shadow: 0 7px 25px rgba(16, 42, 67, 0.05);
        margin: 1.2rem 0;
    }

    .welcome-icon {
        font-size: 3.2rem;
        margin-bottom: 0.5rem;
    }

    .welcome-title {
        color: #102a43;
        font-size: 1.45rem;
        font-weight: 800;
    }

    .welcome-text {
        color: #627d98;
        line-height: 2;
        font-size: 0.95rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #102a43;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    section[data-testid="stSidebar"] .stTextInput input {
        color: #102a43 !important;
        background: white !important;
    }

    .sidebar-brand {
        text-align: center;
        direction: rtl;
        padding: 0.8rem 0 1.4rem 0;
    }

    .sidebar-brand-icon {
        font-size: 2.5rem;
    }

    .sidebar-brand-title {
        font-size: 1.35rem;
        font-weight: 800;
    }

    .sidebar-brand-subtitle {
        font-size: 0.78rem;
        opacity: 0.7;
        line-height: 1.8;
    }

    .sidebar-section {
        direction: rtl;
        text-align: right;
        font-size: 0.95rem;
        font-weight: 700;
        margin-top: 1.2rem;
        margin-bottom: 0.5rem;
    }

    .sidebar-feature {
        direction: rtl;
        text-align: right;
        font-size: 0.82rem;
        line-height: 2;
        opacity: 0.85;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-family: 'Cairo', sans-serif;
        font-weight: 600;
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        direction: rtl;
    }

    /* Hide streamlit menu/footer */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #e5eaf0;
        border-radius: 15px;
        padding: 0.7rem;
        direction: rtl;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# Session State
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "backend_url" not in st.session_state:
    st.session_state.backend_url = BACKEND_URL

# =========================================================
# Sidebar
# =========================================================

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-icon">📖</div>
            <div class="sidebar-brand-title">سِراج</div>
            <div class="sidebar-brand-subtitle">
                المساعد الذكي للسيرة النبوية
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown(
        '<div class="sidebar-section">⚙️ إعدادات الاتصال</div>',
        unsafe_allow_html=True,
    )

    backend_url = st.text_input(
        "Backend API",
        value=st.session_state.backend_url,
        label_visibility="collapsed",
        placeholder="http://localhost:8000",
    )

    st.session_state.backend_url = backend_url

    if st.button(
        "🩺 اختبار اتصال الخادم",
        use_container_width=True,
    ):
        try:
            health_response = requests.get(
                f"{backend_url}/health",
                timeout=5,
            )

            if health_response.status_code == 200:
                st.success("الخادم يعمل بنجاح")
            else:
                st.error(
                    f"الخادم أعاد Status Code: "
                    f"{health_response.status_code}"
                )

        except requests.RequestException:
            st.error("تعذر الاتصال بالـ Backend")

    st.markdown("---")

    st.markdown(
        '<div class="sidebar-section">✨ مميزات النظام</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-feature">
        ✓ إجابات باللغة العربية<br>
        ✓ يعتمد على مصادر السيرة فقط<br>
        ✓ إظهار المصادر المستخدمة<br>
        ✓ لا يستخدم المعرفة العامة<br>
        ✓ مصمم باستخدام تقنية RAG
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    if st.button(
        "🗑️ مسح المحادثة",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.rerun()

    st.markdown(
        """
        <div style="
            direction: rtl;
            text-align: center;
            opacity: 0.65;
            font-size: 0.72rem;
            margin-top: 2rem;
            line-height: 1.8;
        ">
        نظام تعليمي وتجريبي<br>
        مبني باستخدام Retrieval-Augmented Generation
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# Hero Header
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">📖 اسألني عن السيرة النبوية</div>
        <div class="hero-subtitle">
            مساعد معرفي ذكي يساعدك على استكشاف أحداث السيرة النبوية
            من خلال البحث داخل مصادر موثوقة، مع عرض المصادر المستخدمة
            لدعم كل إجابة.
        </div>
        <div class="status-pill">
            🟢 Source-Grounded Islamic RAG Assistant
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# Info Cards
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="info-card">
            <div class="info-card-icon">📚</div>
            <div class="info-card-title">مصادر محددة</div>
            <div class="info-card-text">
                يعتمد النظام على كتابي مختصر السيرة النبوية
                والرحيق المختوم فقط.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="info-card">
            <div class="info-card-icon">🔎</div>
            <div class="info-card-title">بحث ذكي</div>
            <div class="info-card-text">
                يسترجع الأجزاء الأكثر ارتباطًا بالسؤال قبل
                إنشاء الإجابة.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="info-card">
            <div class="info-card-icon">🛡️</div>
            <div class="info-card-title">إجابة موثقة</div>
            <div class="info-card-text">
                لا يعتمد على المعرفة العامة، ويعرض المصادر
                المستخدمة مع كل إجابة.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# Welcome Screen / Suggested Questions
# =========================================================

if not st.session_state.messages:
    st.markdown(
        """
        <div class="welcome-box">
            <div class="welcome-icon">🌙</div>
            <div class="welcome-title">مرحبًا بك في سِراج</div>
            <div class="welcome-text">
                اطرح سؤالك حول السيرة النبوية، وسأبحث لك داخل
                المصادر المتاحة وأعرض الإجابة مع مراجعها.
                <br>
                يمكنك البدء بأحد الأسئلة المقترحة بالأسفل.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">💡 أسئلة مقترحة للبدء</div>',
        unsafe_allow_html=True,
    )

    suggested_questions = [
        "متى وُلد النبي صلى الله عليه وسلم؟",
        "ما هي هجرة الحبشة الأولى؟",
        "ماذا حدث في غزوة بدر؟",
        "من هو النجاشي ملك الحبشة؟",
        "متى فُتحت مكة؟",
        "ما هي حادثة الإفك؟",
    ]

    question_columns = st.columns(2)

    for index, suggested_question in enumerate(suggested_questions):
        with question_columns[index % 2]:
            if st.button(
                f"💬 {suggested_question}",
                key=f"suggested_{index}",
                use_container_width=True,
            ):
                st.session_state.pending_question = suggested_question
                st.rerun()

# =========================================================
# Display Previous Messages
# =========================================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("sources"):
            with st.expander("📚 عرض المصادر المستخدمة"):
                for index, source in enumerate(
                    message["sources"],
                    start=1,
                ):
                    st.markdown(
                        f"""
                        <div class="source-card">
                            <div class="source-label">
                                المصدر {index}
                            </div>
                            {source}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

# =========================================================
# Get Question
# =========================================================

question = st.chat_input(
    "اكتب سؤالك عن السيرة النبوية هنا..."
)

# Support suggested question buttons
if "pending_question" in st.session_state:
    question = st.session_state.pending_question
    del st.session_state.pending_question

# =========================================================
# Query Backend
# =========================================================

if question:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        placeholder = st.empty()

        placeholder.markdown(
            """
            <div style="
                direction: rtl;
                text-align: right;
                color: #627d98;
                padding: 0.5rem;
            ">
            🔎 جاري البحث في المصادر...
            <br>
            🤖 جاري تجهيز إجابة موثقة...
            </div>
            """,
            unsafe_allow_html=True,
        )

        try:
            response = requests.post(
                f"{backend_url}/query",
                json={"question": question},
                timeout=60,
            )

            response.raise_for_status()

            data = response.json()

            answer = data.get(
                "answer",
                "لم يتم العثور على إجابة.",
            )

            sources = data.get("sources", [])

            placeholder.markdown(answer)

            if sources:
                with st.expander("📚 عرض المصادر المستخدمة"):
                    for index, source in enumerate(
                        sources,
                        start=1,
                    ):
                        st.markdown(
                            f"""
                            <div class="source-card">
                                <div class="source-label">
                                    المصدر {index}
                                </div>
                                {source}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                }
            )

        except requests.exceptions.Timeout:
            error_message = (
                "⏱️ استغرق الطلب وقتًا أطول من المتوقع. "
                "يرجى المحاولة مرة أخرى."
            )

            placeholder.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                }
            )

        except requests.exceptions.ConnectionError:
            error_message = (
                "❌ لا يمكن الاتصال بالخادم حاليًا. "
                "تأكد من تشغيل الـ Backend ثم حاول مرة أخرى."
            )

            placeholder.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                }
            )

        except requests.exceptions.HTTPError:
            error_message = (
                "❌ حدثت مشكلة أثناء معالجة السؤال من الخادم."
            )

            placeholder.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                }
            )

        except Exception:
            error_message = (
                "❌ حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى."
            )

            placeholder.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                }
            )