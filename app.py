import streamlit as st
import pandas as pd
import json

from graph.agent_graph import agents_graph
from tools.data_extractor_tool import run_sql
from tools.plots_render_tool import render_plotly
from tools.dashboard_builder_tool import build_dashboard_from_paths
from utils.clean_utils import clean_json

from agents.narrative_agent import run_narrative_agent
from agents.sql_feedback_agent import run_sql_feedback_agent
from agents.visualization_agent import run_visualization_agent
from agents.dashboard_agent import run_dashboard_agent
from tools.forecast_tool import run_forecast


st.set_page_config(page_title="DataGenie AI Analytics", layout="wide")
st.title("DataGenie — AI Analytics Assistant")

query = st.text_input("Enter your query")
run_btn = st.button("Run Analysis")

if run_btn and query:

    with st.spinner("Thinking..."):

        result = agents_graph.invoke({"question": query})
        validator = result["validator"]

        # st.subheader("🧠 Interpretation")
        # st.json(validator)

        # NON ANALYTICS
        if not validator.get("is_valid") or not validator.get("is_analytics"):
            st.error("❌ Not an analytics question.")
            st.stop()


        # DASHBOARD 
        if validator.get("dashboard", False):

            st.info("Dashboard request detected — building dashboard...")

            raw_dashboard = run_dashboard_agent(query)
            dashboard_questions = json.loads(clean_json(raw_dashboard))["questions"]

            chart_paths = []

            for dq in dashboard_questions:

                st.write(f"➡ Running: **{dq}**")
                sub = agents_graph.invoke({"question": dq})
                sql = sub["sql_query"]

                sql_res = run_sql(dq, sql)

                if not sql_res["success"]:
                    st.warning("Skipping (SQL failed)")
                    continue

                df = sql_res["data"]

                narrative = run_narrative_agent(dq, df)
                st.subheader("Narrative Summary")
                st.markdown(
                    f"""
                    <div style='font-size:24px; line-height:1.6;'>
                        <strong>{narrative}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    

                if sub["validator"].get("visualization", True):

                    spec = run_visualization_agent(
                        sub["validator"]["analysis_goal"],
                        df.head(2),
                        df.columns.tolist()
                    )

                    visual_json = clean_json(spec)
                    path, fig = render_plotly(df, visual_json)

                    st.plotly_chart(fig, use_container_width=True)
                    chart_paths.append(path)

            if chart_paths:
                dashboard_path = build_dashboard_from_paths(chart_paths)
                st.success("Dashboard created!")
                st.markdown(f"[Open Dashboard]({dashboard_path})", unsafe_allow_html=True)

            st.stop()

        # STANDARD QUERY
        sql = result["sql_query"]
        # st.subheader("📝 SQL Generated")
        # st.code(sql, language="sql")

        sql_result = run_sql(query, sql)

        # feedback loop
        if not sql_result["success"]:
            st.warning("SQL failed — fixing...")

            fixed_sql = run_sql_feedback_agent(
                question=sql_result["question"],
                sql=sql_result["sql"],
                error=sql_result["error"] or sql_result["reason"]
            )

            # st.code(fixed_sql, language="sql")
            sql_result = run_sql(query, fixed_sql)

            if not sql_result["success"]:
                st.error("Still failed. Stopping.")
                st.stop()

        df = sql_result["data"]

        # narrative summary
        narrative = run_narrative_agent(query, df)
        st.subheader("📝 Narrative Summary")
        st.markdown(
        f"""
        <div style='font-size:24px; line-height:1.6;'>
            <strong>{narrative}</strong>
        </div>
        """,
        unsafe_allow_html=True
        )


        # preview
        st.subheader("📄 Data Preview")
        st.dataframe(df)

        # FORECAST 
        if validator.get("requires_forecast", False):

            st.subheader("📈 Forecast")

            # expand allowed time column patterns
            time_candidates = ["date", "month", "month_start", "year", "timestamp"]

            detected_time_cols = [
                c for c in df.columns
                if any(key in c.lower() for key in time_candidates)
            ]

            if not detected_time_cols:
                st.error(
                    "⚠️ Forecasting requires a time column "
                    "(date / month / year). SQL did not return one."
                )
            else:
                time_col = detected_time_cols[0]

                st.info(f"Using **{time_col}** as time column for forecasting.")

                try:
                    forecast_df, fig = run_forecast(
                        df=df,
                        time_col=time_col,
                        value_col=validator.get("metric", "revenue"),
                        horizon=validator.get("horizon", 6),
                        granularity=validator.get("time_granularity", "month"),
                    )

                    st.dataframe(forecast_df)
                    st.plotly_chart(fig, use_container_width=True)
                    st.success("Forecasting complete!")
                except Exception as e:
                    st.warning(f"⚠️ Forecasting failed: {e}")

        # VISUALIZATION
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