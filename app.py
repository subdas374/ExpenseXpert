from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import pymongo

app = Flask(__name__)

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["expenses_tracker"]
users_collection = db["users"]
expenses_collection = db["expenses"]



class User:
    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password = password

class Expense:
    def __init__(self, user_id, amount, category, expense_date):
        self.user_id = user_id
        self.amount = amount
        self.category = category
        self.expense_date = expense_date





@app.route('/')
def index():
    return render_template("home.html")







@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # Check if the email is already registered
        if users_collection.find_one({"email": email}):
            return "Email is already registered. Please use a different email."

        # Check if the username is already taken
        if users_collection.find_one({"username": username}):
            return "Username is already taken. Please choose a different username."

        # Create a new user
        user = User(email, username, password)
        users_collection.insert_one(user.__dict__)

        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if user exists
        user = users_collection.find_one({"username": username, "password": password})
        if user:
            return redirect(url_for('user_dashboard', username=username))
        else:
            return 'Invalid credentials. Please try again.'
    return render_template('login.html')



@app.route('/user/<username>/dashboard')
def user_dashboard(username):
    # Get user information
    user = users_collection.find_one({"username": username})
    if user:
        # Get user expenses
        expenses = expenses_collection.find({"user_id": username}).sort("expense_date", -1)
        total_expenses = sum(expense["amount"] for expense in expenses)

        # Get data for the pie chart
        category_data = expenses_collection.aggregate([
            {"$match": {"user_id": username}},
            {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}}
        ])
        category_labels = [category["_id"] for category in category_data]
        category_data = [category["total"] for category in category_data]
        

        return render_template('dashboard.html', user=user, expenses=expenses, total_expenses=total_expenses)
    else:
        return 'User not found.'

@app.route('/user/<username>/add_expense', methods=['POST'])
def add_expense(username):
    amount = float(request.form['amount'])
    category = request.form['category']
    expense_date = datetime.now()

    # Add expense to database
    expense = Expense(username, amount, category, expense_date)
    expenses_collection.insert_one(expense.__dict__)

    return redirect(url_for('user_dashboard', username=username))









if __name__ == '__main__':
    app.run()