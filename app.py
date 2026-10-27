

from datetime import datetime
import pandas as pd
import streamlit as st

from mailer import send_mail
from odoo_api import get_outstanding_invoices
from reminder_db import init_db, can_send, mark_sent, get_last_sent
from reminder_logic import should_send_upcoming_reminder

# ---------------------------
# INIT
# ---------------------------
init_db()

st.title("Outstanding Invoice Reminder System")

# ---------------------------
# LOAD DATA
# ---------------------------
try:
    data = get_outstanding_invoices()
except Exception as exc:
    st.error(f"Failed to load invoices from Odoo: {exc}")
    st.stop()

df = pd.DataFrame(data)

# ---------------------------
# CLEAN
# ---------------------------
df["customer"] = df["partner_id"].apply(
    lambda x: x[1] if isinstance(x, (list, tuple)) else ""
)

df = df.drop(columns=["partner_id"])

df["amount_residual"] = pd.to_numeric(df["amount_residual"])
df["invoice_date_due"] = pd.to_datetime(df["invoice_date_due"]).dt.date

today = datetime.today().date()

df = df[df["amount_residual"] > 0]

# ---------------------------
# CALCULATE
# ---------------------------
df["days_overdue"] = (today - df["invoice_date_due"]).apply(lambda x: x.days)
df["days_to_due"] = (df["invoice_date_due"] - today).apply(lambda x: x.days)

# ---------------------------
# SPLIT
# ---------------------------
overdue_df = df[df["days_overdue"] > 0]
upcoming_14_df = df[df["days_to_due"] == 14]

# ---------------------------
# GROUP OVERDUE (CUSTOMER)
# ---------------------------
overdue_customers = overdue_df.groupby("customer").agg({
    "amount_residual": "sum",
    "name": lambda x: list(x),
    "invoice_date_due": lambda x: list(x),
    "days_overdue": "max"
}).reset_index()

# ---------------------------
# UI TABS
# ---------------------------
tab1, tab2 = st.tabs(["Overdue Customers", "14 Days Before Due"])

# ======================================================
# 🔴 OVERDUE (DB CONTROLLED)
# ======================================================
with tab1:

    st.subheader("Overdue Customers")

    if overdue_customers.empty:
        st.success("No overdue customers 🎉")

    for i, row in overdue_customers.iterrows():

        st.markdown("---")
        st.subheader(f"Customer: {row['customer']}")

        st.write(f"Total Outstanding: {row['amount_residual']:,.2f}")

        st.write("Invoices:")
        for inv, due in zip(row["name"], row["invoice_date_due"]):
            st.write(f"- {inv} | Due: {due}")

        # ---------------------------
        # STATUS (IMPORTANT)
        # ---------------------------
        last_sent = get_last_sent(row["customer"], "overdue")

        if can_send(row["customer"], "overdue", 3):
            st.success("Ready to send ✅")
        else:
            st.warning(f"Already sent recently ⚠️ (Last: {last_sent})")

        # ---------------------------
        # EMAIL INPUT
        # ---------------------------
        email = st.text_input(
            f"Email - {row['customer']}",
            key=f"o_email{i}"
        )

        invoice_lines = "\n".join(
            [f"- {inv} | Due: {due}" for inv, due in zip(row["name"], row["invoice_date_due"])]
        )

        subject = f"Overdue Outstanding - {row['customer']}"

        body = f"""
Dear Finance Team,

This is a gentle reminder to kindly arrange the settlement of the outstanding amount at your earliest convenience.

Total Outstanding: {row['amount_residual']:,.2f}

Invoices:
{invoice_lines}

Timely payment will help us ensure smooth operations and continue the trust and support extended through your credit facility.
Could you please confirm the expected payment date for this invoice?

Regards,
Malshi Bhagya,
Finance Department,
Frella International PVT LTD
+94768578248
"""

        st.text_area("Draft Email", body, key=f"o_body{i}")

        # ---------------------------
        # SEND BUTTON
        # ---------------------------
        if st.button(f"Send Overdue - {row['customer']}", key=f"o_btn{i}"):

            if not email:
                st.warning("Enter email")
                continue

            if can_send(row["customer"], "overdue", 3):

                try:
                    send_mail(email, subject, body)
                    mark_sent(row["customer"], "overdue")
                    st.success("Reminder sent ✅")

                except Exception as e:
                    st.error(f"Error: {e}")

            else:
                st.warning("Already sent within last 3 days ⚠️")

# ======================================================
# 🟡 UPCOMING 14 DAYS (INVOICE LEVEL)
# ======================================================
with tab2:

    st.subheader("Invoices Due in 14 Days")

    if upcoming_14_df.empty:
        st.success("No invoices due in 14 days 🎉")

    for i, row in upcoming_14_df.iterrows():

        st.markdown("---")
        st.subheader(f"Invoice: {row['name']}")

        st.write(f"Customer: {row['customer']}")
        st.write(f"Due Date: {row['invoice_date_due']}")
        st.write(f"Amount: {row['amount_residual']:,.2f}")

        # ---------------------------
        # STATUS
        # ---------------------------
        last_sent = get_last_sent(row["name"], "upcoming_14")

        if can_send(row["name"], "upcoming_14", 999):
            st.success("Ready to send ✅")
        else:
            st.warning(f"Already sent ⚠️ (Last: {last_sent})")

        # ---------------------------
        # EMAIL INPUT
        # ---------------------------
        email = st.text_input(
            f"Email - {row['name']}",
            key=f"u_email{i}"
        )

        subject = f"Upcoming Invoice Reminder - {row['name']}"

        body = f"""
Dear Finance Team,

This is a reminder that the following invoice will be due in 14 days.

Invoice: {row['name']}
Due Date: {row['invoice_date_due']}
Amount: {row['amount_residual']:,.2f}

Please arrange payment before due date. Could you please confirm the expected payment date for these invoices?

Regards,
Malshi Bhagya,
Finance Department,
Frella International PVT LTD
+94768578248
"""

        st.text_area("Draft Email", body, key=f"u_body{i}")

        # ---------------------------
        # SEND BUTTON
        # ---------------------------
        if st.button(f"Send Reminder - {row['name']}", key=f"u_btn{i}"):

            if not email:
                st.warning("Enter email")
                continue

            if can_send(row["name"], "upcoming_14", 999):

                send_mail(email, subject, body)
                mark_sent(row["name"], "upcoming_14")
                st.success("Reminder sent ✅")

            else:
                st.warning("Already sent for this invoice ⚠️")