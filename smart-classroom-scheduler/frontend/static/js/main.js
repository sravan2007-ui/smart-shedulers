// Main JavaScript file for Smart Classroom Scheduler

// Global variables
let currentEntity = null;
let currentData = [];

// Initialize when document is ready
$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Add fade-in animation to cards
    $('.card').addClass('fade-in');
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut();
    }, 5000);
});

// Notification System
let notifications = JSON.parse(localStorage.getItem('notifications') || '[]');

function showAlert(message, type = 'info') {
    // Add to notification system
    addNotification(message, type);
    
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show position-fixed" role="alert" style="top: 20px; left: 50%; transform: translateX(-50%); z-index: 9999; min-width: 300px; max-width: 500px;">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Remove existing alerts
    $('.alert:not(.flash-message)').remove();
    
    // Add new alert to body
    $('body').append(alertHtml);
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        $('.alert:not(.flash-message)').fadeOut();
    }, 5000);
}

function addNotification(message, type = 'info') {
    const notification = {
        id: Date.now(),
        message: message,
        type: type,
        timestamp: new Date().toISOString(),
        read: false
    };
    
    notifications.unshift(notification);
    
    // Keep only last 50 notifications
    if (notifications.length > 50) {
        notifications = notifications.slice(0, 50);
    }
    
    localStorage.setItem('notifications', JSON.stringify(notifications));
    updateNotificationUI();
}

function updateNotificationUI() {
    const unreadCount = notifications.filter(n => !n.read).length;
    const badge = document.getElementById('notificationCount');
    const list = document.getElementById('notificationList');
    
    if (badge) {
        badge.textContent = unreadCount;
        badge.style.display = unreadCount > 0 ? 'block' : 'none';
    }
    
    if (list) {
        if (notifications.length === 0) {
            list.innerHTML = `
                <div class="no-notifications">
                    <i class="fas fa-bell-slash"></i>
                    <p>No notifications</p>
                </div>
            `;
        } else {
            list.innerHTML = notifications.map(notification => `
                <div class="notification-item ${notification.read ? 'read' : 'unread'}" data-id="${notification.id}">
                    <div class="notification-icon">
                        <i class="fas ${getNotificationIcon(notification.type)}"></i>
                    </div>
                    <div class="notification-content">
                        <div class="notification-message">${notification.message}</div>
                        <div class="notification-time">${formatNotificationTime(notification.timestamp)}</div>
                    </div>
                    <button class="notification-close" onclick="removeNotification(${notification.id})">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `).join('');
        }
    }
}

function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'fa-check-circle';
        case 'danger': return 'fa-exclamation-triangle';
        case 'warning': return 'fa-exclamation-circle';
        case 'info': return 'fa-info-circle';
        default: return 'fa-bell';
    }
}

function formatNotificationTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
}

function toggleNotificationPanel() {
    const panel = document.getElementById('notificationPanel');
    const isOpen = panel.classList.contains('open');
    
    if (isOpen) {
        panel.classList.remove('open');
    } else {
        panel.classList.add('open');
        // Mark all notifications as read
        notifications.forEach(n => n.read = true);
        localStorage.setItem('notifications', JSON.stringify(notifications));
        updateNotificationUI();
    }
}

function removeNotification(id) {
    notifications = notifications.filter(n => n.id !== id);
    localStorage.setItem('notifications', JSON.stringify(notifications));
    updateNotificationUI();
}

function clearAllNotifications() {
    notifications = [];
    localStorage.setItem('notifications', JSON.stringify(notifications));
    updateNotificationUI();
    document.getElementById('notificationPanel').classList.remove('open');
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return false;
    }
    return true;
}

// Generic CRUD Functions
function loadEntityData(entityType, callback) {
    $.get(`/api/${entityType}`, function(data) {
        currentData = data;
        if (callback) callback(data);
    }).fail(function() {
        showAlert(`Error loading ${entityType}!`, 'danger');
    });
}

function saveEntity(entityType, formData, callback) {
    $.ajax({
        url: `/api/${entityType}`,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            if (response.success) {
                showAlert(`${capitalizeFirst(entityType.slice(0, -1))} added successfully!`, 'success');
                if (callback) callback();
            }
        },
        error: function() {
            showAlert(`Error adding ${entityType.slice(0, -1)}!`, 'danger');
        }
    });
}

function updateEntity(entityType, id, formData, callback) {
    $.ajax({
        url: `/api/${entityType}/${id}`,
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            if (response.success) {
                showAlert(`${capitalizeFirst(entityType.slice(0, -1))} updated successfully!`, 'success');
                if (callback) callback();
            }
        },
        error: function() {
            showAlert(`Error updating ${entityType.slice(0, -1)}!`, 'danger');
        }
    });
}

