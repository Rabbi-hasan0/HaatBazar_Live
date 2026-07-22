# 🛒 HaatBazar - E-Commerce API Platform

![Django](https://img.shields.io/badge/Django-4.x-092E20?style=for-the-badge&logo=django)
![DRF](https://img.shields.io/badge/Django_REST_Framework-3.x-red?style=for-the-badge&logo=django)
![Railway](https://img.shields.io/badge/Railway-Deployed-purple?style=for-the-badge&logo=railway)
![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)

**HaatBazar** is a robust and scalable E-Commerce REST API backend built with **Django** and **Django REST Framework (DRF)**. It provides end-to-end features for managing multi-vendor shops, products, categories, shopping carts, and merchant management with secure JWT authentication.

---

## 🌐 Live API Endpoints

- 🛍️ **Customer / Public Base URL:**  
  https://haatbazar.up.railway.app/haatbazar/all-shops/

- 🏪 **Merchant Portal Base URL:**  
  https://haatbazar.up.railway.app/haatbazar/accounts/merchant/login/

---

## 📷 Screenshots

### 🛍️ Customer Site
| Home / Shops Page | Product Details |
| :---: | :---: |
| ![Customer Site 1](Image_URL_Here) | ![Customer Site 2](Image_URL_Here) |

### ⚙️ Admin & Merchant Site
| Admin Dashboard | Merchant Order |
| :---: | :---: |
| ![Dashboard](https://github.com/Rabbi-hasan0/HaatBazar_Live/raw/main/photos/dashboard.png) | ![Order](https://github.com/Rabbi-hasan0/HaatBazar_Live/raw/main/photos/order.png) |
---

## ✨ Features

- 🔐 **Authentication:** Secure Token-based Authentication using `djangorestframework_simplejwt`.
- 🏪 **Multi-Vendor & Shops:** Dedicated endpoints for merchants and customer shop listings.
- 📦 **Product Catalog:** Full CRUD API operations for products, categories, and inventory.
- 🛒 **Cart & Order System:** Seamless API endpoints for cart items and order processing.
- 🖼️ **Media & Assets:** Image processing with `Pillow` and static file serving with `WhiteNoise`.
- 📊 **Data Export/Import:** Support for Excel handling using `openpyxl` and `tablib`.
- 🚀 **Railway Ready:** Pre-configured with `Gunicorn` and `Procfile` for cloud deployment.

---

## 🛠️ Tech Stack

- **Backend Framework:** Django, Django REST Framework (DRF)
- **Database:** PostgreSQL / SQLite
- **Security:** PyJWT, SimpleJWT
- **WSGI Server:** Gunicorn
- **Deployment Platform:** Railway

---

## 🚀 Local Development Setup

### 1. Clone the Repository
git clone https://github.com/rabbihasan162/HaatBazar.git
cd HaatBazar/single_E_comerce

### 2. Create and Activate Virtual Environment
# On Windows:
python -m venv venv
venv\Scripts\activate

# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate

### 3. Install Dependencies
pip install -r requirements.txt

### 4. Setup Environment Variables
Create a .env file inside the project directory:
SECRET_KEY=your_secret_key_here
DEBUG=True

### 5. Run Migrations & Start Server
python manage.py migrate
python manage.py runserver

Visit http://127.0.0.1:8000/ in your browser.

---

## ☁️ Deployment

This project is deployed and hosted live on **Railway**.

---

## 👨‍💻 Author

**Rabbi Hasan**
- GitHub: [@rabbihasan162](https://github.com/rabbihasan162)
