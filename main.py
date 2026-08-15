# ============================================================
# main.py
# קובץ זה הוא נקודת הכניסה הראשית להרצת המערכת
# הוא מציג תפריט טקסטואלי בטרמינל, ממוקד סביב ה"הזמנה" כישות המרכזית -
# כפי שיעבוד בפועל מנהל מלון (ובעתיד, סוכן AI בוואטסאפ)
# ============================================================

import database as db


def print_menu():
    # מדפיס את תפריט הפעולות האפשריות למשתמש, מקובץ לפי קטגוריות
    print("\n===== מערכת ניהול הזמנות - hotelAi =====")
    print("--- הזמנות ---")
    print("1. הצגת כל ההזמנות")
    print("2. הוספת הזמנה חדשה (כולל זיהוי/יצירת אורח לפי טלפון או אימייל)")
    print("3. עדכון סטטוס הזמנה")
    print("4. מחיקת הזמנה")
    print("5. תצוגת תפוסה - איזה אורח נמצא באיזה חדר (לפי תאריך)")
    print("--- אורחים ---")
    print("6. הצגת כל האורחים + ההזמנות שלהם")
    print("--- חדרים ---")
    print("7. הצגת סטטוס חדרים (פנוי / תפוס)")
    print("--- לידים - בקשות לחדר שעדיין לא הפכו להזמנה ---")
    print("8. הצגת כל הלידים")
    print("9. הוספת ליד חדש (בעתיד: ייווצר אוטומטית ע\"י הסוכן)")
    print("10. המרת ליד להזמנה בפועל")
    print("0. יציאה")


def _yes(answer):
    # פונקציית עזר: מפרשת תשובת כן/לא בעברית או אנגלית, בצורה סלחנית
    return answer.strip() in ("כן", "כ", "yes", "y", "Y")


# ============================================================
# ------------------------ הזמנות -----------------------------
# ============================================================

def handle_show_reservations():
    # מציג את כל ההזמנות במערכת: מי האורח (עם טלפון), איזה חדר, תאריכים וסטטוס
    reservations = db.get_all_reservations()
    if not reservations:
        print("אין הזמנות במערכת.")
        return
    print(f"{'מזהה':<6}{'שם אורח':<14}{'טלפון':<14}{'חדר':<7}{'צ׳ק-אין':<13}{'צ׳ק-אאוט':<13}{'סטטוס'}")
    for res_id, guest_name, phone, room_number, check_in, check_out, status, notes in reservations:
        print(f"{res_id:<6}{guest_name:<14}{(phone or '-'):<14}{room_number:<7}{check_in:<13}{check_out:<13}{status}")


def _select_or_create_guest():
    # מזהה אורח לפי טלפון או אימייל (לא לפי מזהה פנימי - הלקוח לא מכיר אותו)
    # אם לא נמצא אורח כזה, יוצר אורח חדש על המקום
    # מחזיר guest_id, או None אם המשתמש לא סיפק פרטים תקינים
    contact = input("טלפון או אימייל של האורח (משמש לזיהוי): ").strip()
    if not contact:
        print("❌ יש להזין טלפון או אימייל לזיהוי האורח.")
        return None

    existing = db.find_guest_by_contact(contact)
    if existing:
        guest_id, full_name, phone, email = existing
        print(f"✅ נמצא אורח קיים: {full_name}")
        return guest_id

    print("לא נמצא אורח קיים עם פרטים אלה - ניצור אורח חדש.")
    full_name = input("שם מלא: ")
    if not full_name.strip():
        print("❌ שם מלא הוא שדה חובה.")
        return None

    is_email = "@" in contact
    phone = contact if not is_email else input("טלפון (אפשר להשאיר ריק): ")
    email = contact if is_email else input("אימייל (אפשר להשאיר ריק): ")
    address = input("כתובת (אפשר להשאיר ריק): ")

    new_id = db.add_guest(full_name, phone or None, email or None, address or None)
    print(f"✅ האורח '{full_name}' נוסף בהצלחה למערכת.")
    return new_id


