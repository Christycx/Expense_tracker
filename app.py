from flask import Flask, render_template, request, redirect, jsonify, url_for
from models import ExpenseManager
import json

app = Flask(__name__)
expense_manager = ExpenseManager('expenses.json')

@app.route("/")
def index():
    expenses = expense_manager.get_all_expenses()
    return render_template('index.html', expenses=expenses)

@app.route('/add_expense', methods=['POST'])
def add_expense():
    try:
        data = request.get_json()
        print("Received data:", data)  # Debug log
        
        if not data:
            return jsonify({'status': 'Error: No data received'}), 400
            
        category = data.get('category', '').strip()
        amount_str = data.get('amount', '')
        date = data.get('date', '')
        
        # Validate required fields
        if not category:
            return jsonify({'status': 'Error: Category is required'}), 400
            
        if not amount_str:
            return jsonify({'status': 'Error: Amount is required'}), 400
            
        if not date:
            return jsonify({'status': 'Error: Date is required'}), 400
        
        # Validate and convert amount
        try:
            amount = float(amount_str)
            if amount <= 0:
                return jsonify({'status': 'Error: Amount must be positive'}), 400
        except (ValueError, TypeError):
            return jsonify({'status': 'Error: Invalid amount format'}), 400
        
        # Add expense
        expense_manager.add_expenses(category, amount, date)
        return jsonify({'status': 'Expense added successfully'})
        
    except Exception as e:
        print("Error in add_expense:", str(e))  # Debug log
        return jsonify({'status': f'Error: {str(e)}'}), 500

@app.route('/delete_expense/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    try:
        print(f"Deleting expense ID: {expense_id}")  # Debug log
        expense_manager.delete_expense(expense_id)
        return jsonify({'status': 'Expense deleted successfully'})
    except Exception as e:
        print("Error in delete_expense:", str(e))  # Debug log
        return jsonify({'status': f'Error deleting expense: {str(e)}'}), 500

@app.route('/view_chart')
def view_chart():
    try:
        all_dates = expense_manager.get_all_dates()
        expenses_by_category = expense_manager.get_expenses_by_category()
        return render_template('chart.html', 
                             expenses_by_category=expenses_by_category,
                             all_dates=all_dates,
                             selected_date='all')
    except Exception as e:
        return f"Error loading chart: {str(e)}", 500

@app.route('/view_chart_by_date')
def view_chart_by_date():
    try:
        expenses_by_date = expense_manager.get_expenses_by_date()
        return render_template('view_chart_by_date.html', expenses_by_date=expenses_by_date)
    except Exception as e:
        return f"Error loading daily chart: {str(e)}", 500

@app.route('/get_chart_data/<date>')
def get_chart_data(date):
    try:
        if date == 'all':
            expenses_by_category = expense_manager.get_expenses_by_category()
        else:
            expenses_by_category = expense_manager.get_expenses_by_category_for_date(date)
        
        all_dates = expense_manager.get_all_dates()
        return jsonify({
            'expenses_by_category': expenses_by_category,
            'all_dates': all_dates,
            'selected_date': date
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_previous_months_expenses')
def get_previous_months_expenses():
    try:
        monthly_expenses = expense_manager.get_monthly_expenses()
        return jsonify(monthly_expenses)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Debug route to check what's in your expenses file
@app.route('/debug_expenses')
def debug_expenses():
    try:
        with open('expenses.json', 'r') as f:
            expenses_data = json.load(f)
        
        # Group by month for debugging
        months_data = {}
        for expense in expenses_data:
            date_str = expense.get('date', '')
            if date_str:
                # Extract year and month
                year_month = date_str[:7]  # Gets YYYY-MM
                if year_month not in months_data:
                    months_data[year_month] = []
                months_data[year_month].append(expense)
        
        # Also group by full date for more detailed view
        dates_data = {}
        for expense in expenses_data:
            date_str = expense.get('date', '')
            if date_str:
                if date_str not in dates_data:
                    dates_data[date_str] = []
                dates_data[date_str].append(expense)
        
        debug_info = {
            'total_expenses': len(expenses_data),
            'expenses_by_month': months_data,
            'expenses_by_date': dates_data,
            'all_expenses': expenses_data
        }
        
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)