import streamlit as st
import plotly.express as px
from app.pages.common import hero
from src.pages_data import cohort_dataframe
from src.clustering.engagement import segment_engagement

def render(user):
    hero("Academic analytics","Explore subject, attendance, performance and academic-risk patterns.")
    df=cohort_dataframe()
    if df.empty:
        st.info("No academic records available."); return
    a,b=st.columns(2)
    with a: st.plotly_chart(px.histogram(df,x="CGPA",color="Department",title="CGPA distribution"),use_container_width=True)
    with b: st.plotly_chart(px.pie(df,names="Risk",title="Risk-band distribution"),use_container_width=True)
    st.plotly_chart(px.scatter(df,x="Attendance",y="Final_Marks",color="Risk",hover_name="Student ID",
                               title="Attendance versus final marks"),use_container_width=True)
    subject=df.melt(id_vars=["Student ID"],value_vars=["Internal_Marks","Assignment_Marks","Quiz_Marks","Final_Marks"],
                    var_name="Assessment",value_name="Marks")
    st.plotly_chart(px.box(subject,x="Assessment",y="Marks",title="Assessment score comparison"),use_container_width=True)
    st.subheader("Exploratory engagement segments")
    segments=segment_engagement(df)
    if segments is not None:
        st.caption("K-Means groups attendance, study time and assignment activity for exploration only; segments are not ability or risk labels.")
        st.dataframe(segments.reset_index(drop=True),use_container_width=True,hide_index=True)
    else:
        st.info("At least six complete student records are needed to explore engagement segments.")
    st.caption("Charts are calculated from current records. Demo data is synthetic.")
