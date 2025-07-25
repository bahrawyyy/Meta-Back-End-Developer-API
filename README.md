# Meta-Back-End-Developer-API

A RESTful API built with Django and Django REST Framework for managing a restaurant system. It includes endpoints for user registration, menu items, cart management, orders, and user roles (customer, manager, delivery crew).

---

## 🚀 Features

- 🔐 User registration and login
- 👨‍🍳 Role-based access control (customer, delivery-crew, manager)
- 📋 Menu items listing, filtering, pagination, and CRUD operations (Manager only)
- 🛒 Cart management for customers
- 📦 Order placement and assignment to delivery crew
- 🔄 Order status updates (by delivery crew)
- 🧑‍💼 Group/user management (Managers only)

---

## 📁 Project Structure

```bash
.
├── urls.py
├── views.py
├── models.py
├── serializers.py
└── ...
```

---

## 🔧 Technologies Used

- Python 3.x
- Django
- Django REST Framework

---

## ⚙️ Installation & Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/little-lemon-api.git
cd little-lemon-api

# Create virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

---

## 📘 API Documentation

See `API_DOCUMENTATION.md` for complete endpoint details and usage.

---

## 🔐 Authentication

All endpoints (except user registration) require authentication. Use token-based authentication:

```http
Authorization: Bearer <your_token>
```
