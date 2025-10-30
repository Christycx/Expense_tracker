@app.route('/add_expense', methods=['POST'])
def add_expense():
    data = request.get_json()
    date = data.get('date')
    expense_manager.add_expenses(data['category'],data['amount'], date)
    return jsonify({'status': 'Expense added Successfully'})



