import streamlit as st
from pathlib import Path
from brief_evaluator.cli import build_default_pipeline

st.set_page_config(page_title="Оценка брифов", layout="wide")
st.title("🧠 ИИ-ассистент оценки брифов")

uploaded_file = st.file_uploader("Загрузите файл с брифом (.txt)", type=["txt"])

if uploaded_file is not None:
    brief_text = uploaded_file.read().decode("utf-8")
    st.text_area("Содержимое брифа", brief_text, height=200)

    if st.button("Оценить проект"):
        with st.spinner("Выполняется анализ..."):
            pipeline = build_default_pipeline()
            result = pipeline.run(brief_text)

        st.subheader("📊 Результат оценки")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Общий балл", f"{result.evaluation.overall_score:.2f}")
            st.metric("Статус", "✅ Пройдено" if result.evaluation.passed else "❌ Не пройдено")
        with col2:
            st.metric("Количество вопросов", len(result.questions))
            st.metric("MVP", result.mvp.title)

        st.subheader("📋 Детальная оценка")
        for score in result.evaluation.scores:
            st.write(f"**{score.criterion_name}**: {score.score:.0%} – {score.comment}")

        st.subheader("❓ Уточняющие вопросы")
        for q in result.questions:
            st.write(f"- {q.text}")

        st.subheader("🚀 Предложение MVP")
        st.write(result.mvp.description)
        st.write("**Ключевые функции:**")
        for f in result.mvp.features:
            st.write(f"- {f}")

        st.subheader("✉️ Черновик ответа заказчику")
        st.text_area("Письмо", result.formatted_text, height=300)