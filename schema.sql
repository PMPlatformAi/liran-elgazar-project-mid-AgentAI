-- ============================================================
-- schema.sql
-- קובץ זה מגדיר את מבנה בסיס הנתונים (הטבלאות) של מערכת ניהול
-- ההזמנות והלידים עבור מלון גנרי (hotelAi)
-- הקובץ בטוח להרצה חוזרת (DROP TABLE IF EXISTS לפני כל CREATE)
-- ============================================================

-- מוחקים טבלאות קיימות (אם יש) כדי שאפשר יהיה להריץ את הקובץ
-- מספר פעמים בלי שגיאות של "הטבלה כבר קיימת"
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS reservations;
DROP TABLE IF EXISTS leads;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS guests;

-- ------------------------------------------------------------
-- טבלת אורחים / לקוחות (guests)
-- כל שורה מייצגת לקוח אחד של המלון
-- ------------------------------------------------------------
CREATE TABLE guests (
    guest_id     INTEGER PRIMARY KEY AUTOINCREMENT,  -- מזהה ייחודי אוטומטי לכל אורח
    full_name    TEXT NOT NULL,                       -- שם מלא של האורח (חובה)
    phone        TEXT,                                -- מספר טלפון
    email        TEXT,                                -- כתובת אימייל
    address      TEXT,                                -- כתובת מגורים
    created_at   TEXT DEFAULT (datetime('now'))        -- תאריך יצירת הרשומה
);

-- ------------------------------------------------------------
-- טבלת חדרים (rooms)
-- כל שורה מייצגת חדר אחד במלון
-- ------------------------------------------------------------
CREATE TABLE rooms (
    room_id         INTEGER PRIMARY KEY AUTOINCREMENT, -- מזהה ייחודי לחדר
    room_number     TEXT NOT NULL UNIQUE,               -- מספר חדר (חייב להיות ייחודי)
    room_type       TEXT NOT NULL,                       -- סוג חדר: יחיד / זוגי / סוויטה וכו'
    price_per_night REAL NOT NULL,                       -- מחיר ללילה
    status          TEXT NOT NULL DEFAULT 'available'    -- available / occupied / maintenance
);

-- ------------------------------------------------------------
-- טבלת הזמנות (reservations) - הליבה של הפרויקט (מקביל ל"תורים")
-- כל שורה מייצגת הזמנת חדר של אורח בטווח תאריכים מסוים
-- ------------------------------------------------------------
CREATE TABLE reservations (
    reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- מזהה ייחודי להזמנה
    guest_id       INTEGER NOT NULL,                    -- מפתח זר -> guests.guest_id
    room_id        INTEGER NOT NULL,                    -- מפתח זר -> rooms.room_id
    check_in_date  TEXT NOT NULL,                        -- תאריך צ'ק-אין (YYYY-MM-DD)
    check_out_date TEXT NOT NULL,                        -- תאריך צ'ק-אאוט (YYYY-MM-DD)
    status         TEXT NOT NULL DEFAULT 'pending',      -- pending / confirmed / cancelled / completed
    notes          TEXT,                                 -- הערות חופשיות להזמנה
    created_at     TEXT DEFAULT (datetime('now')),       -- תאריך יצירת ההזמנה במערכת
    FOREIGN KEY (guest_id) REFERENCES guests (guest_id),
    FOREIGN KEY (room_id)  REFERENCES rooms (room_id)
);

-- ------------------------------------------------------------
-- טבלת לידים (leads) - בונוס 2
-- ליד = בקשה פוטנציאלית לחדר שעדיין לא הפכה להזמנה בפועל
-- (למשל: פנייה בוואטסאפ "יש לכם חדר זוגי פנוי בספטמבר?")
-- ------------------------------------------------------------
CREATE TABLE leads (
    lead_id            INTEGER PRIMARY KEY AUTOINCREMENT,  -- מזהה ייחודי לליד
    full_name          TEXT NOT NULL,                       -- שם הפונה
    phone              TEXT,                                -- טלפון ליצירת קשר (גם מזהה בפועל בוואטסאפ)
    source             TEXT,                                -- מקור הפנייה (אתר / טלפון / וואטסאפ / סוכן AI...)
    desired_room_type  TEXT,                                -- סוג חדר מבוקש (יחיד / זוגי / סוויטה)
    desired_check_in   TEXT,                                -- תאריך צ'ק-אין מבוקש (YYYY-MM-DD)
    desired_check_out  TEXT,                                -- תאריך צ'ק-אאוט מבוקש (YYYY-MM-DD)
    status             TEXT NOT NULL DEFAULT 'new',         -- new / in_progress / converted / rejected
    notes              TEXT,                                -- הערות נוספות על הפנייה
    created_at         TEXT DEFAULT (datetime('now'))        -- תאריך יצירת הליד
);

-- ------------------------------------------------------------
-- טבלת חשבוניות (invoices) - בונוס 1
-- כל שורה מייצגת חשבונית שהופקה עבור לקוח (בד"כ בגין הזמנה)
-- ------------------------------------------------------------
CREATE TABLE invoices (
    invoice_id     INTEGER PRIMARY KEY AUTOINCREMENT,  -- מזהה ייחודי לחשבונית
    invoice_number TEXT NOT NULL UNIQUE,                -- מספר חשבונית מס ייחודי (לתצוגה ללקוח)
    guest_id       INTEGER NOT NULL,                    -- מפתח זר -> guests.guest_id
    reservation_id INTEGER,                              -- מפתח זר -> reservations.reservation_id (יכול להיות ריק)
    amount         REAL NOT NULL,                        -- סכום החשבונית
    issue_date     TEXT DEFAULT (datetime('now')),       -- תאריך הפקת החשבונית
    FOREIGN KEY (guest_id) REFERENCES guests (guest_id),
    FOREIGN KEY (reservation_id) REFERENCES reservations (reservation_id)
);
