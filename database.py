# ============================================================
# database.py
# קובץ זה אחראי על כל התקשורת מול בסיס הנתונים SQLite
# הוא מכיל: פתיחת חיבור, יצירת טבלאות, והפונקציות לביצוע
# פעולות CRUD (Create, Read, Update, Delete) על כל אחת מהטבלאות
# ============================================================

import sqlite3          # ספריית פייתון המובנית לעבודה עם SQLite
import re                # לצורך בדיקת פורמט תאריך תקין (YYYY-MM-DD)
from pathlib import Path  # לניהול נתיב קובץ ה-DB בצורה בטוחה
from datetime import date  # לקבלת תאריך "היום" כברירת מחדל בתצוגת תפוסה

# תבנית regex לבדיקת פורמט תאריך YYYY-MM-DD (לדוגמה: 2026-09-01)
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# שם קובץ בסיס הנתונים - ייווצר אוטומטית בתיקיית הפרויקט בהרצה ראשונה
DB_FILE = Path(__file__).parent / "hotel.db"


def get_connection():
    # פונקציה שמחזירה חיבור (connection) לבסיס הנתונים
    # check_same_thread=False מאפשר שימוש נוח יותר אם נרחיב בעתיד
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")  # מפעיל אכיפת מפתחות זרים ב-SQLite
    return conn


def create_tables():
    # פונקציה שיוצרת את כל הטבלאות לפי קובץ schema.sql
    # הקריאה מהקובץ מבטיחה מקור אמת אחד למבנה ה-DB
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = get_connection()
    conn.executescript(schema_sql)  # מריץ את כל פקודות ה-SQL בקובץ בבת אחת
    conn.commit()
    conn.close()
    print("✅ הטבלאות נוצרו בהצלחה בקובץ:", DB_FILE)


# ============================================================
# --------------------- GUESTS (אורחים) ---------------------
# ============================================================

def add_guest(full_name, phone=None, email=None, address=None):
    # מוסיף אורח חדש לטבלת guests ומחזיר את ה-id שנוצר
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO guests (full_name, phone, email, address) VALUES (?, ?, ?, ?)",
        (full_name, phone, email, address)
    )
    conn.commit()
    new_id = cursor.lastrowid  # מזהה השורה החדשה שנוספה
    conn.close()
    return new_id


def get_all_guests():
    # מחזיר רשימה של כל האורחים בטבלה
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT guest_id, full_name, phone, email, address FROM guests")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_guest_by_id(guest_id):
    # מחזיר אורח בודד לפי מזהה, או None אם לא נמצא
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT guest_id, full_name, phone, email, address FROM guests WHERE guest_id = ?", (guest_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def find_guest_by_phone(phone):
    # מחפש אורח קיים לפי מספר טלפון - משמש למניעת יצירת כפילויות
    # מחזיר (guest_id, full_name) אם נמצא, אחרת None
    if not phone:
        return None
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT guest_id, full_name FROM guests WHERE phone = ?", (phone,))
    row = cursor.fetchone()
    conn.close()
    return row


def find_guest_by_contact(contact):
    # מחפש אורח קיים לפי טלפון או אימייל - זהו הזיהוי ה"טבעי" מבחינת הלקוח
    # (הלקוח לא מכיר ולא אמור להכיר מזהה פנימי של המערכת)
    # מחזיר (guest_id, full_name, phone, email) אם נמצא, אחרת None
    if not contact:
        return None
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT guest_id, full_name, phone, email FROM guests WHERE phone = ? OR email = ?",
        (contact, contact)
    )
    row = cursor.fetchone()
    conn.close()
    return row


