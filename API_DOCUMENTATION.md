# 📘 API Documentation – Little Lemon Restaurant

This file documents all available endpoints and their expected behavior.

---

## 🧑‍💻 User Endpoints

### 🔹 POST /users/ – Register new user
```json
Request:
{
  "username": "john",
  "password": "1234",
  "email": "john@example.com"
}

Response:
{
  "message": "User created successfully",
  "user_id": 5
}
```

---

### 🔹 GET /users/users/me – Get current user info
> Requires token authentication.

```json
Response:
{
  "username": "john",
  "email": "john@example.com"
}
```

---

## 📋 Menu Items

### 🔹 GET /menu-items/ – List menu items (with filters)
> Roles: customer, delivery-crew, manager

Query Params: title, price, category, page, per_page

```http
GET /menu-items/?title=burger&price=20&category=Main&page=1&per_page=5
```

---

### 🔹 POST /menu-items/ – Create menu item
> Role: manager

```json
{
  "title": "Burger",
  "price": "12.99",
  "category": 1
}
```

---

### 🔹 GET /menu-items/<id>/ – Get menu item detail  
🔹 PUT, PATCH, DELETE – Update/delete (manager only)

---

## 👥 Group Management

### 🔹 GET /groups/<group_name>/users – List users in group  
🔹 POST /groups/<group_name>/users – Add user to group  
🔹 DELETE /groups/<group_name>/users/<user_id>/ – Remove user from group  
> Role: manager  
> Valid group_name: manager, delivery-crew

```json
Request:
{
  "user_id": 5
}
```

---

## 🛒 Cart Management

### 🔹 POST /cart/menu-items/ – Add item to cart  
### 🔹 GET /cart/menu-items/ – View current user's cart  
### 🔹 DELETE /cart/menu-items/ – Clear user’s cart  
> Role: customer

---

## 📦 Orders

### 🔹 POST /orders/ – Create order from current cart  
> Role: customer

---

### 🔹 GET /orders/ – View orders
- Manager: View all orders
- Delivery Crew: View assigned orders
- Customer: View own orders

---

### 🔹 GET /orders/<order_id>/
- Delivery Crew: View own order
- Manager: View/edit/delete any order
- Delivery Crew: PATCH status

```json
PATCH /orders/5/
{
  "status": "delivered"
}
```

```json
PUT /orders/5/
{
  "delivery_crew": 4
}
```

---

## 🛡️ Role Permissions Summary

| Endpoint | Customer | Delivery Crew | Manager |
|---------|----------|----------------|---------|
| /users/ | ✅ | ✅ | ✅ |
| /users/users/me | ✅ | ✅ | ✅ |
| /menu-items/ | ✅ (GET) | ✅ (GET) | ✅ (all) |
| /groups/... | ❌ | ❌ | ✅ |
| /cart/... | ✅ | ❌ | ❌ |
| /orders/ | ✅ (own) | ✅ (assigned) | ✅ (all) |
| /orders/<id>/ | ❌ | ✅ (own) | ✅ |

---
