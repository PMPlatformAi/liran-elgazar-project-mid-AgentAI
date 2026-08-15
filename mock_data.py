# ============================================================
# mock_data.py
# קובץ זה מכניס נתוני דמה ("מוקים") ראשוניים לבסיס הנתונים
# המטרה: לאפשר בדיקה מהירה של המערכת בלי להקליד ידנית כל אורח/חדר/הזמנה
# יש להריץ אותו פעם אחת בלבד, אחרי יצירת הטבלאות (create_tables)
# ============================================================

import database as db


def insert_mock_data():
    print("🔄 מכניס נתוני דמה למערכת...")

    # --- אורחים (guests) ---
    guest1 = db.add_guest("דנה כהן", "050-1111111", "dana@example.com", "רחוב הרצל 5, תל אביב")
    guest2 = db.add_guest("יוסי לוי", "052-2222222", "yossi@example.com", "רחוב ביאליק 12, חיפה")
    guest3 = db.add_guest("מאיה אברהם", "054-3333333", "maya@example.com", "רחוב אלנבי 8, ירושלים")
    print(f"✅ נוספו 3 אורחים: {guest1}, {guest2}, {guest3}")

    # --- חדרים (rooms) ---
    room1 = db.add_room("101", "יחיד", 350)
    room2 = db.add_room("102", "זוגי", 500)
    room3 = db.add_room("201", "סוויטה", 900)
    print(f"✅ נוספו 3 חדרים: {room1}, {room2}, {room3}")

    # --- הזמנות (reservations) ---
    # שימו לב: add_reservation בודק בעצמו התנגשויות תאריכים לאותו חדר
    res1 = db.add_reservation(guest1, room1, "2026-08-01", "2026-08-05", notes="בקשה לחדר שקט")
    res2 = db.add_reservation(guest2, room2, "2026-08-03", "2026-08-06")
    res3 = db.add_reservation(guest3, room3, "2026-09-01", "2026-09-04", notes="ירח דבש")
    print(f"✅ נוספו 3 הזמנות: {res1}, {res2}, {res3}")

    # --- לידים (leads) - בונוס 2 ---
    # עכשיו כוללים סוג חדר מבוקש ותאריכים מבוקשים - בקשה קונקרטית לחדר, לא רק איש קשר
    lead1 = db.add_lead("אורי שפירא", "053-4444444", source="אתר האינטרנט",
                         desired_room_type="סוויטה", desired_check_in="2026-09-10",
                         desired_check_out="2026-09-13", notes="מתעניין לספטמבר")
    lead2 = db.add_lead("נועה ברק", "050-5555555", source="סוכן AI - hotelAi",
                         desired_room_type="זוגי", desired_check_in="2026-10-01",
                         desired_check_out="2026-10-03", notes="פנייה אוטומטית מהצ'אטבוט")
    print(f"✅ נוספו 2 לידים: {lead1}, {lead2}")

    # --- חשבוניות (invoices) - בונוס 1 ---
    inv1 = db.add_invoice("INV-1001", guest1, amount=1400, reservation_id=res1)
    inv2 = db.add_invoice("INV-1002", guest2, amount=1500, reservation_id=res2)
    print(f"✅ נוספו 2 חשבוניות: {inv1}, {inv2}")

    print("🎉 נתוני הדמה נוספו בהצלחה!")


if __name__ == "__main__":
    # הרצה ישירה של הקובץ תיצור קודם את הטבלאות ואז תכניס את נתוני הדמה
    db.create_tables()
    insert_mock_data()