def get_guests_with_reservations():
    # מחזיר את כל האורחים יחד עם ההזמנות שלהם (חדר + תאריכים + סטטוס)
    # זו התצוגה השימושית: "מי האורח" תמיד מוצג יחד עם "מה הוא הזמין"
    # LEFT JOIN כדי שגם אורח בלי אף הזמנה (מקרה קצה) עדיין יופיע ברשימה
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT g.full_name, g.phone, g.email,
               ro.room_number, r.check_in_date, r.check_out_date, r.status
        FROM guests g
        LEFT JOIN reservations r ON r.guest_id = g.guest_id AND r.status != 'cancelled'
        LEFT JOIN rooms ro ON ro.room_id = r.room_id
        ORDER BY g.full_name, r.check_in_date
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_guest(guest_id):
    # מוחק אורח לפי מזהה
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM guests WHERE guest_id = ?", (guest_id,))
    conn.commit()
    affected = cursor.rowcount  # כמה שורות נמחקו בפועל (0 או 1)
    conn.close()
    return affected > 0


# ============================================================
# ---------------------- ROOMS (חדרים) -----------------------
# ============================================================

def add_room(room_number, room_type, price_per_night, status="available"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO rooms (room_number, room_type, price_per_night, status) VALUES (?, ?, ?, ?)",
        (room_number, room_type, price_per_night, status)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_all_rooms():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT room_id, room_number, room_type, price_per_night, status FROM rooms")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_room_occupancy(as_of_date=None):
    # מחזיר, עבור כל חדר, את שם האורח ששוהה בו בתאריך הנתון (אם יש כזה)
    # זו תצוגה "ממוקדת-חדר" - הפוכה מ-get_all_reservations שהיא "ממוקדת-הזמנה"
    # אם לא סופק תאריך, נעשה שימוש בתאריך של היום
    if as_of_date is None:
        as_of_date = date.today().isoformat()
    if not DATE_PATTERN.match(as_of_date):
        raise ValueError("פורמט תאריך שגוי - יש להזין בפורמט YYYY-MM-DD, לדוגמה 2026-09-01")

    conn = get_connection()
    cursor = conn.cursor()
    # LEFT JOIN כדי שגם חדרים ללא הזמנה פעילה יופיעו (עם ערכי NULL לאורח)
    cursor.execute("""
        SELECT ro.room_id, ro.room_number, ro.room_type,
               g.full_name, r.check_in_date, r.check_out_date, r.status
        FROM rooms ro
        LEFT JOIN reservations r
            ON r.room_id = ro.room_id
            AND r.status != 'cancelled'
            AND r.check_in_date <= ? AND r.check_out_date > ?
        LEFT JOIN guests g ON g.guest_id = r.guest_id
        ORDER BY ro.room_number
    """, (as_of_date, as_of_date))
    rows = cursor.fetchall()
    conn.close()
    return as_of_date, rows


def get_room_availability(check_in_date, check_out_date):
    # מחזיר את כל החדרים יחד עם זמינות אמיתית לטווח התאריכים הנתון
    # (מבוסס על אותה בדיקת התנגשויות שמשמשת את add_reservation, ולא על
    # שדה ה-status הסטטי בטבלה, שאינו תלוי בתאריכים)
    if not DATE_PATTERN.match(check_in_date) or not DATE_PATTERN.match(check_out_date):
        raise ValueError("פורמט תאריך שגוי - יש להזין בפורמט YYYY-MM-DD, לדוגמה 2026-09-01")
    if check_in_date >= check_out_date:
        raise ValueError("תאריך צ'ק-אין חייב להיות לפני תאריך צ'ק-אאוט")

    rooms = get_all_rooms()
    results = []
    for room_id, room_number, room_type, price, status in rooms:
        if status == "maintenance":
            availability = "בתחזוקה - לא זמין"
        elif check_reservation_conflict(room_id, check_in_date, check_out_date):
            availability = "תפוס בתאריכים אלה"
        else:
            availability = "פנוי בתאריכים אלה"
        results.append((room_id, room_number, room_type, price, status, availability))
    return results


def update_room_status(room_id, new_status):
    # מעדכן את הסטטוס של חדר (available / occupied / maintenance)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE rooms SET status = ? WHERE room_id = ?", (new_status, room_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


# ============================================================
# ------------------- RESERVATIONS (הזמנות) -------------------
# זוהי הליבה של הפרויקט - מקביל לניהול "תורים" בדרישות המקוריות
# ============================================================

def check_reservation_conflict(room_id, check_in_date, check_out_date):
    # בודק אם קיימת כבר הזמנה לאותו חדר שחופפת בטווח התאריכים הנתון
    # מחזיר True אם יש התנגשות, אחרת False
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT reservation_id FROM reservations
        WHERE room_id = ?
          AND status != 'cancelled'
          AND NOT (check_out_date <= ? OR check_in_date >= ?)
    """, (room_id, check_in_date, check_out_date))
    conflict = cursor.fetchone()
    conn.close()
    return conflict is not None


def add_reservation(guest_id, room_id, check_in_date, check_out_date, notes=None):
    # מוסיף הזמנה חדשה, לאחר בדיקת תקינות בסיסית ובדיקת התנגשות תאריכים

    # --- בדיקה 1: שדות התאריך לא ריקים ---
    if not check_in_date or not check_out_date:
        raise ValueError("חובה לספק תאריך צ'ק-אין ותאריך צ'ק-אאוט")

    # --- בדיקה 2: פורמט התאריך תקין (YYYY-MM-DD) ---
    # בלי הבדיקה הזו, תאריך כמו 01-09-2026 היה מתקבל בשקט וגורם להשוואות שגויות
    if not DATE_PATTERN.match(check_in_date) or not DATE_PATTERN.match(check_out_date):
        raise ValueError("פורמט תאריך שגוי - יש להזין בפורמט YYYY-MM-DD, לדוגמה 2026-09-01")

    # --- בדיקה 3: תאריך הצ'ק-אין קודם לתאריך הצ'ק-אאוט ---
    if check_in_date >= check_out_date:
        raise ValueError("תאריך צ'ק-אין חייב להיות לפני תאריך צ'ק-אאוט")

    # --- בדיקה 4: האורח קיים בפועל בטבלת guests ---
    # בלי הבדיקה הזו, SQLite היה זורק שגיאת FOREIGN KEY לא ברורה (IntegrityError)
    if get_guest_by_id(guest_id) is None:
        raise ValueError(f"לא נמצא אורח עם מזהה {guest_id} - בדוק את הרשימה באפשרות 5 בתפריט")

    # --- בדיקה 5: החדר קיים בפועל בטבלת rooms ---
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT room_id FROM rooms WHERE room_id = ?", (room_id,))
    room_exists = cursor.fetchone()
    conn.close()
    if room_exists is None:
        raise ValueError(f"לא נמצא חדר עם מזהה {room_id} - בדוק את הרשימה באפשרות 7 בתפריט")

    # --- בדיקה 6: אין התנגשות עם הזמנה קיימת לאותו חדר ---
    if check_reservation_conflict(room_id, check_in_date, check_out_date):
        raise ValueError(f"קיימת כבר הזמנה לחדר {room_id} בטווח התאריכים המבוקש")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO reservations (guest_id, room_id, check_in_date, check_out_date, status, notes)
           VALUES (?, ?, ?, ?, 'pending', ?)""",
        (guest_id, room_id, check_in_date, check_out_date, notes)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_all_reservations():
    # מחזיר את כל ההזמנות, כולל שם האורח, טלפון האורח ומספר החדר (JOIN בין 3 טבלאות)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.reservation_id, g.full_name, g.phone, ro.room_number,
               r.check_in_date, r.check_out_date, r.status, r.notes
        FROM reservations r
        JOIN guests g ON r.guest_id = g.guest_id
        JOIN rooms ro ON r.room_id = ro.room_id
        ORDER BY r.check_in_date
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_reservation_status(reservation_id, new_status):
    # מעדכן סטטוס הזמנה: pending / confirmed / cancelled / completed
    valid_statuses = ("pending", "confirmed", "cancelled", "completed")
    if new_status not in valid_statuses:
        raise ValueError(f"סטטוס לא תקין: {new_status}")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE reservations SET status = ? WHERE reservation_id = ?", (new_status, reservation_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def delete_reservation(reservation_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reservations WHERE reservation_id = ?", (reservation_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


# ============================================================
# --------------------- LEADS (לידים) - בונוס 2 ---------------
# ============================================================

def add_lead(full_name, phone=None, source=None, desired_room_type=None,
              desired_check_in=None, desired_check_out=None, notes=None):
    # מוסיף ליד חדש - בקשה לחדר שעדיין לא הפכה להזמנה בפועל
    # בעתיד: זה יקרה אוטומטית מתוך הסוכן כשמישהו שואל בוואטסאפ על זמינות
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO leads (full_name, phone, source, desired_room_type,
                               desired_check_in, desired_check_out, status, notes)
           VALUES (?, ?, ?, ?, ?, ?, 'new', ?)""",
        (full_name, phone, source, desired_room_type, desired_check_in, desired_check_out, notes)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_all_leads():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT lead_id, full_name, phone, source,
               desired_room_type, desired_check_in, desired_check_out, status, notes
        FROM leads
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_lead_by_id(lead_id):
    # מחזיר ליד בודד לפי מזהה, או None אם לא נמצא
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT lead_id, full_name, phone, source,
               desired_room_type, desired_check_in, desired_check_out, status, notes
        FROM leads WHERE lead_id = ?
    """, (lead_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def update_lead_status(lead_id, new_status):
    valid_statuses = ("new", "in_progress", "converted", "rejected")
    if new_status not in valid_statuses:
        raise ValueError(f"סטטוס לא תקין: {new_status}")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE leads SET status = ? WHERE lead_id = ?", (new_status, lead_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def convert_lead_to_reservation(lead_id, room_id, check_in_date=None, check_out_date=None):
    # ממיר ליד ישירות להזמנה: מוצא/יוצר את האורח לפי הטלפון של הליד,
    # יוצר הזמנה בפועל על החדר שנבחר, ומעדכן את סטטוס הליד ל-'converted'
    # אם לא סופקו תאריכים, נעשה שימוש בתאריכים המבוקשים שנשמרו על הליד
    lead_row = get_lead_by_id(lead_id)
    if lead_row is None:
        raise ValueError(f"לא נמצא ליד עם מזהה {lead_id}")

    (_, full_name, phone, source, desired_room_type,
     desired_check_in, desired_check_out, status, notes) = lead_row

    final_check_in = check_in_date or desired_check_in
    final_check_out = check_out_date or desired_check_out
    if not final_check_in or not final_check_out:
        raise ValueError("לליד הזה אין תאריכים מבוקשים - יש לספק תאריכי צ'ק-אין וצ'ק-אאוט")

    # מוצאים אורח קיים לפי טלפון, או יוצרים אורח חדש מפרטי הליד
    existing_guest = find_guest_by_phone(phone) if phone else None
    if existing_guest:
        guest_id = existing_guest[0]
    else:
        guest_id = add_guest(full_name=full_name, phone=phone)

    new_reservation_id = add_reservation(guest_id, room_id, final_check_in, final_check_out,
                                          notes=f"הומר מליד #{lead_id}" + (f" - {notes}" if notes else ""))
    update_lead_status(lead_id, "converted")
    return new_reservation_id


# ============================================================
# ------------------- INVOICES (חשבוניות) - בונוס 1 -----------
# ============================================================

def add_invoice(invoice_number, guest_id, amount, reservation_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO invoices (invoice_number, guest_id, reservation_id, amount)
           VALUES (?, ?, ?, ?)""",
        (invoice_number, guest_id, reservation_id, amount)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_guest_history(guest_id):
    # מחזיר עבור לקוח נתון: את כל ההזמנות שלו ואת כל החשבוניות שלו
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT reservation_id, room_id, check_in_date, check_out_date, status
        FROM reservations WHERE guest_id = ?
    """, (guest_id,))
    reservations = cursor.fetchall()

    cursor.execute("""
        SELECT invoice_id, invoice_number, amount, issue_date
        FROM invoices WHERE guest_id = ?
    """, (guest_id,))
    invoices = cursor.fetchall()

    conn.close()
    return {"reservations": reservations, "invoices": invoices}
