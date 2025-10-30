$(document).ready(function() {
    // Set default date to today
    const today = new Date().toISOString().split('T')[0];
    $('#date').val(today);

    // Add expense functionality
    $('#add_expense').click(function(){
        var category = $("#category").val().trim();
        var amount = $("#amount").val().trim();
        var date = $("#date").val();
        
        console.log("Adding expense:", {category, amount, date}); // Debug log
        
        // Validate inputs
        if (!category) {
            alert('Please enter a category');
            return;
        }
        
        if (!amount || isNaN(amount) || parseFloat(amount) <= 0) {
            alert('Please enter a valid amount');
            return;
        }
        
        if (!date) {
            alert('Please select a date');
            return;
        }

        $.ajax({
            url: '/add_expense',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                'category': category, 
                'amount': amount,
                'date': date
            }),
            success: function(response){
                console.log("Add success:", response); // Debug log
                alert(response.status);
                window.location.reload(); 
            },
            error: function(xhr, status, error){
                console.error("Add error:", xhr.responseJSON); // Debug log
                let errorMsg = 'Error adding expense';
                if (xhr.responseJSON && xhr.responseJSON.status) {
                    errorMsg = xhr.responseJSON.status;
                }
                alert(errorMsg);
            }            
        });
    });

    // Delete expense functionality - FIXED: Use event delegation for dynamic elements
    $(document).on('click', '.delete_expense', function() {
        var expenseID = parseInt($(this).attr('data-id'));
        console.log("Deleting expense ID:", expenseID); // Debug log

        if (confirm('Are you sure you want to delete this expense?')) {
            $.ajax({
                url: '/delete_expense/' + expenseID,
                type: 'DELETE',
                success: function(response){
                    console.log("Delete success:", response); // Debug log
                    alert(response.status);
                    window.location.reload(); 
                },
                error: function(xhr, status, error){
                    console.error("Delete error:", xhr.responseJSON); // Debug log
                    let errorMsg = 'Error deleting expense';
                    if (xhr.responseJSON && xhr.responseJSON.status) {
                        errorMsg = xhr.responseJSON.status;
                    }
                    alert(errorMsg);
                }        
            });
        }
    });

    // Previous Months Expenses functionality
    $('#previous_months_btn').on('click', function() {
        loadPreviousMonthsExpenses();
    });

    // Close modal functionality
    $('#closeModal').on('click', function() {
        $('#previousMonthsModal').addClass('hidden');
    });

    // Close modal when clicking outside
    $('#previousMonthsModal').on('click', function(e) {
        if (e.target === this) {
            $('#previousMonthsModal').addClass('hidden');
        }
    });
});

function loadPreviousMonthsExpenses() {
    $.ajax({
        url: '/get_previous_months_expenses',
        type: 'GET',
        success: function(response) {
            displayMonthlyExpenses(response);
        },
        error: function(xhr, status, error) {
            alert('Error loading monthly expenses: ' + error);
        }
    });
}

function displayMonthlyExpenses(monthlyData) {
    const container = $('#monthlyExpensesContainer');
    container.empty();

    if (Object.keys(monthlyData).length === 0) {
        container.html('<p class="text-gray-500 text-center">No expense data available for previous months.</p>');
    } else {
        // Sort months in reverse chronological order (most recent first)
        const months = Object.keys(monthlyData).sort((a, b) => {
            return new Date(monthlyData[b].year, monthlyData[b].month - 1) - 
                   new Date(monthlyData[a].year, monthlyData[a].month - 1);
        });

        months.forEach(monthName => {
            const monthData = monthlyData[monthName];
            const monthElement = `
                <div class="border rounded-lg p-4 bg-gray-50">
                    <div class="flex justify-between items-center mb-3">
                        <h4 class="text-xl font-semibold text-gray-800">${monthName}</h4>
                        <span class="text-lg font-bold text-blue-600">Total: $${monthData.total.toFixed(2)}</span>
                    </div>
                    ${Object.keys(monthData.categories).length > 0 ? 
                        `<div class="space-y-2">
                            ${Object.entries(monthData.categories).map(([category, amount]) => 
                                `<div class="flex justify-between text-sm">
                                    <span class="text-gray-600">${category}</span>
                                    <span class="font-medium">$${amount.toFixed(2)}</span>
                                </div>`
                            ).join('')}
                        </div>` :
                        '<p class="text-gray-500 text-sm">No expenses for this month</p>'
                    }
                </div>
            `;
            container.append(monthElement);
        });
    }

    // Show the modal
    $('#previousMonthsModal').removeClass('hidden');
}