function deleteEntity(entityType, id, callback) {
    if (confirm(`Are you sure you want to delete this ${entityType.slice(0, -1)}?`)) {
        $.ajax({
            url: `/api/${entityType}/${id}`,
            method: 'DELETE',
            success: function(response) {
                if (response.success) {
                    showAlert(`${capitalizeFirst(entityType.slice(0, -1))} deleted successfully!`, 'success');
                    if (callback) callback();
                }
            },
            error: function() {
                showAlert(`Error deleting ${entityType.slice(0, -1)}!`, 'danger');
            }
        });
    }
}

// Table utilities
function createActionButtons(entityType, id) {
    return `
        <button class="btn btn-sm btn-outline-primary me-1" onclick="edit${capitalizeFirst(entityType.slice(0, -1))}(${id})" title="Edit">
            <i class="fas fa-edit"></i>
        </button>
        <button class="btn btn-sm btn-outline-danger" onclick="delete${capitalizeFirst(entityType.slice(0, -1))}(${id})" title="Delete">
            <i class="fas fa-trash"></i>
        </button>
    `;
}

function createBadge(text, type = 'secondary') {
    return `<span class="badge bg-${type}">${text}</span>`;
}

// Search and filter functions
function initializeSearch(tableId, searchInputId) {
    $(`#${searchInputId}`).on('keyup', function() {
        const value = $(this).val().toLowerCase();
        $(`#${tableId} tbody tr`).filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
        });
    });
}

function initializeFilter(tableId, filterSelectId, columnIndex) {
    $(`#${filterSelectId}`).on('change', function() {
        const value = $(this).val();
        if (value === '') {
            $(`#${tableId} tbody tr`).show();
        } else {
            $(`#${tableId} tbody tr`).each(function() {
                const cellText = $(this).find(`td:eq(${columnIndex})`).text();
                $(this).toggle(cellText.includes(value));
            });
        }
    });
}

// Modal utilities
function resetModal(modalId) {
    $(`#${modalId} form`)[0].reset();
    $(`#${modalId} .was-validated`).removeClass('was-validated');
}

function populateSelect(selectId, data, valueField, textField, placeholder = 'Select...') {
    const select = $(`#${selectId}`);
    select.empty().append(`<option value="">${placeholder}</option>`);
    
    data.forEach(function(item) {
        select.append(`<option value="${item[valueField]}">${item[textField]}</option>`);
    });
}

// Timetable utilities
function createTimetableGrid(schedule, days, timeSlots) {
    const grid = {};
    
    // Initialize grid
    days.forEach(day => {
        grid[day] = {};
        timeSlots.forEach(slot => {
            grid[day][slot] = null;
        });
    });
    
    // Populate grid with schedule data
    schedule.forEach(entry => {
        if (grid[entry.day] && grid[entry.day][entry.time_slot] !== undefined) {
            grid[entry.day][entry.time_slot] = entry;
        }
    });
    
    return grid;
}

