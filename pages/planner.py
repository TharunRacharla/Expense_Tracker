import streamlit as st

goal_amount = st.number_input("what is its cost?",min_value=1)

emi_amount = st.number_input("Enter EMI amount", max_value=goal_amount)
installments = st.slider("amount", min_value=1, max_value=24, value=6, width=200)

total = installments*emi_amount
if total < goal_amount:
    st.progress(total/goal_amount)
elif total >= goal_amount:
    st.progress(100)
    st.write(f"Amount exceeds by {total-goal_amount}")