def handle_add_reservation():
    # מבקש מהמשתמש פרטי הזמנה חדשה ומוסיף אותה, עם טיפול בשגיאות
    guest_id = _select_or_create_guest()
    if guest_id is None:
        return  # לא הצלחנו לזהות/ליצור אורח - חוזרים לתפריט הראשי

    # שואלים את התאריכים ומציגים ישר אילו חדרים באמת פנויים באותו טווח
    check_in = input("\nתאריך צ'ק-אין (YYYY-MM-DD, לדוגמה 2026-09-01): ")
    check_out = input("תאריך צ'ק-אאוט (YYYY-MM-DD, לדוגמה 2026-09-04): ")

    try:
        rooms_with_availability = db.get_room_availability(check_in, check_out)
    except ValueError as e:
        print(f"❌ שגיאה: {e}")
        return

    print(f"\n--- זמינות חדרים ל-{check_in} .. {check_out} ---")
    print(f"{'מזהה':<6}{'מספר חדר':<11}{'סוג':<10}{'מחיר/לילה':<12}{'זמינות'}")
    for room_id, room_number, room_type, price, status, availability in rooms_with_availability:
        print(f"{room_id:<6}{room_number:<11}{room_type:<10}{price:<12}{availability}")

    try:
        room_id = int(input("\nמזהה חדר פנוי (מהעמודה הראשונה למעלה): "))
        notes = input("הערות (אפשר להשאיר ריק): ")

        new_id = db.add_reservation(guest_id, room_id, check_in, check_out, notes or None)
        print(f"✅ ההזמנה נוספה בהצלחה, מזהה הזמנה: {new_id}")
    except ValueError as e:
        # תופס גם שגיאות המרה למספר וגם שגיאות לוגיות (כמו מזהה לא קיים / התנגשות תאריכים)
        print(f"❌ שגיאה: {e}")


def handle_update_reservation_status():
    print("\n--- הזמנות קיימות ---")
    handle_show_reservations()
    try:
        res_id = int(input("\nמזהה הזמנה לעדכון: "))
        print("סטטוסים אפשריים: pending (ממתין) / confirmed (מאושר) / cancelled (בוטל) / completed (הושלם)")
        new_status = input("סטטוס חדש: ")
        success = db.update_reservation_status(res_id, new_status)
        print("✅ הסטטוס עודכן." if success else "❌ לא נמצאה הזמנה עם מזהה זה.")
    except ValueError as e:
        print(f"❌ שגיאה: {e}")


def handle_delete_reservation():
    print("\n--- הזמנות קיימות ---")
    handle_show_reservations()
    try:
        res_id = int(input("\nמזהה הזמנה למחיקה: "))
        success = db.delete_reservation(res_id)
        print("✅ ההזמנה נמחקה." if success else "❌ לא נמצאה הזמנה עם מזהה זה.")
    except ValueError:
        print("❌ יש להזין מספר תקין.")


def handle_show_occupancy():
    # תצוגת תפוסה: לכל חדר - איזה אורח נמצא בו בתאריך נתון (ברירת מחדל: היום)
    date_input = input("לאיזה תאריך לבדוק תפוסה? (YYYY-MM-DD, אפשר להשאיר ריק בשביל היום): ").strip()
    try:
        as_of_date, occupancy = db.get_room_occupancy(date_input or None)
    except ValueError as e:
        print(f"❌ שגיאה: {e}")
        return

    print(f"\n--- תפוסה נכון לתאריך {as_of_date} ---")
    print(f"{'חדר':<10}{'סוג':<10}{'אורח בחדר'}")
    for room_id, room_number, room_type, guest_name, check_in, check_out, status in occupancy:
        occupant = guest_name if guest_name else "— פנוי —"
        print(f"{room_number:<10}{room_type:<10}{occupant}")


