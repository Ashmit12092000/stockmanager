// Global JavaScript for Stock Management System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Auto-dismiss alerts after 5 seconds
    autoDismissAlerts();
    
    // Confirmation dialogs for dangerous actions
    setupConfirmationDialogs();
    
    // Stock balance checking
    setupStockBalanceChecking();
    
    // Form validation enhancements
    enhanceFormValidation();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Auto-dismiss alert messages
function autoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });
}

// Setup confirmation dialogs for dangerous actions
function setupConfirmationDialogs() {
    // Delete confirmations
    const deleteLinks = document.querySelectorAll('a[href*="delete"], button[data-action="delete"]');
    deleteLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // Submit confirmations
    const submitButtons = document.querySelectorAll('button[data-confirm], a[data-confirm]');
    submitButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure you want to proceed?';
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

// Stock balance checking for issue forms
function setupStockBalanceChecking() {
    const itemSelects = document.querySelectorAll('select[name*="item_id"]');
    const locationSelects = document.querySelectorAll('select[name*="location_id"]');
    
    function checkStockBalance(itemSelect, locationSelect) {
        const itemId = itemSelect.value;
        const locationId = locationSelect.value;
        
        if (itemId && locationId) {
            fetch(`/api/stock_balance/${itemId}/${locationId}`)
                .then(response => response.json())
                .then(data => {
                    showStockBalance(itemSelect.closest('form'), data.balance);
                })
                .catch(error => {
                    console.error('Error fetching stock balance:', error);
                });
        }
    }
    
    itemSelects.forEach(function(select) {
        select.addEventListener('change', function() {
            const form = this.closest('form');
            const locationSelect = form.querySelector('select[name*="location_id"]');
            if (locationSelect) {
                checkStockBalance(this, locationSelect);
            }
        });
    });
    
    locationSelects.forEach(function(select) {
        select.addEventListener('change', function() {
            const form = this.closest('form');
            const itemSelect = form.querySelector('select[name*="item_id"]');
            if (itemSelect) {
                checkStockBalance(itemSelect, this);
            }
        });
    });
}

// Show stock balance information
function showStockBalance(form, balance) {
    // Remove existing stock info
    const existingInfo = form.querySelector('.stock-balance-info');
    if (existingInfo) {
        existingInfo.remove();
    }
    
    // Create new stock info element
    const stockInfo = document.createElement('div');
    stockInfo.className = 'stock-balance-info alert mt-2';
    
    if (balance === 0) {
        stockInfo.className += ' alert-danger';
        stockInfo.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i><strong>Out of Stock!</strong> No items available at this location.';
    } else if (balance <= 5) {
        stockInfo.className += ' alert-warning';
        stockInfo.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i><strong>Low Stock:</strong> Only ${balance} items available.`;
    } else {
        stockInfo.className += ' alert-info';
        stockInfo.innerHTML = `<i class="fas fa-info-circle me-2"></i><strong>Available:</strong> ${balance} items in stock.`;
    }
    
    // Insert after location select
    const locationSelect = form.querySelector('select[name*="location_id"]');
    if (locationSelect) {
        locationSelect.closest('.mb-3').appendChild(stockInfo);
    }
}

// Enhanced form validation
function enhanceFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            // Validate quantity fields
            const quantityInputs = form.querySelectorAll('input[type="number"][name*="quantity"]');
            let hasError = false;
            
            quantityInputs.forEach(function(input) {
                const value = parseInt(input.value);
                if (value <= 0) {
                    showFieldError(input, 'Quantity must be greater than 0');
                    hasError = true;
                } else {
                    clearFieldError(input);
                }
            });
            
            if (hasError) {
                e.preventDefault();
                return false;
            }
        });
    });
}

// Show field error
function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

// Clear field error
function clearFieldError(field) {
    field.classList.remove('is-invalid');
    
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Utility function to format numbers
function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

// Utility function to format dates
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Search functionality enhancement
function enhanceSearch() {
    const searchInputs = document.querySelectorAll('input[type="search"], input[placeholder*="Search"]');
    
    searchInputs.forEach(function(input) {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                // Implement live search if needed
                performLiveSearch(this.value, this.closest('form'));
            }, 300);
        });
    });
}

// Live search implementation (if needed)
function performLiveSearch(query, form) {
    // This can be implemented for real-time search functionality
    // For now, we'll just submit the form after a delay
    if (query.length >= 3 || query.length === 0) {
        // form.submit();
    }
}

// Table sorting functionality
function makeSortable(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const headers = table.querySelectorAll('th');
    headers.forEach((header, index) => {
        if (header.textContent.trim() !== 'Actions') {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => sortTable(table, index));
        }
    });
}

// Sort table by column
function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    // Determine if column contains numbers
    const firstCellText = rows[0]?.cells[columnIndex]?.textContent.trim();
    const isNumeric = !isNaN(parseFloat(firstCellText)) && isFinite(firstCellText);
    
    rows.sort((a, b) => {
        const aVal = a.cells[columnIndex].textContent.trim();
        const bVal = b.cells[columnIndex].textContent.trim();
        
        if (isNumeric) {
            return parseFloat(bVal) - parseFloat(aVal);
        } else {
            return aVal.localeCompare(bVal);
        }
    });
    
    rows.forEach(row => tbody.appendChild(row));
}

// Initialize additional features when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    enhanceSearch();
    
    // Make main tables sortable
    makeSortable('itemsTable');
    makeSortable('stockTable');
    makeSortable('requestsTable');
});

// Export functions for global use
window.StockManagement = {
    formatNumber: formatNumber,
    formatDate: formatDate,
    showStockBalance: showStockBalance,
    makeSortable: makeSortable
};
