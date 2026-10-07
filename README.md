# 🏔️ TrekOS: Expedition Management Platform

**TrekOS** is a robust, full-stack web application designed to streamline the management of trekking and mountaineering expeditions. Built with **Flask** and **SQLAlchemy**, it utilizes a Server-Side Rendered (SSR) architecture to deliver secure, role-based portals for Platform Administrators, Expedition Guides (Staff), and Trekkers (Users).

---

## ✨ Key Features by Role

### 🛡️ Admin Command Center
* **Comprehensive Dashboard:** Real-time metrics on total users, active treks, and platform bookings.
* **Trek Management:** Full CRUD (Create, Read, Update, Delete) capabilities for expeditions. Tracks real-time slot capacities.
* **User Management:** Safely remove users with automated cascading deletion (cleaning up orphaned bookings and assignments).
* **Staff Assignments:** Approve guide applications and assign staff members to specific active expeditions.
* **System History:** Live audit log tracking critical platform actions (e.g., trek creations, new bookings).

### 🧭 Staff / Guide Portal
* **Field Dashboard:** Instant access to assigned upcoming and active expeditions.
* **Participant Manifests:** View detailed lists of all trekkers booked for their assigned trips.
* **Status Updates:** Update expedition statuses (Upcoming -> Active -> Completed) directly from the field.

### 🎒 Trekker / User Experience
* **Explore & Filter:** Browse active expeditions and filter by location and difficulty (Beginner, Moderate, Hard).
* **Smart Booking Engine:** Secure booking system that prevents duplicate reservations and enforces maximum slot capacities.
* **Personal Dashboard:** Track upcoming trips and review complete trekking history.
* **Profile Management:** Securely update personal details, gender, and passwords.

---

## 🛠️ Tech Stack

* **Backend Framework:** Python 3.x, Flask
* **Database & ORM:** SQLite (Development), PostgreSQL via Supabase (Production), Flask-SQLAlchemy
* **Authentication & Security:** Flask-Login (Session management), Werkzeug.security (Password hashing)
* **Frontend UI:** HTML5, CSS3, Jinja2 Templating
* **Deployment:** Vercel (Serverless Hosting)

---

## 🚀 Local Installation & Setup

Want to run TrekOS on your local machine? Follow these steps:

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR-USERNAME/TrekOS.git](https://github.com/YOUR-USERNAME/TrekOS.git)
cd TrekOS
