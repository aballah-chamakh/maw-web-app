# Mawlety Order Sync – Full-Stack App

**Mawlety Order Sync** is a full-stack application built with **Django** and **React.js** that automates the end‑to‑end order workflow for the brand **Mawlety**. The application loads orders directly from the Mawlety PrestaShop store, saves them into its own database, and automatically submits them to Mawlety's carrier platform. It then continuously synchronizes the statuses by comparing the orders submitted from the app with their corresponding orders on the carrier platform and updates the status on the Mawlety store whenever a difference is detected. This eliminates manual syncing and ensures full alignment between the store and the carrier system.

## Demo 

Click the image below to view the demo video on YouTube : 

[![Mawlety Order Sync Demo](https://img.youtube.com/vi/7op97GIx-RE/maxresdefault.jpg)](https://youtu.be/7op97GIx-RE)

## Features

* **Automatic Order Loading**: Retrieves orders directly from the Mawlety PrestaShop store and stores them in the app database.
* **Automated Carrier Submission**: Submits loaded orders to Mawlety's carrier platform without manual intervention.
* **Status Synchronization**: Compares app-submitted orders with their counterparts on the carrier platform and updates the order status on Mawlety's store whenever changes occur.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/aballah-chamakh/maw-web-app.git
   ```
2. Set up the Python environment and install dependencies:

   ```bash
   cd backend 
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```
3. Apply migrations and start the **Django** server:

   ```bash
   cd maw
   python manage.py migrate
   python manage.py runserver
   ```
4. Start the React front-end:

   ```bash
   cd frontend/maw
   npm install
   npm start
   ```

## Requirements

* Python 3.8+
* **Django** 3.2+
* Node.js 14+
* **React.js** 17+


