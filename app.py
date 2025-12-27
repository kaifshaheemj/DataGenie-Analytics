import streamlit as st
import pandas as pd
import json

from graph.agent_graph import agents_graph
from tools.data_extractor_tool import run_sql
from tools.plots_render_tool import render_plotly
from tools.dashboard_builder_tool import build_dashboard_from_paths
from utils.clean_utils import clean_json

from agents.sql_feedback_agent import run_sql_feedback_agent
from agents.visualization_agent import run_visualization_agent
from agents.dashboard_agent import run_dashboard_agent


st.set_page_config(page_title="DataGenie AI Analytics", layout="wide")

st.title("🤖 DataGenie — AI Analytics Assistant")

query = st.text_input("Enter your query")

run_btn = st.button("Run Analysis")

if run_btn and query:

    with st.spinner("Thinking..."):

        result = agents_graph.invoke({"question": query})
        validator = result["validator"]

        st.subheader("🧠 Interpretation")
        st.json(validator)

        # -------------------------
        # ❌ Non-analytics
        # -------------------------
        if not validator.get("is_valid") or not validator.get("is_analytics"):
            st.error("❌ Not an analytics question.")
            st.stop()

        # -------------------------
        # 📊 DASHBOARD MODE
        # -------------------------
        if validator.get("dashboard", False):
            st.info("📊 Dashboard request detected — building dashboard...")

            raw_dashboard = run_dashboard_agent(query)
            dashboard_questions = json.loads(clean_json(raw_dashboard))["questions"]

            st.write("Generated dashboard questions:")
            st.write(dashboard_questions)

            chart_paths = []

            for dq in dashboard_questions:

                st.write(f"➡ Running: **{dq}**")

                sub = agents_graph.invoke({"question": dq})
                sub_sql = sub["sql_query"]

                sql_res = run_sql(dq, sub_sql)

                if not sql_res["success"]:
                    st.warning("Skipping (SQL failed)")
                    continue

                df = sql_res["data"]

                if sub["validator"].get("visualization", True):

                    spec = run_visualization_agent(
                        sub["validator"]["analysis_goal"],
                        df.head(2),
                        df.columns.tolist()
                    )

                    spec_json = clean_json(spec)

                    path, fig = render_plotly(df, spec_json)

                    st.plotly_chart(fig, use_container_width=True)

                    chart_paths.append(path)

            if chart_paths:

                dashboard_path = build_dashboard_from_paths(chart_paths)

                st.success("Dashboard created!")
                st.markdown(
                    f"[Open Dashboard]({dashboard_path})",
                    unsafe_allow_html=True
                )

            st.stop()

        # -------------------------
        # STANDARD SINGLE QUERY
        # -------------------------
        sql = result["sql_query"]

        st.subheader("📝 SQL Generated")
        st.code(sql, language="sql")

        sql_result = run_sql(query, sql)

        # feedback loop
        if not sql_result["success"]:
            st.warning("SQL failed — fixing...")

            fixed_sql = run_sql_feedback_agent(
                question=sql_result["question"],
                sql=sql_result["sql"],
                error=sql_result["error"] or sql_result["reason"]
            )

            st.code(fixed_sql, language="sql")

            sql_result = run_sql(query, fixed_sql)

            if not sql_result["success"]:
                st.error("❌ Still failed. Stopping.")
                st.stop()

        df = sql_result["data"]

        st.subheader("📄 Data Preview")
        st.dataframe(df)

        if validator.get("visualization", False):

            st.subheader("📊 Visualization")

            visual = run_visualization_agent(
                validator["analysis_goal"],
                df.head(2),
                df.columns.tolist()
            )

            visual_json = clean_json(visual)

            path, fig = render_plotly(df, visual_json)

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("No visualization required.")

    st.success("✅ Analysis complete!")