# ============================================================
# --------------------- אורחים (תמיד עם הזמנות) -----------------
# ============================================================

def handle_show_guests():
    # מציג את כל האורחים יחד עם ההזמנות שלהם (חדר + תאריכים)
    # אין כאן "אורח בפני עצמו" - הערך היחיד הוא לראות מה כל אורח הזמין
    rows = db.get_guests_with_reservations()
    if not rows:
        print("אין אורחים במערכת.")
        return

    print(f"{'שם אורח':<14}{'טלפון':<14}{'חדר':<8}{'צ׳ק-אין':<13}{'צ׳ק-אאוט':<13}{'סטטוס'}")
    for full_name, phone, email, room_number, check_in, check_out, status in rows:
        room_display = room_number if room_number else "-"
        check_in_display = check_in if check_in else "-"
        check_out_display = check_out if check_out else "-"
        status_display = status if status else "אין הזמנות"
        print(f"{full_name:<14}{(phone or '-'):<14}{room_display:<8}{check_in_display:<13}{check_out_display:<13}{status_display}")


# ============================================================
# ---------------------- חדרים (סטטוס) --------------------------
# ============================================================

def handle_show_rooms():
    # מציג את סטטוס החדרים: פנוי / תפוס, לפי בקשת המשתמש
    rooms = db.get_all_rooms()
    if not rooms:
        print("אין חדרים במערכת.")
        return

    check_specific_dates = input("להציג זמינות לתאריכים ספציפיים? (כן/לא): ")

    if _yes(check_specific_dates):
        check_in = input("תאריך צ'ק-אין (YYYY-MM-DD): ")
        check_out = input("תאריך צ'ק-אאוט (YYYY-MM-DD): ")
        try:
            rooms_with_availability = db.get_room_availability(check_in, check_out)
        except ValueError as e:
            print(f"❌ שגיאה: {e}")
            return
        print(f"\n{'מספר חדר':<11}{'סוג':<10}{'מחיר/לילה':<12}{'סטטוס'}")
        for room_id, room_number, room_type, price, status, availability in rooms_with_availability:
            print(f"{room_number:<11}{room_type:<10}{price:<12}{availability}")
    else:
        # ללא תאריך ספציפי - מציגים לפי מצב "היום"
        as_of_date, occupancy = db.get_room_occupancy()
        print(f"\n--- סטטוס חדרים נכון להיום ({as_of_date}) ---")
        print(f"{'מספר חדר':<11}{'סוג':<10}{'סטטוס'}")
        for room_id, room_number, room_type, guest_name, check_in, check_out, status in occupancy:
            room_status = "תפוס" if guest_name else "פנוי"
            print(f"{room_number:<11}{room_type:<10}{room_status}")


# ============================================================
# --------------------- לידים (בקשות לחדר) ----------------------
# ============================================================

def handle_show_leads():
    # מציג את כל הלידים - בקשות לחדר (סוג + תאריכים) שעדיין לא הפכו להזמנה
    leads = db.get_all_leads()
    if not leads:
        print("אין לידים במערכת.")
        return
    print(f"{'מזהה':<6}{'שם':<14}{'טלפון':<14}{'סוג חדר':<10}{'צ׳ק-אין':<13}{'צ׳ק-אאוט':<13}{'סטטוס'}")
    for lead_id, full_name, phone, source, room_type, check_in, check_out, status, notes in leads:
        print(f"{lead_id:<6}{full_name:<14}{(phone or '-'):<14}{(room_type or '-'):<10}"
              f"{(check_in or '-'):<13}{(check_out or '-'):<13}{status}")


