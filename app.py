import streamlit as st
import pandas as pd
from utils.data_loader import load_file
from utils.agent import create_agent, run_agent
from utils.chart_detector import maybe_render_chart
from utils.report_generator import generate_report

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DataChat",
    page_icon="📊",
    layout="wide",
)

st.title("📊 DataChat")
st.caption("Upload a CSV or Excel file and ask questions about your data in plain English.")

# ── Session state init ────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "df" not in st.session_state:
    st.session_state.df = None
if "report_text" not in st.session_state:
    st.session_state.report_text = None
if "report_pdf" not in st.session_state:
    st.session_state.report_pdf = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📁 Your Data")
    uploaded_file = st.file_uploader(
        "Upload a CSV or Excel file",
        type=["csv", "xlsx", "xls"],
    )

    if uploaded_file:
        df, error = load_file(uploaded_file)
        if error:
            st.error(f"Could not load file: {error}")
        else:
            st.session_state.df = df
            st.session_state.agent = create_agent(df)
            st.session_state.report_text = None
            st.session_state.report_pdf = None
            st.success(f"✅ Loaded {len(df):,} rows × {len(df.columns)} columns")

            st.subheader("Preview")
            st.dataframe(df.head(5), use_container_width=True)

            st.subheader("Columns")
            col_info = pd.DataFrame({
                "Column": df.columns,
                "Type": df.dtypes.astype(str).values,
            })
            st.dataframe(col_info, use_container_width=True, hide_index=True)

    if st.session_state.df is not None:
        st.divider()

        # ── Generate Report button ────────────────────────────────────────────
        if st.button("📄 Generate Full Report", use_container_width=True, type="primary"):
            with st.spinner("Analyzing your data and writing the report… this takes ~30 seconds"):
                try:
                    report_text, pdf_bytes = generate_report(st.session_state.df)
                    st.session_state.report_text = report_text
                    st.session_state.report_pdf = pdf_bytes
                    st.success("✅ Report ready!")
                except Exception as e:
                    st.error(f"Report generation failed: {e}")

        # Show download button if report is ready
        if st.session_state.report_pdf is not None:
            st.download_button(
                label="⬇️ Download PDF Report",
                data=st.session_state.report_pdf,
                file_name="datachat_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        st.divider()
        if st.button("🗑️ Clear data & chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.agent = None
            st.session_state.df = None
            st.session_state.report_text = None
            st.session_state.report_pdf = None
            st.rerun()

# ── Main area ─────────────────────────────────────────────────────────────────
if st.session_state.df is None:
    st.info("👈 Upload a file in the sidebar to get started.")
    st.stop()

# Show report preview in main area if generated
if st.session_state.report_text is not None:
    with st.expander("📄 Report Preview", expanded=True):
        st.markdown(st.session_state.report_text)
    st.divider()

# Render chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "chart" in msg and msg["chart"] is not None:
            st.plotly_chart(msg["chart"], use_container_width=True)

# Chat input
user_input = st.chat_input("Ask a question about your data…")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            response, chart = run_agent(
                agent=st.session_state.agent,
                df=st.session_state.df,
                question=user_input,
            )
        st.markdown(response)
        if chart is not None:
            st.plotly_chart(chart, use_container_width=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "chart": chart,
    })
