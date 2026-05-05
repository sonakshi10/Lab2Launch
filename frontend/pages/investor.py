import streamlit as st

def investor_page():
    st.title("Investor Workspace")

    st.subheader("Find Projects to Fund")
    st.caption("Search for projects that match your investment interests.")

    query = st.text_input("Search by domain, problem, or keyword")

    if st.button("Find Opportunities"):
        st.success("Search executed")
        st.write("Matching projects will appear here")