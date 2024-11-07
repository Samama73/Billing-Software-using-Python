import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from PIL import Image, ImageDraw, ImageFont

class BillingSoftware(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Billing Software")
        self.geometry("800x600")

        # Connect to database
        self.conn = sqlite3.connect("billing_database.db")
        self.cursor = self.conn.cursor()

        # Create tables
        self.create_tables()

        # Create widgets
        self.create_widgets()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                name TEXT,
                gender TEXT,
                contact TEXT,
                email TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT,
                price REAL,
                quantity INTEGER,
                brand TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS billings (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                product_id INTEGER,
                total_amount REAL,
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        """)
        self.conn.commit()

    def create_widgets(self):
        # Create a notebook to hold the different pages
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create frames for each page
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.customer_frame = ttk.Frame(self.notebook)
        self.inventory_frame = ttk.Frame(self.notebook)
        self.billing_frame = ttk.Frame(self.notebook)

        # Add frames to the notebook
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.notebook.add(self.customer_frame, text="Customers")
        self.notebook.add(self.inventory_frame, text="Inventory")
        self.notebook.add(self.billing_frame, text="Billing")

        # Create widgets for Dashboard
        self.create_dashboard_widgets()

        # Create widgets for Customer Management
        self.create_customer_widgets()

        # Create widgets for Inventory Management
        self.create_inventory_widgets()

        # Create widgets for Billing Management
        self.create_billing_widgets()

    def create_dashboard_widgets(self):
        tk.Label(self.dashboard_frame, text="Dashboard", font=("Arial", 24)).pack(pady=20)

        # Search bar
        search_frame = tk.Frame(self.dashboard_frame)
        search_frame.pack(pady=10)
        tk.Label(search_frame, text="Search:").grid(row=0, column=0)
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.grid(row=0, column=1)
        self.search_button = tk.Button(search_frame, text="Search", command=self.search)
        self.search_button.grid(row=0, column=2)

        # Notification bell icon
        self.notification_button = tk.Button(self.dashboard_frame, text="🔔", command=self.show_notifications)
        self.notification_button.pack(side=tk.RIGHT, padx=10)

        # Profile section
        profile_frame = tk.Frame(self.dashboard_frame)
        profile_frame.pack(pady=10)
        tk.Label(profile_frame, text="Profile:").grid(row=0, column=0)
        self.profile_label = tk.Label(profile_frame, text="Samama Momin")
        self.profile_label.grid(row=0, column=1)

        self.total_sales_label = tk.Label(self.dashboard_frame, text="Total Sales: $0.00", font=("Arial", 18))
        self.total_sales_label.pack(pady=10)

        self.total_revenue_label = tk.Label(self.dashboard_frame, text="Total Revenue: $0.00", font=("Arial", 18))
        self.total_revenue_label.pack(pady=10)

        self.update_dashboard()

    def search(self):
        search_term = self.search_entry.get().lower()
        # Logic for searching customers and products can be implemented here
        print(f"Searching for: {search_term}")

    def show_notifications(self):
        messagebox.showinfo("Notifications", "You have no new notifications.")

    def update_dashboard(self):
        # Calculate total sales and revenue
        self.cursor.execute("SELECT SUM(total_amount) FROM billings")
        total_revenue = self.cursor.fetchone()[0] or 0.0
        self.total_revenue_label.config(text=f"Total Revenue: ${total_revenue:.2f}")

        self.cursor.execute("SELECT COUNT(*) FROM billings")
        total_sales = self.cursor.fetchone()[0]
        self.total_sales_label.config(text=f"Total Sales: {total_sales}")

    def create_customer_widgets (self):
        tk.Label(self.customer_frame, text="Add Customer ").grid(row=0, column=0, columnspan=2)

        tk.Label(self.customer_frame, text="Name").grid(row=1, column=0)
        self.customer_name = tk.Entry(self.customer_frame)
        self.customer_name.grid(row=1, column=1)

        tk.Label(self.customer_frame, text="Gender").grid(row=2, column=0)
        self.customer_gender = tk.Entry(self.customer_frame)
        self.customer_gender.grid(row=2, column=1)

        tk.Label(self.customer_frame, text="Contact").grid(row=3, column=0)
        self.customer_contact = tk.Entry(self.customer_frame)
        self.customer_contact.grid(row=3, column=1)

        tk.Label(self.customer_frame, text="Email").grid(row=4, column=0)
        self.customer_email = tk.Entry(self.customer_frame)
        self.customer_email.grid(row=4, column=1)

        tk.Button(self.customer_frame, text="Save", command=self.add_customer).grid(row=5, columnspan=2)

        self.customer_list = tk.Listbox(self.customer_frame)
        self.customer_list.grid(row=6, columnspan=2)
        self.customer_list.bind('<<ListboxSelect>>', self.load_customer)

        tk.Button(self.customer_frame, text="Delete", command=self.delete_customer).grid(row=7, columnspan=2)

    def add_customer(self):
        name = self.customer_name.get()
        gender = self.customer_gender.get()
        contact = self.customer_contact.get()
        email = self.customer_email.get()

        self.cursor.execute("INSERT INTO customers (name, gender, contact, email) VALUES (?, ?, ?, ?)", (name, gender, contact, email))
        self.conn.commit()

        self.customer_list.insert(tk.END, f"{name} ({contact})")
        self.customer_name.delete(0, tk.END)
        self.customer_gender.delete(0, tk.END)
        self.customer_contact.delete(0, tk.END)
        self.customer_email.delete(0, tk.END)

    def load_customer(self, event):
        selected_customer = self.customer_list.get(self.customer_list.curselection())
        self.cursor.execute("SELECT * FROM customers WHERE name=? AND contact=?", selected_customer.split(" (")[0], selected_customer.split(" (")[1][:-1])
        customer_data = self.cursor.fetchone()

        self.customer_name.delete(0, tk.END)
        self.customer_name.insert(0, customer_data[1])
        self.customer_gender.delete(0, tk.END)
        self.customer_gender.insert(0, customer_data[2])
        self.customer_contact.delete(0, tk.END)
        self.customer_contact.insert(0, customer_data[3])
        self.customer_email.delete(0, tk.END)
        self.customer_email.insert(0, customer_data[4])

    def delete_customer(self):
        selected_customer = self.customer_list.get(self.customer_list.curselection())
        name, contact = selected_customer.split(" (")
        contact = contact[:-1]

        self.cursor.execute("DELETE FROM customers WHERE name=? AND contact=?", (name, contact))
        self.conn.commit()

        self.customer_list.delete(self.customer_list.curselection())
        self.customer_name.delete(0, tk.END)
        self.customer_gender.delete(0, tk.END)
        self.customer_contact.delete(0, tk.END)
        self.customer_email.delete(0, tk.END)

    def create_inventory_widgets(self):
        tk.Label(self.inventory_frame, text="Add Product").grid(row=0, column=0, columnspan=2)

        tk.Label(self.inventory_frame, text="Product Name").grid(row=1, column=0)
        self.product_name = tk.Entry(self.inventory_frame)
        self.product_name.grid(row=1, column=1)

        tk.Label(self.inventory_frame, text="Price").grid(row=2, column=0)
        self.product_price = tk.Entry(self.inventory_frame)
        self.product_price.grid(row=2, column=1)

        tk.Label(self.inventory_frame, text="Quantity").grid(row=3, column=0)
        self.product_quantity = tk.Entry(self.inventory_frame)
        self.product_quantity.grid(row=3, column=1)

        tk.Label(self.inventory_frame, text="Brand").grid(row=4, column=0)
        self.product_brand = tk.Entry(self.inventory_frame)
        self.product_brand.grid(row=4, column=1)

        tk.Button(self.inventory_frame, text="Save", command=self.add_product).grid(row=5, columnspan=2)

        self.product_list = tk.Listbox(self.inventory_frame)
        self.product_list.grid(row=6, columnspan=2)
        self.product_list.bind('<<ListboxSelect>>', self.load_product)

        tk.Button(self.inventory_frame, text="Edit", command=self.edit_product).grid(row=7, column=0 )
        tk.Button(self.inventory_frame, text="Delete", command=self.delete_product).grid(row=7, column=1)

    def add_product(self):
        name = self.product_name.get()
        price = self.product_price.get()
        quantity = self.product_quantity.get()
        brand = self.product_brand.get()

        self.cursor.execute("INSERT INTO products (name, price, quantity, brand) VALUES (?, ?, ?, ?)", (name, price, quantity, brand))
        self.conn.commit()

        self.product_list.insert(tk.END, f"{name} (${price}) - {quantity} units")
        self.product_name.delete(0, tk.END)
        self.product_price.delete(0, tk.END)
        self.product_quantity.delete(0, tk.END)
        self.product_brand.delete(0, tk.END)

    def load_product(self, event):
        selected_product = self.product_list.get(self.product_list.curselection())
        name, price_quantity = selected_product.split(" ($")
        price, quantity = price_quantity.split(") - ")
        quantity = quantity[:-5]

        self.cursor.execute("SELECT * FROM products WHERE name=? AND price=? AND quantity=?", (name, price, quantity))
        product_data = self.cursor.fetchone()

        self.product_name.delete(0, tk.END)
        self.product_name.insert(0, product_data[1])
        self.product_price.delete(0, tk.END)
        self.product_price.insert(0, product_data[2])
        self.product_quantity.delete(0, tk.END)
        self.product_quantity.insert(0, product_data[3])
        self.product_brand.delete(0, tk.END)
        self.product_brand.insert(0, product_data[4])

    def edit_product(self):
        selected_product = self.product_list.get(self.product_list.curselection())
        name, price_quantity = selected_product.split(" ($")
        price, quantity = price_quantity.split(") - ")
        quantity = quantity[:-5]

        name = self.product_name.get()
        price = self.product_price.get()
        quantity = self.product_quantity.get()
        brand = self.product_brand.get()

        self.cursor.execute("UPDATE products SET name=?, price=?, quantity=?, brand=? WHERE name=? AND price=? AND quantity=?", (name, price, quantity, brand, selected_product.split(" ($")[0], price, quantity))
        self.conn.commit()

        self.product_list.delete(self.product_list.curselection())
        self.product_list.insert(tk.END, f"{name} (${price}) - {quantity} units")

    def delete_product(self):
        selected_product = self.product_list.get(self.product_list.curselection())
        name, price_quantity = selected_product.split(" ($")
        price, quantity = price_quantity.split(") - ")
        quantity = quantity[:-5]

        self.cursor.execute("DELETE FROM products WHERE name=? AND price=? AND quantity=?", (name, price, quantity))
        self.conn.commit()

        self.product_list.delete(self.product_list.curselection())
        self.product_name.delete(0, tk.END)
        self.product_price.delete(0, tk.END)
        self.product_quantity.delete(0, tk.END)
        self.product_brand.delete(0, tk.END)

    def create_billing_widgets(self):
        tk.Label(self.billing_frame, text="Billing").grid(row=0, column=0, columnspan=2)

        tk.Label(self.billing_frame, text="Customer").grid(row=1, column=0)
        self.customer_id = tk.Entry(self.billing_frame)
        self.customer_id.grid(row=1, column=1)

        tk.Label(self.billing_frame, text="Product").grid(row=2, column=0)
        self.product_id = tk.Entry(self.billing_frame)
        self.product_id.grid(row=2, column=1)

        tk.Button(self.billing_frame, text="Generate Bill", command=self.generate_bill).grid(row=3, columnspan=2)

        self.billing_list = tk.Listbox(self.billing_frame)
        self.billing_list.grid(row=4, columnspan=2)
        self.billing_list.bind('<<ListboxSelect>>', self.load_billing)

        tk.Button(self.billing_frame, text="Edit", command=self.edit_billing).grid(row=5, column=0)
        tk.Button(self.billing_frame, text="Delete", command=self.delete_billing).grid(row=5, column=1)

    def generate_bill(self):
        customer_id = (self.customer_id.get(),)
        product_id = (self.product_id.get(),)

        self.cursor.execute("SELECT * FROM customers WHERE id=?", customer_id)
        customer_data = self.cursor.fetchone()

        self.cursor.execute("SELECT * FROM products WHERE id=?", product_id)
        product_data = self.cursor.fetchone()

        total_amount = product_data[2] * 1  # Assuming 1 unit is purchased

        self.cursor.execute("INSERT INTO billings (customer_id, product_id, total_amount) VALUES (?, ?, ?)", (customer_id[0], product_id[0], total_amount))
        self.conn.commit()

        self.billing_list.insert(tk.END, f"Bill for {customer_data[1]} - {product_data[1]} (${total_amount:.2f})")
        self.customer_id.delete(0, tk.END)
        self.product_id.delete(0, tk.END)

        self.update_dashboard()

        # Generate bill image
        bill_image = Image.new('RGB', (400, 200), color = (73, 109, 137))
        draw = ImageDraw.Draw(bill_image)
        font = ImageFont.load_default()

        draw.text((10, 10), f"Bill for: {customer_data[1]}", font=font, fill=(255, 255, 0))
        draw.text((10, 30), f"Product: {product_data[1]}", font=font, fill=(255, 255, 0))
        draw.text((10, 50), f"Total Amount: ${total_amount:.2f}", font=font, fill=(255, 255, 0))
        bill_image.save(f"bill_{customer_id[0]}_{product_id[0]}.png")

    def load_billing(self, event):
        selected_billing = self.billing_list.get(self.billing_list.curselection())
        customer_name, product_name_price = selected_billing.split(" - ")
        product_name, price = product_name_price.split(" ($")
        price = price[:-2]

        self.cursor.execute("SELECT * FROM billings WHERE total_amount=?", price)
        billing_data = self.cursor.fetchone()

        self.customer_id.delete(0, tk.END)
        self.customer_id.insert(0, billing_data[1])
        self.product_id.delete(0, tk.END)
        self.product_id.insert(0, billing_data[2])

    def edit_billing(self):
        selected_billing = self.billing_list.get(self.billing_list.curselection())
        customer_name, product_name_price = selected_billing.split(" - ")
        product_name, price = product_name_price.split(" ($")
        price = price[:-2]

        customer_id = self.customer_id.get()
        product_id = self.product_id.get()

        self.cursor.execute("UPDATE billings SET customer_id=?, product_id=? WHERE total_amount=?", (customer_id, product_id, price))
        self.conn.commit()

        self.billing_list.delete(self.billing_list.curselection())
        self.billing_list.insert(tk.END, f"Bill for {customer_id} - {product_id} (${price})")

    def delete_billing(self):
        selected_billing = self.billing_list.get(self.billing_list.curselection())
        customer_name, product_name_price = selected_billing.split(" - ")
        product_name, price = product_name_price.split(" ($")
        price = price[:-2]

        self.cursor.execute("DELETE FROM billings WHERE total_amount=?", price)
        self.conn.commit()

        self.billing_list.delete(self.billing_list.curselection())
        self.customer_id.delete(0, tk.END)
        self.product_id.delete(0, tk.END)

if __name__ == "__main__":
    app = BillingSoftware()
    app.mainloop()