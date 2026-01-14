import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Loan Management System", layout="wide")
st.title("🏦 AI-Powered Loan Management System")

# ---------------- SESSION STATE INIT ----------------
if "loan_records" not in st.session_state:
    st.session_state.loan_records = []

# ---------------- MAIN NAVIGATION ----------------
choice = st.radio(
    "What would you like to do?",
    ["🏠 Home", "🆕 Apply for New Loan", "📑 Application Summary", "📄 Check Existing Loan"],
    horizontal=True
)

# ================= HOME =================
if choice == "🏠 Home":
    st.subheader("Welcome 👋")
    st.info(
        "AI-driven loan system for gig & informal workers.\n"
        "• Adaptive EMI\n"
        "• Risk-based lending\n"
        "• Multiple borrower management"
    )

# ================= APPLY FOR NEW LOAN =================
if choice == "🆕 Apply for New Loan":
    st.header("🆕 Apply for a New Loan")

    st.subheader("👤 Personal Details")
    name = st.text_input("Full Name")
    age = st.number_input("Age", 18, 100)
    occupation = st.text_input("Occupation")
    bank = st.text_input("Bank Name")
    cibil = st.number_input("CIBIL Score", 300, 900)

    st.subheader("💰 Income Details")
    prev_income = st.number_input("Previous Month Income (₹)", min_value=0)
    curr_income = st.number_input("Current Month Income (₹)", min_value=0)
    exp_income = st.number_input("Expected Next Month Income (₹)", min_value=0)

    avg_income = (prev_income + curr_income + exp_income) / 3
    st.metric("Average Income", f"₹{avg_income:.2f}")

    st.subheader("📉 Expenses & Duration")
    expenses = st.number_input("Monthly Expenses (₹)", min_value=0)
    duration = st.slider("Loan Duration (Months)", 6, 36, 12)

    repayment_capacity = max(avg_income - expenses, 0)

    if avg_income < 10000 or cibil < 600:
        risk = "High Risk 🔴"
    elif avg_income < 20000 or cibil < 700:
        risk = "Medium Risk 🟠"
    else:
        risk = "Low Risk 🟢"

    st.subheader("⚙️ EMI Configuration")
    emi_percent = st.slider("EMI as % of Income", 10, 30, 20)
    emi = avg_income * emi_percent / 100

    loan_options = {
        "Personal Loan": repayment_capacity * duration * 0.9,
        "Micro Business Loan": repayment_capacity * duration * 1.2,
        "Emergency Credit Line": repayment_capacity * duration * 0.6
    }

    loan_type = st.selectbox("Loan Type", loan_options.keys())
    loan_amount = loan_options[loan_type]

    if st.button("✅ Submit Loan Application"):
        st.session_state.loan_records.append({
            "Name": name,
            "Age": age,
            "Occupation": occupation,
            "Bank": bank,
            "CIBIL": cibil,
            "Average Income": avg_income,
            "Expenses": expenses,
            "Risk": risk,
            "Loan Type": loan_type,
            "Loan Amount": loan_amount,
            "EMI": emi,
            "Duration": duration,
            "Applied On": datetime.now().strftime("%d %b %Y")
        })

        st.success("🎉 Loan Application Saved Successfully!")
        st.rerun()

# ================= APPLICATION SUMMARY =================
if choice == "📑 Application Summary":
    st.header("📑 All Loan Applications")

    if not st.session_state.loan_records:
        st.warning("No loan applications found.")
    else:
        df = pd.DataFrame(st.session_state.loan_records)
        st.dataframe(df)

# ================= EXISTING LOAN (MULTI USER) =================
if choice == "📄 Check Existing Loan":
    st.header("📄 Existing Loan Management")

    if not st.session_state.loan_records:
        st.warning("⚠️ No existing loans found.")
    else:
        borrower_names = [
            f"{i+1}. {loan['Name']} ({loan['Loan Type']})"
            for i, loan in enumerate(st.session_state.loan_records)
        ]

        selected = st.selectbox(
            "Select Borrower",
            borrower_names
        )

        index = borrower_names.index(selected)
        data = st.session_state.loan_records[index]

        st.subheader("🏦 Loan Details")
        st.write(f"**Borrower:** {data['Name']}")
        st.write(f"**Bank:** {data['Bank']}")
        st.write(f"**Loan Type:** {data['Loan Type']}")
        st.write(f"**Total Loan:** ₹{data['Loan Amount']:.2f}")
        st.write(f"**Risk Level:** {data['Risk']}")

        current_emi = int(data["EMI"])
        total_loan = int(data["Loan Amount"])
        months = data["Duration"]

        st.subheader("🔧 Adjust EMI")
        new_emi = st.slider(
            "Adaptive EMI",
            int(current_emi * 0.5),
            int(current_emi * 1.3),
            current_emi
        )

        balance = total_loan
        schedule = []

        for m in range(1, months + 1):
            balance = max(balance - new_emi, 0)
            schedule.append([m, new_emi, balance])

        df = pd.DataFrame(
            schedule,
            columns=["Month", "EMI Paid (₹)", "Remaining Balance (₹)"]
        )

        st.subheader("📊 Repayment Schedule")
        st.table(df.head(12))

        fig, ax = plt.subplots()
        ax.plot(df["Month"], df["Remaining Balance (₹)"], marker="o")
        ax.set_title("Loan Balance Over Time")
        st.pyplot(fig)

        st.success("✅ Loan loaded successfully.")
