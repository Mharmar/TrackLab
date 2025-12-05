# 🧪 TrackLab: Laboratory Equipment Management System

**TrackLab** is a robust, role-based desktop application developed using Python and Tkinter for managing and tracking laboratory equipment lending and inventory in real-time. It ensures accountability, minimizes equipment loss, and provides detailed reporting on usage and status.

---

## ✨ Features Overview

| Category | Feature | Description |
| :--- | :--- | :--- |
| **Inventory** | **Real-Time Tracking** | Dashboard updates instantly upon borrow/return transactions, showing available stock. |
| | **Visual Status** | Inventory list dynamically displays stock level, condition (Broken, Out of Stock, Good). |
| **Transaction**| **Time Limits & Overdue** | Users must select an **Expected Return Date and Time** via a custom calendar interface. |
| | **Dynamic Status** | Items are automatically flagged as **Overdue** on the Dashboard if the due time passes. |
| **Security** | **Role-Based Access** | Strict separation of privileges between Admin, Staff, and Students. |
| | **Ownership Lock** | Students/Staff can **only return** items they personally borrowed. |
| | **Admin Override** | Administrators can force-return, **Void/Delete transactions**, and manage equipment for all users. |
| **User Interface** | **Responsive Design** | Application window starts maximized for optimal display of the dashboard. |
| | **Modern Aesthetics** | Gradient background on the landing page and circular profile pictures on borrower cards. |
| **Reporting** | **Detailed Analytics** | Comprehensive reporting module for Borrowing History, Damage Reports, Overdue Items, and visual usage charts. |

---

## 🛠️ Setup and Installation 

### 1. Prerequisites

* **Python 3.8+**
* **MySQL Database (XAMPP/WAMP/MAMP):** The application relies on a MySQL server running locally.
    * **XAMPP Port:** The application is configured to connect to MySQL on port `3307` (standard XAMPP default). If your port is different, you must update `database/connection.py`.

### 2. Install Python Dependencies

Open your terminal in the project root directory and install the required packages:

```bash
pip install mysql-connector-python Pillow
```
### 3. Database Initialization (CRITICAL STEP)

The application requires a database named tracklab with the necessary tables (users, equipment, borrowers, etc.).

Run the setup script once from the project root:
```bash
python setup_database.py
```

This script will create the database, all necessary tables, and ensure the default Admin user is functional.

---

### 🔑 User Roles and Default Credentials
The system implements three distinct roles, with Admin having exclusive management capabilities:
| Role | Username | Password | Inventory Management | Transaction Management |
| :--- | :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | **Full Control** (Add/Edit/Delete) | **Override** (Return/Void any transaction) |
| **Staff** | *(Register via App)* | *(Register via App)* | Read-Only | Can only return own items |
| **Student** | *(Register via App)* | *(Register via App)* | Read-Only | Can only return own items |
---
### Admin Login Access
To log in as the administrator, use the specific "Admin Login" link provided below the standard sign-in form on the login page.

---
#### 📂 Project Structure

```bash
TrackLab/
├── database/               # MySQL connection and CRUD logic (Users, Equipment, Borrows)
│   ├── connection.py       # Manages MySQL connector
│   ├── borrow_db.py        # Handles dynamic Overdue status, fetching borrows, and Admin Void
│   ├── reports_db.py       # Contains complex queries for analytics and reports
│   └── users_db.py         # Login, registration, and profile updates
├── gui/                    # Tkinter UI pages and classes
│   ├── app.py              # Main application controller, window manager, and global logo loader
│   ├── dashboard_page.py   # Primary view with role-based borrower list and inventory
│   ├── borrow_page.py      # Detailed borrowing form with custom Calendar/Time picker
│   ├── equipment_page.py   # Admin-only management view (Add, Edit, Delete)
│   └── popups.py           # Reusable popups (Quick Borrow, Add Item, Return)
├── utils/                  # Helper modules (Colors, ID generation, Session management)
│   └── tracklablogo.png    # Application logo file (Source of truth)
├── main.py                 # Application entry point
└── setup_database.py       # One-time database creation script
```

---
