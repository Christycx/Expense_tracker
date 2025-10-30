from flask import Flask, render_template, request, redirect, jsonify, url_for
from models1 import ExpenseManager

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
        
        # Check if data is received
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
        return jsonify({'status': f'Error: {str(e)}'}), 500

@app.route('/delete_expense/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    try:
        expense_manager.delete_expense(expense_id)
        return jsonify({'status': 'Expense deleted successfully'})
    except Exception as e:
        return jsonify({'status': f'Error deleting expense: {str(e)}'}), 500

@app.route('/view_chart')
def view_chart():
    try:
        # Get all unique dates for the dropdown
        all_dates = expense_manager.get_all_dates()
        # Get category data for all expenses (default view)
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

# New route for filtered chart data
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

if __name__ == '__main__':
    app.run(debug=True)