function generateTimetableTable(grid, days, timeSlots) {
    let html = `
        <div class="table-responsive">
            <table class="table table-bordered timetable-grid">
                <thead class="table-primary">
                    <tr>
                        <th class="text-center">Time</th>
                        ${days.map(day => `<th class="text-center">${day}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
    `;
    
    timeSlots.forEach(timeSlot => {
        html += `<tr><td class="fw-bold text-center align-middle">${timeSlot}</td>`;
        
        days.forEach(day => {
            const entry = grid[day][timeSlot];
            if (entry) {
                const cellClass = entry.is_fixed ? 'timetable-cell fixed-slot' : 'timetable-cell';
                html += `
                    <td class="${cellClass}">
                        <div class="subject-name">${entry.subject_name}</div>
                        <div class="subject-code">${entry.subject_code}</div>
                        <div class="faculty-name"><i class="fas fa-user"></i> ${entry.faculty_name}</div>
                        <div class="classroom-name"><i class="fas fa-door-open"></i> ${entry.classroom_name}</div>
                        ${entry.is_fixed ? '<div class="fixed-indicator"><i class="fas fa-lock"></i> Fixed</div>' : ''}
                    </td>
                `;
            } else {
                html += '<td class="timetable-cell empty-slot">-</td>';
            }
        });
        
        html += '</tr>';
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    return html;
}

// Export functions
function exportToCSV(data, filename) {
    const csv = convertArrayToCSV(data);
    downloadCSV(csv, filename);
}

function convertArrayToCSV(data) {
    if (!data || !data.length) return '';
    
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
    ].join('\n');
    
    return csvContent;
}

function downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Print functions
function printTimetable(elementId) {
    const printContent = document.getElementById(elementId).innerHTML;
    const originalContent = document.body.innerHTML;
    
    document.body.innerHTML = `
        <html>
            <head>
                <title>Timetable</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    @media print {
                        .timetable-grid { font-size: 12px; }
                        .timetable-cell { padding: 8px; }
                        .subject-name { font-weight: bold; }
                        .no-print { display: none; }
                    }
                </style>
            </head>
            <body>
                ${printContent}
            </body>
        </html>
    `;
    
    window.print();
    document.body.innerHTML = originalContent;
    location.reload();
}

// Local storage utilities
function saveToLocalStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
    } catch (e) {
        console.error('Error saving to localStorage:', e);
    }
}

function getFromLocalStorage(key) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : null;
    } catch (e) {
        console.error('Error reading from localStorage:', e);
        return null;
    }
}

// Theme utilities
function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.body.setAttribute('data-theme', newTheme);
    saveToLocalStorage('theme', newTheme);
}

function initializeTheme() {
    const savedTheme = getFromLocalStorage('theme') || 'light';
    document.body.setAttribute('data-theme', savedTheme);
}

// Initialize theme on page load
$(document).ready(function() {
    initializeTheme();
    initializeSidebar();
});

// Sidebar functionality
function initializeSidebar() {
    // Toggle sidebar on desktop
    $('#sidebarToggle').on('click', function() {
        $('#sidebar').toggleClass('collapsed');
        $('#mainContent').toggleClass('expanded');
    });
    
    // Mobile sidebar toggle
    $('#mobileSidebarToggle').on('click', function() {
        $('#sidebar').toggleClass('open');
    });
    
    // Submenu toggle
    $('.submenu-toggle').on('click', function(e) {
        e.preventDefault();
        $(this).parent().toggleClass('open');
    });
    
    // Set active navigation item
    setActiveNavItem();
}

function setActiveNavItem() {
    const currentPath = window.location.pathname;
    $('.nav-link').removeClass('active');
    
    $('.nav-link').each(function() {
        const href = $(this).attr('href');
        if (href && currentPath.includes(href) && href !== '/') {
            $(this).addClass('active');
        }
    });
    
    // Dashboard special case
    if (currentPath === '/' || currentPath === '/dashboard') {
        $('a[href="/dashboard"]').addClass('active');
    }
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    // Only show alert for critical errors, not minor ones
    if (e.error && e.error.message && 
        !e.error.message.includes('Non-Error promise rejection') &&
        !e.error.message.includes('Script error') &&
        !e.error.message.includes('ResizeObserver loop limit exceeded')) {
        console.warn('Showing error alert for:', e.error.message);
        showAlert(`JavaScript Error: ${e.error.message}`, 'danger');
    }
});

// AJAX error handling
$(document).ajaxError(function(event, xhr, settings, thrownError) {
    console.error('AJAX Error:', xhr.status, xhr.responseText, settings.url);
    
    if (xhr.status === 401) {
        showAlert('Session expired. Please login again.', 'warning');
        setTimeout(() => {
            window.location.href = '/login';
        }, 2000);
    } else if (xhr.status === 500) {
        let errorMsg = 'Server error. Please try again later.';
        try {
            const response = JSON.parse(xhr.responseText);
            if (response.error) {
                errorMsg = response.error;
            }
        } catch (e) {
            // Use default message
        }
        showAlert(errorMsg, 'danger');
    } else if (xhr.status === 0) {
        showAlert('Network error. Please check your connection.', 'danger');
    } else if (xhr.status === 400) {
        let errorMsg = 'Bad request. Please check your input.';
        try {
            const response = JSON.parse(xhr.responseText);
            if (response.error) {
                errorMsg = response.error;
            }
        } catch (e) {
            // Use default message
        }
        showAlert(errorMsg, 'warning');
    }
});

// Keyboard shortcuts
$(document).keydown(function(e) {
    // Ctrl+S to save (prevent default browser save)
    if (e.ctrlKey && e.which === 83) {
        e.preventDefault();
        const activeModal = $('.modal.show');
        if (activeModal.length) {
            const saveButton = activeModal.find('.btn-primary').last();
            if (saveButton.length) {
                saveButton.click();
            }
        }
    }
    
    // Escape to close modals
    if (e.which === 27) {
        $('.modal.show').modal('hide');
    }
});

// Auto-save functionality for forms
function enableAutoSave(formId, storageKey) {
    const form = $(`#${formId}`);
    
    // Load saved data
    const savedData = getFromLocalStorage(storageKey);
    if (savedData) {
        Object.keys(savedData).forEach(key => {
            const field = form.find(`[name="${key}"]`);
            if (field.length) {
                field.val(savedData[key]);
            }
        });
    }
    
    // Save on input change
    form.on('input change', function() {
        const formData = {};
        form.find('input, select, textarea').each(function() {
            const field = $(this);
            formData[field.attr('name')] = field.val();
        });
        saveToLocalStorage(storageKey, formData);
    });
    
    // Clear saved data on successful submit
    form.on('submit', function() {
        localStorage.removeItem(storageKey);
    });
}