def handle_add_lead():
    # הוספת ליד חדש - בקשה לחדר שעדיין לא סגורה
    # הערה: בעתיד השלב הזה יקרה אוטומטית מתוך הסוכן שמנתח שיחת וואטסאפ
    full_name = input("שם הפונה: ")
    if not full_name.strip():
        print("❌ שם הוא שדה חובה.")
        return
    phone = input("טלפון (אפשר ריק): ")
    source = input("מקור הפנייה - למשל אתר / וואטסאפ / טלפון (אפשר ריק): ")
    room_type = input("סוג חדר מבוקש - יחיד / זוגי / סוויטה (אפשר ריק): ")
    check_in = input("תאריך צ'ק-אין מבוקש (YYYY-MM-DD, אפשר ריק): ")
    check_out = input("תאריך צ'ק-אאוט מבוקש (YYYY-MM-DD, אפשר ריק): ")
    notes = input("הערות נוספות (אפשר ריק): ")

    new_id = db.add_lead(full_name, phone or None, source or None,
                          room_type or None, check_in or None, check_out or None, notes or None)
    print(f"✅ הליד נוסף בהצלחה, מזהה: {new_id} | סטטוס התחלתי: new (חדש)")


def handle_convert_lead():
    # ממיר ליד ישירות להזמנה בפועל - זה הרגע שבו פנייה הופכת לעסקה סגורה
    print("\n--- לידים קיימים ---")
    handle_show_leads()
    try:
        lead_id = int(input("\nמזהה ליד להמרה: "))
    except ValueError:
        print("❌ יש להזין מספר תקין.")
        return

    lead_row = db.get_lead_by_id(lead_id)
    if lead_row is None:
        print("❌ לא נמצא ליד עם מזהה זה.")
        return

    (_, full_name, phone, source, desired_room_type,
     desired_check_in, desired_check_out, status, notes) = lead_row

    # אם לליד אין תאריכים שמורים, נבקש אותם עכשיו
    check_in = desired_check_in or input("תאריך צ'ק-אין (YYYY-MM-DD): ")
    check_out = desired_check_out or input("תאריך צ'ק-אאוט (YYYY-MM-DD): ")

    try:
        rooms_with_availability = db.get_room_availability(check_in, check_out)
    except ValueError as e:
        print(f"❌ שגיאה: {e}")
        return

    print(f"\n--- זמינות חדרים ל-{check_in} .. {check_out} (מבוקש: {desired_room_type or 'לא צויין'}) ---")
    print(f"{'מזהה':<6}{'מספר חדר':<11}{'סוג':<10}{'מחיר/לילה':<12}{'זמינות'}")
    for room_id, room_number, room_type, price, room_status, availability in rooms_with_availability:
        print(f"{room_id:<6}{room_number:<11}{room_type:<10}{price:<12}{availability}")

    try:
        room_id = int(input("\nמזהה חדר לשיוך להזמנה: "))
        new_reservation_id = db.convert_lead_to_reservation(lead_id, room_id, check_in, check_out)
        print(f"✅ הליד הומר להזמנה בפועל, מזהה הזמנה: {new_reservation_id}")
    except ValueError as e:
        print(f"❌ שגיאה: {e}")


def main():
    # פונקציית הכניסה הראשית - מריצה לולאת תפריט עד שהמשתמש בוחר לצאת
    while True:
        print_menu()
        choice = input("בחר פעולה: ")

        if choice == "1":
            handle_show_reservations()
        elif choice == "2":
            handle_add_reservation()
        elif choice == "3":
            handle_update_reservation_status()
        elif choice == "4":
            handle_delete_reservation()
        elif choice == "5":
            handle_show_occupancy()
        elif choice == "6":
            handle_show_guests()
        elif choice == "7":
            handle_show_rooms()
        elif choice == "8":
            handle_show_leads()
        elif choice == "9":
            handle_add_lead()
        elif choice == "10":
            handle_convert_lead()
        elif choice == "0":
            print("להתראות! 👋")
            break
        else:
            print("❌ בחירה לא תקינה, נסה שוב.")


if __name__ == "__main__":
    main()
