# E-commerce Backend API

This is a Flask-based REST API for the e-commerce dataset.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Load data into the database:
```bash
python load_data.py
```

3. Run the Flask application:
```bash
python main.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

- `GET /api/users` - Get all users
- `GET /api/products` - Get all products  
- `GET /api/orders` - Get all orders
- `GET /api/order-items` - Get all order items
- `GET /api/distribution-centers` - Get all distribution centers
- `GET /api/inventory-items` - Get all inventory items

## Database

The application uses SQLite as the database for simplicity. The database file `ecommerce.db` will be created automatically when you run the application.

## Data Loading

The `load_data.py` script will load CSV files from the `../dataset/` directory into the SQLite database. Make sure your CSV files are in the correct location before running the script.

## Troubleshooting

If you encounter the `'mssql.runQuery' not found` error, this solution replaces the Microsoft SQL Server connection with SQLAlchemy and SQLite, which is more suitable for development and doesn't require additional database setup. 