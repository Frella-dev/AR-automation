# import sqlite3
# from datetime import date

# DB_NAME = "reminders.db"


# def init_db():

#     conn = sqlite3.connect(DB_NAME)

#     conn.execute("""
#     CREATE TABLE IF NOT EXISTS reminders(
#         invoice TEXT,
#         reminder_type TEXT,
#         last_sent DATE
#     )
#     """)

#     conn.commit()
#     conn.close()


# def can_send(invoice, reminder_type, days_gap):

#     conn = sqlite3.connect(DB_NAME)

#     cur = conn.cursor()

#     cur.execute(
#         "SELECT last_sent FROM reminders WHERE invoice=? AND reminder_type=?",
#         (invoice, reminder_type)
#     )

#     row = cur.fetchone()

#     conn.close()

#     if row is None:
#         return True

#     last_sent = date.fromisoformat(row[0])

#     diff = (date.today() - last_sent).days

#     return diff >= days_gap


# def mark_sent(invoice, reminder_type):

#     conn = sqlite3.connect(DB_NAME)

#     conn.execute(
#         """
#         INSERT OR REPLACE INTO reminders(invoice, reminder_type, last_sent)
#         VALUES (?, ?, ?)
#         """,
#         (invoice, reminder_type, date.today())
#     )

#     conn.commit()
#     conn.close()

import sqlite3
from datetime import date

DB_NAME = "reminders.db"


# ---------------------------
# INIT DB
# ---------------------------
def init_db():

    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS reminders(
        invoice TEXT,
        reminder_type TEXT,
        last_sent DATE,
        PRIMARY KEY (invoice, reminder_type)
    )
    """)

    conn.commit()
    conn.close()


# ---------------------------
# CHECK IF CAN SEND
# ---------------------------
def can_send(invoice, reminder_type, days_gap):
    """
    Returns True if reminder can be sent.
    Logic:
    - If never sent → allow
    - If sent before → check days gap
    """

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "SELECT last_sent FROM reminders WHERE invoice=? AND reminder_type=?",
        (invoice, reminder_type)
    )

    row = cur.fetchone()
    conn.close()

    # Never sent before
    if row is None:
        return True

    last_sent = date.fromisoformat(row[0])
    diff = (date.today() - last_sent).days

    return diff >= days_gap


# ---------------------------
# MARK AS SENT
# ---------------------------
def mark_sent(invoice, reminder_type):
    """
    Save/update last sent date
    """

    conn = sqlite3.connect(DB_NAME)

    conn.execute(
        """
        INSERT OR REPLACE INTO reminders(invoice, reminder_type, last_sent)
        VALUES (?, ?, ?)
        """,
        (invoice, reminder_type, date.today())
    )

    conn.commit()
    conn.close()


# ---------------------------
# GET LAST SENT DATE (FOR UI)
# ---------------------------
def get_last_sent(invoice, reminder_type):
    """
    Returns last sent date (string) or None
    """

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "SELECT last_sent FROM reminders WHERE invoice=? AND reminder_type=?",
        (invoice, reminder_type)
    )

    row = cur.fetchone()
    conn.close()

    return row[0] if row else None