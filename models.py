# ============================================================
# models.py
# קובץ זה מגדיר את היישויות (Entities) של המערכת כמחלקות פייתון (OOP)
# כל מחלקה מייצגת "אובייקט" מהעולם האמיתי (אורח, חדר, הזמנה, ליד, חשבונית)
# המחלקות האלה הן "מיכל נתונים" נוח לעבודה בקוד - הן לא נוגעות ב-DB בעצמן.
# הגישה לבסיס הנתונים עצמו מתבצעת בקובץ database.py
# ============================================================


class Guest:
    # מחלקה שמייצגת אורח / לקוח של המלון
    def __init__(self, full_name, phone=None, email=None, address=None, guest_id=None):
        self.guest_id = guest_id      # מזהה מה-DB (יהיה None עד שהאורח נשמר בפועל)
        self.full_name = full_name    # שם מלא - שדה חובה
        self.phone = phone            # טלפון
        self.email = email            # אימייל
        self.address = address        # כתובת

    def __str__(self):
        # הדפסה נוחה לקריאה של אובייקט אורח
        return f"[{self.guest_id}] {self.full_name} | טלפון: {self.phone} | אימייל: {self.email}"


class Room:
    # מחלקה שמייצגת חדר במלון
    def __init__(self, room_number, room_type, price_per_night, status="available", room_id=None):
        self.room_id = room_id
        self.room_number = room_number        # מספר חדר, למשל "101"
        self.room_type = room_type            # סוג חדר: יחיד / זוגי / סוויטה
        self.price_per_night = price_per_night  # מחיר ללילה
        self.status = status                  # available / occupied / maintenance

    def __str__(self):
        return f"[{self.room_id}] חדר {self.room_number} ({self.room_type}) - {self.price_per_night}₪ ללילה - סטטוס: {self.status}"


class Reservation:
    # מחלקה שמייצגת הזמנת חדר עבור אורח בטווח תאריכים
    def __init__(self, guest_id, room_id, check_in_date, check_out_date,
                 status="pending", notes=None, reservation_id=None):
        self.reservation_id = reservation_id
        self.guest_id = guest_id              # מפתח זר לאורח
        self.room_id = room_id                # מפתח זר לחדר
        self.check_in_date = check_in_date    # תאריך צ'ק-אין בפורמט YYYY-MM-DD
        self.check_out_date = check_out_date  # תאריך צ'ק-אאוט בפורמט YYYY-MM-DD
        self.status = status                  # pending / confirmed / cancelled / completed
        self.notes = notes

    def __str__(self):
        return (f"[{self.reservation_id}] אורח #{self.guest_id} | חדר #{self.room_id} | "
                f"{self.check_in_date} -> {self.check_out_date} | סטטוס: {self.status}")


class Lead:
    # מחלקה שמייצגת ליד - בקשה פוטנציאלית לחדר שעדיין לא הפכה להזמנה
    def __init__(self, full_name, phone=None, source=None, desired_room_type=None,
                 desired_check_in=None, desired_check_out=None, status="new", notes=None, lead_id=None):
        self.lead_id = lead_id
        self.full_name = full_name
        self.phone = phone
        self.source = source                        # מקור הפנייה: אתר / וואטסאפ / סוכן AI וכו'
        self.desired_room_type = desired_room_type    # סוג חדר מבוקש
        self.desired_check_in = desired_check_in      # תאריך צ'ק-אין מבוקש
        self.desired_check_out = desired_check_out    # תאריך צ'ק-אאוט מבוקש
        self.status = status                          # new / in_progress / converted / rejected
        self.notes = notes

    def __str__(self):
        return (f"[{self.lead_id}] {self.full_name} | מבקש: {self.desired_room_type} "
                f"({self.desired_check_in} -> {self.desired_check_out}) | סטטוס: {self.status}")


class Invoice:
    # מחלקה שמייצגת חשבונית מס עבור לקוח
    def __init__(self, invoice_number, guest_id, amount, reservation_id=None, invoice_id=None):
        self.invoice_id = invoice_id
        self.invoice_number = invoice_number  # מספר חשבונית ייחודי לתצוגה
        self.guest_id = guest_id
        self.reservation_id = reservation_id
        self.amount = amount

    def __str__(self):
        return f"[{self.invoice_id}] חשבונית {self.invoice_number} | אורח #{self.guest_id} | סכום: {self.amount}₪"
