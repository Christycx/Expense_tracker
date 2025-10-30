import json
import os
from datetime import datetime, timedelta

class Expense:
    def __init__(self, expense_id, category, amount, date=None):
        self.expense_id = expense_id
        self.category = category
        self.amount = amount
        self.date = date if date else datetime.now().strftime('%Y-%m-%d')
    
    def to_dict(self):
        return {
            'expense_id': self.expense_id,
            'category': self.category,
            'amount': self.amount,
            'date': self.date
        }

class ExpenseManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.expenses = []
        self.load_expenses()
    
    def load_expenses(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as file:
                    data = json.load(file)
                    # Convert dict to Expense objects
                    self.expenses = [Expense(**expense) for expense in data]
            except (json.JSONDecodeError, KeyError):
                self.expenses = []
        else:
            self.expenses = []

    def save_expenses(self):
        try:
            with open(self.file_path, 'w') as file:
                json.dump([expense.to_dict() for expense in self.expenses], file, indent=2)
        except Exception as e:
            print(f"Error saving expenses: {e}")
    
    def get_all_expenses(self):
        return self.expenses
    
    def add_expenses(self, category, amount, date=None):
        # FIXED: Proper ID generation
        if self.expenses:
            expense_id = max(expense.expense_id for expense in self.expenses) + 1
        else:
            expense_id = 1
            
        new_expense = Expense(expense_id, category, amount, date)
        self.expenses.append(new_expense)
        self.save_expenses()

    def delete_expense(self, expense_id):
        # FIXED: Ensure we're working with the latest data
        self.load_expenses()
        self.expenses = [expense for expense in self.expenses if expense.expense_id != expense_id]
        self.save_expenses()

    def get_expenses_by_category(self):
        expenses_by_category = {}
        for expense in self.expenses:
            if expense.category in expenses_by_category:
                expenses_by_category[expense.category] += expense.amount
            else:
                expenses_by_category[expense.category] = expense.amount
        return expenses_by_category
    
    def get_expenses_by_date(self):
        expenses_by_date = {}
        for expense in self.expenses:
            if expense.date in expenses_by_date:
                expenses_by_date[expense.date] += expense.amount
            else:
                expenses_by_date[expense.date] = expense.amount
        return dict(sorted(expenses_by_date.items()))
    
    # Get all unique dates
    def get_all_dates(self):
        dates = sorted(set(expense.date for expense in self.expenses), reverse=True)
        return dates
    
    # Get expenses by category for a specific date
    def get_expenses_by_category_for_date(self, date):
        expenses_by_category = {}
        for expense in self.expenses:
            if expense.date == date:
                if expense.category in expenses_by_category:
                    expenses_by_category[expense.category] += expense.amount
                else:
                    expenses_by_category[expense.category] = expense.amount
        return expenses_by_category
    
    # FIXED METHOD: Get monthly expenses for the last 3 months
    def get_monthly_expenses(self):
        monthly_expenses = {}
        
        # Get current date
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        print(f"DEBUG: Current date is {current_date}")
        print(f"DEBUG: Current year: {current_year}, month: {current_month}")
        
        # Calculate the last 3 months
        for i in range(3):
            # Calculate target month and year
            target_month = current_month - i
            target_year = current_year
            
            # Handle year rollover
            if target_month < 1:
                target_month += 12
                target_year -= 1
            
            month_name = datetime(target_year, target_month, 1).strftime('%B %Y')
            
            print(f"DEBUG: Checking month {month_name} (Year: {target_year}, Month: {target_month})")
            
            # Initialize month data
            monthly_expenses[month_name] = {
                'total': 0,
                'categories': {},
                'year': target_year,
                'month': target_month
            }
            
            # Calculate expenses for this month
            expense_count = 0
            for expense in self.expenses:
                try:
                    expense_date = datetime.strptime(expense.date, '%Y-%m-%d')
                    if expense_date.year == target_year and expense_date.month == target_month:
                        monthly_expenses[month_name]['total'] += expense.amount
                        expense_count += 1
                        
                        # Add to category total
                        if expense.category in monthly_expenses[month_name]['categories']:
                            monthly_expenses[month_name]['categories'][expense.category] += expense.amount
                        else:
                            monthly_expenses[month_name]['categories'][expense.category] = expense.amount
                except ValueError:
                    # Skip invalid dates
                    continue
            
            print(f"DEBUG: Found {expense_count} expenses in {month_name}")
        
        print(f"DEBUG: Final monthly expenses: {list(monthly_expenses.keys())}")
        return monthly_expenses