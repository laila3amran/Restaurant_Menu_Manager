🍴 Restaurant Menu Manager

A Flask web application to manage a restaurant menu with full CRUD functionality and image uploads. Built using Flask, PostgreSQL, and Tailwind CSS for a clean, modern UI.

# Features

- View the restaurant menu in card layout with images

- Add a new dish with name, price, and image (upload from your computer)

- Update existing dishes, including changing image

- Delete dishes

- Click on a dish to see detailed information

- Styled using Tailwind CSS with custom color scheme:

      Primary: #555879

      Secondary: #98A1BC

      Accent: #DED3C4

      Background: #F4EBD3


Usage

Navigate to Menu to see all dishes.

Click Add Item to add a new dish.

Click on a dish card to view details, update, or delete it.

Images are uploaded directly from your computer.

# Project Structure
Restaurant_Menu_Manager/
│
├── app.py                # Main Flask application
├── database.py           # DB connection helper
├── create_table.py       # Script to create DB tables
├── requirements.txt
├── static/
│   └── uploads/          # Uploaded dish images
├── templates/
│   ├── base.html
│   ├── menu.html
│   ├── add_item.html
│   ├── update_item.html
│   └── item_details.html
└── .gitignore

# Dependencies

Python 3.x

Flask

psycopg2-binary

Tailwind CSS (via CDN)

