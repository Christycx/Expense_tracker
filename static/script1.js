$(document).ready(function() {
    // Set default date to today
    const today = new Date().toISOString().split('T')[0];
    $('#date').val(today);

    $('#add_expense').click(function(){
        var category = $("#category").val().trim();
        var amount = $("#amount").val().trim();
        var date = $("#date").val();
        
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

        // Send the raw values, let backend handle parsing
        $.ajax({
            url: '/add_expense',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                'category': category, 
                'amount': amount,  // Send as string, let backend parse
                'date': date
            }),
            success: function(response){
                alert(response.status);
                window.location.reload(); 
            },
            error: function(xhr, status, error){
                // Improved error handling
                let errorMsg = 'Error adding expense';
                if (xhr.responseJSON && xhr.responseJSON.status) {
                    errorMsg = xhr.responseJSON.status;
                }
                alert(errorMsg);
            }            
        });
    });

    $('.delete_expense').on('click', function() {
        var expenseID = parseInt($(this).attr('data-id'));

        if (confirm('Are you sure you want to delete this expense?')) {
            $.ajax({
                url: '/delete_expense/' + expenseID,
                type: 'DELETE',
                success: function(response){
                    alert(response.status);
                    window.location.reload(); 
                },
                error: function(xhr, status, error){
                    let errorMsg = 'Error deleting expense';
                    if (xhr.responseJSON && xhr.responseJSON.status) {
                        errorMsg = xhr.responseJSON.status;
                    }
                    alert(errorMsg);
                }        
            });
        }
    });
});