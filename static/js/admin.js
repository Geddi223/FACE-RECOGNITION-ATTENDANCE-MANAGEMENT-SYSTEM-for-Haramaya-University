
document.addEventListener('DOMContentLoaded', function() {
    // Scroll effect for navbar
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 10) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Dark mode toggle
    const darkModeSwitch = document.getElementById('darkModeSwitch');
    const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Check for saved user preference or use system preference
    if (localStorage.getItem('darkMode') === 'enabled' || 
        (localStorage.getItem('darkMode') !== 'disabled' && darkModeMediaQuery.matches)) {
        document.body.classList.add('dark-mode');
        darkModeSwitch.checked = true;
    }

    darkModeSwitch.addEventListener('change', function() {
        if (this.checked) {
            document.body.classList.add('dark-mode');
            localStorage.setItem('darkMode', 'enabled');
        } else {
            document.body.classList.remove('dark-mode');
            localStorage.setItem('darkMode', 'disabled');
        }
    });

    // Language selector functionality
    const languageOptions = document.querySelectorAll('.language-option');
    languageOptions.forEach(option => {
        option.addEventListener('click', function(e) {
            e.preventDefault();
            const lang = this.getAttribute('data-lang');
            document.getElementById('current-language').textContent = this.textContent;
            // Here you would typically implement language change logic
            console.log('Language changed to:', lang);
        });
    });

    // Search functionality
    const searchInput = document.getElementById('globalSearch');
    searchInput.addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            // Implement search functionality here
            console.log('Searching for:', this.value);
        }
    });

    // Simulate loading notifications
    
document.addEventListener('DOMContentLoaded', function() {
    // Load initial payroll data
    loadPayrollData();
    
    // Set up event listeners
    document.getElementById('processPayrollBtn').addEventListener('click', processPayroll);
    document.getElementById('newPayrollBtn').addEventListener('click', createNewPayroll);
    document.getElementById('recalculatePayrollBtn').addEventListener('click', recalculatePayroll);
    document.getElementById('exportPayrollBtn').addEventListener('click', exportPayroll);
    document.getElementById('emailSummaryBtn').addEventListener('click', emailPayrollSummary);
    document.getElementById('printPayslipBtn').addEventListener('click', printPayslip);
    document.getElementById('emailPayslipBtn').addEventListener('click', emailCurrentPayslip);
    document.getElementById('printModalPayslipBtn').addEventListener('click', printModalPayslip);
    document.getElementById('emailModalPayslipBtn').addEventListener('click', emailModalPayslip);
    
    // Set up period selector change handler
    document.getElementById('payrollPeriod').addEventListener('change', function() {
        loadPayrollData(this.value);
    });
});

function loadPayrollData(period = 'current') {
    const tableBody = document.querySelector('#payrollTable tbody');
    const loadingRow = tableBody.querySelector('.text-center');
    
    // Show loading state
    loadingRow.style.display = '';
    
    fetch(`/api/payroll?period=${period}`)
        .then(response => response.json())
        .then(data => {
            // Hide loading row
            loadingRow.style.display = 'none';
            
            // Update payroll table
            updatePayrollTable(data.employees);
            
            // Update summary information
            updatePayrollSummary(data.summary);
            
            // Update recent payslips
            updateRecentPayslips(data.recentPayslips);
            
            // Update pagination info
            document.getElementById('showingCount').textContent = data.employees.length;
            document.getElementById('totalCount').textContent = data.summary.totalEmployees;
        })
        .catch(error => {
            console.error('Error loading payroll data:', error);
            loadingRow.innerHTML = `
                <div class="text-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Failed to load payroll data. Please try again.
                </div>
            `;
        });
}

function updatePayrollTable(employees) {
    const tableBody = document.querySelector('#payrollTable tbody');
    tableBody.innerHTML = '';
    
    employees.forEach(employee => {
        const row = document.createElement('tr');
        row.innerHTML = 
            <td>
                <div class="d-flex align-items-center">
                    <div class="avatar avatar-sm me-2 bg-primary">${employee.initials}</div>
                    <div>${employee.name}</div>
                </div>
            </td>
            <td>ETB ${employee.basicSalary.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
            <td>ETB ${employee.allowances.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
            <td>ETB ${employee.deductions.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
            <td class="fw-bold">ETB ${employee.netPay.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
            <td>
                <span class="badge ${getStatusBadgeClass(employee.status)}">
                    ${employee.status}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-outline-primary view-payslip" data-id="${employee.id}">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-outline-success ms-1 email-payslip" data-id="${employee.id}">
                    <i class="fas fa-envelope"></i>
                </button>
            </td>
        ;
        tableBody.appendChild(row);
    });
    
    // Add event listeners to action buttons
    document.querySelectorAll('.view-payslip').forEach(btn => {
        btn.addEventListener('click', function() {
            viewPayslip(this.dataset.id);
        });
    });
    
    document.querySelectorAll('.email-payslip').forEach(btn => {
        btn.addEventListener('click', function() {
            emailPayslip(this.dataset.id);
        });
    });
}

function updatePayrollSummary(summary) {
    document.getElementById('totalEmployees').textContent = summary.totalEmployees.toLocaleString();
    document.getElementById('payrollTotal').textContent = `ETB ${summary.totalPayroll.toLocaleString('en-US', {minimumFractionDigits: 2})`;
    document.getElementById('basicSalaryTotal').textContent = `ETB ${summary.basicSalary.toLocaleString('en-US', {minimumFractionDigits: 2})`;
    document.getElementById('allowancesTotal').textContent = `ETB ${summary.allowances.toLocaleString('en-US', {minimumFractionDigits: 2})`;
    document.getElementById('deductionsTotal').textContent = `ETB ${summary.deductions.toLocaleString('en-US', {minimumFractionDigits: 2})`;
    document.querySelector('#basicSalaryProgress .progress-bar').style.width = `${summary.basicPercentage}%`;
    document.querySelector('#allowancesProgress .progress-bar').style.width = `${summary.allowancesPercentage}%`;
    document.querySelector('#deductionsProgress .progress-bar').style.width = `${summary.deductionsPercentage}%`;
}

function updateRecentPayslips(payslips) {
    const container = document.getElementById('recentPayslips');
    container.innerHTML = '';
    
    payslips.slice(0, 3).forEach(payslip => {
        const item = document.createElement('div');
        item.className = 'payroll-item p-3 bg-light rounded mb-2';
        item.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <strong>${payslip.employeeName}</strong>
                <span class="text-success">ETB ${payslip.netPay.toLocaleString('en-US', {minimumFractionDigits: 2})}</span>
            </div>
            <div class="d-flex justify-content-between text-muted small">
                <span>${payslip.period}</span>
                <span class="${getStatusClass(payslip.status)}">${payslip.status}</span>
            </div>
        `;
        container.appendChild(item);
    });
    
    if (payslips.length === 0) {
        container.innerHTML = `
            <div class="text-center py-2 text-muted">
                <i class="fas fa-inbox fa-2x mb-2"></i>
                <p>No recent payslips found</p>
            </div>
        `;
    }
}

function getStatusClass(status) {
    switch (status.toLowerCase()) {
        case 'paid': return 'status-paid';
        case 'pending': return 'status-pending';
        case 'processing': return 'status-processing';
        case 'rejected': return 'status-rejected';
        default: return 'status-pending';
    }
}

function getStatusBadgeClass(status) {
    switch (status.toLowerCase()) {
        case 'paid': return 'bg-success';
        case 'pending': return 'bg-warning';
        case 'processing': return 'bg-info';
        case 'rejected': return 'bg-danger';
        default: return 'bg-secondary';
    }
}

function processPayroll() {
    const period = document.getElementById('payrollPeriod').value;
    const paymentDate = document.getElementById('paymentDate').value;
    
    // Show processing overlay
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay d-flex align-items-center justify-content-center';
    overlay.innerHTML = `
        <div class="text-center bg-white p-4 rounded shadow-sm">
            <div class="spinner-border text-primary mb-3" role="status"></div>
            <h5 class="mb-1">Processing Payroll</h5>
            <p class="mb-0 text-muted">Please wait while we process payroll for ${period}</p>
        </div>
    `;
    document.querySelector('.card-body').appendChild(overlay);
    
    // Simulate API call
    setTimeout(() => {
        overlay.remove();
        showToast('Payroll processed successfully!', 'success');
        loadPayrollData(period);
    }, 3000);
}

// Other payroll functions would be defined here...
function createNewPayroll() {
    // Implementation for creating new payroll
    console.log('Creating new payroll...');
}

function recalculatePayroll() {
    // Implementation for recalculating payroll
    console.log('Recalculating payroll...');
}

function exportPayroll() {
    // Implementation for exporting payroll
    console.log('Exporting payroll data...');
}

function emailPayrollSummary() {
    // Implementation for emailing payroll summary
    console.log('Emailing payroll summary...');
}

function printPayslip() {
    // Implementation for printing payslip
    console.log('Printing payslip...');
}

function emailCurrentPayslip() {
    // Implementation for emailing current payslip
    console.log('Emailing current payslip...');
}

function printModalPayslip() {
    // Implementation for printing modal payslip
    console.log('Printing modal payslip...');
}

function emailModalPayslip() {
    // Implementation for emailing modal payslip
    console.log('Emailing modal payslip...');
}

function viewPayslip(employeeId) {
    fetch(`/api/payroll/payslip/${employeeId}`)
        .then(response => response.json())
        .then(data => {
            displayPayslipModal(data);
        })
        .catch(error => {
            console.error('Error loading payslip:', error);
            showToast('Failed to load payslip', 'danger');
        });
}

function displayPayslipModal(payslip) {
    const modal = new bootstrap.Modal(document.getElementById('payslipModal'));
    const modalBody = document.getElementById('payslipModalBody');
    
    modalBody.innerHTML = `
        <div class="payslip-container">
            <!-- Payslip content similar to the static one would be generated here -->
            <div class="payslip-header">
                <div class="row">
                    <div class="col-md-6">
                        <h2 class="mb-1">${payslip.company.name}</h2>
                        <p class="text-muted mb-0">${payslip.company.address}</p>
                    </div>
                    <div class="col-md-6 text-md-end">
                        <h3 class="text-payroll mb-1">PAYSLIP</h3>
                        <p class="mb-0"><strong>Period:</strong> ${payslip.period}</p>
                        <p class="mb-0"><strong>Payment Date:</strong> ${payslip.paymentDate}</p>
                        <p class="mb-0"><strong>Payslip #:</strong> ${payslip.payslipNumber}</p>
                    </div>
                </div>
            </div>
            <!-- Rest of the payslip content would be dynamically generated -->
        </div>
    `;
    
    modal.show();
}

function emailPayslip(employeeId) {
    fetch(`/api/payroll/email-payslip/${employeeId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Payslip emailed successfully!', 'success');
        } else {
            showToast('Failed to email payslip', 'danger');
        }
    })
    .catch(error => {
        console.error('Error emailing payslip:', error);
        showToast('Error sending email', 'danger');
    });
}

function showToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it hides
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '11';
    document.body.appendChild(container);
    return container;
}


    document.addEventListener("DOMContentLoaded", function() {
        // ===== DARK MODE TOGGLE =====
        const darkModeSwitch = document.getElementById('darkModeSwitch');
        
        // Load saved preference
        if (localStorage.getItem('darkMode') === 'enabled') {
            document.documentElement.setAttribute('data-theme', 'dark');
            darkModeSwitch.checked = true;
        }
    
        // Toggle handler
        darkModeSwitch.addEventListener('change', function() {
            if (this.checked) {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('darkMode', 'enabled');
            } else {
                document.documentElement.removeAttribute('data-theme');
                localStorage.setItem('darkMode', 'disabled');
            }
        });

    document.addEventListener('DOMContentLoaded', function() {
        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    
        // Load recent activities
        
        // Attendance table filtering
    document.addEventListener('DOMContentLoaded', function() {
        // Update last updated time
        function updateLastUpdated() {
            const now = new Date();
            document.getElementById('lastUpdated').textContent = now.toLocaleTimeString();
        }
        setInterval(updateLastUpdated, 60000);
        
        // Add animation to cards
        const cards = document.querySelectorAll('.stat-card');
        cards.forEach((card, index) => {
            card.classList.add('fade-in', `delay-${index + 1}`);
        });
        
        // Tooltip initialization
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    });
    // Chart variables
    var attendanceChart, departmentChart;
    
    
    
    
        
        // Update current week label
        const currentWeek = weeks.find(w => w.offset === currentWeekOffset);
        if (currentWeek) {
            $('#currentWeekLabel').text(currentWeek.label);
        }
    }
    
    
    
    function loadDepartmentData(filter = 'all') {
        // Show loading state
        $('#departmentChart').closest('.card-body').find('.loading-overlay').show();
        
        $.ajax({
            url: '/api/departments/distribution',
            type: 'GET',
            data: { filter: filter },
            dataType: 'json',
            success: function(response) {
                updateDepartmentChart(response.data);
                updateDepartmentLegend(response.data);
            },
            error: function(xhr) {
                console.error('Error loading department data:', xhr.responseText);
                showToast('Failed to load department data', 'danger');
            },
            complete: function() {
                $('#departmentChart').closest('.card-body').find('.loading-overlay').hide();
            }
        });
    }
    
    
    function updateDepartmentLegend(data) {
        const legendContainer = $('#departmentLegend');
        legendContainer.empty();
        
        data.forEach((dept, index) => {
            const color = departmentColors[index % departmentColors.length];
            const percentage = Math.round((dept.count / data.reduce((sum, d) => sum + d.count, 0)) * 100;
            
            legendContainer.append(`
                <div class="dept-legend-item">
                    <div class="dept-color" style="background-color: ${color};"></div>
                    <div class="dept-name">${dept.name}</div>
                    <div class="dept-count">${dept.count}</div>
                    <div class="dept-percentage">${percentage}%</div>
                </div>
            `);
        });
    }
    
    function showToast(message, type) {
        const toast = $(`
            <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 11">
                <div class="toast align-items-center text-white bg-${type} border-0 show" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="d-flex">
                        <div class="toast-body">${message}</div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                </div>
            </div>
        `);
        $('body').append(toast);
        setTimeout(() => toast.remove(), 3000);
    }
    
    // Initialize on page load
    $(document).ready(function() {
        // Load initial data
        loadAttendanceData(0);
        loadDepartmentData('all');
        
        // Week selector event
        $(document).on('click', '#weekDropdown a', function(e) {
            e.preventDefault();
            const offset = $(this).data('offset');
            loadAttendanceData(offset);
        });
        
        // Refresh button event
        $('#refreshAttendance').click(function() {
            const currentOffset = $('#weekDropdown a.active').data('offset') || 0;
            loadAttendanceData(currentOffset);
        });
        
        // Department filter events
        $(document).on('click', '#deptFilterDropdown .dropdown-item[data-filter]', function(e) {
            e.preventDefault();
            const filter = $(this).data('filter');
            if (filter === 'export') {
                // Handle export
                console.log('Export department data');
            } else {
                loadDepartmentData(filter);
            }
        });
        
        // Initialize tooltips
        $('[data-bs-toggle="tooltip"]').tooltip();
    });
document.addEventListener("DOMContentLoaded", function() {
    // ===== DARK MODE TOGGLE =====
    const darkModeSwitch = document.getElementById('darkModeSwitch');
    
    // Load saved preference
    if (localStorage.getItem('darkMode') === 'enabled') {
        document.documentElement.setAttribute('data-theme', 'dark');
        darkModeSwitch.checked = true;
    }

    // Toggle handler
    darkModeSwitch.addEventListener('change', function() {
        if (this.checked) {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('darkMode', 'enabled');
        } else {
            document.documentElement.removeAttribute('data-theme');
            localStorage.setItem('darkMode', 'disabled');
        }
    });

    // ===== MULTILINGUAL SUPPORT =====
    const languageOptions = {
        en: {
            universityName: "Haramaya University",
            systemName: "Attendance & Payroll System",
            searchPlaceholder: "Search employees, payroll...",
            notifications: "Notifications",
            profile: "Profile",
            settings: "Settings",
            logout: "Logout",
            payroll: "Payroll",
            processPayroll: "Process Payroll",
            payslips: "Payslips",
            taxSettings: "Tax Settings"
        },
        om: {
            universityName: "Yuunivarsiitii Haramayaa",
            systemName: "Sirna Sagantaa fi Kaffaltii Misha",
            searchPlaceholder: "Hojjettoota, kaffaltii...",
            notifications: "Beeksisaawwan",
            profile: "Profile",
            settings: "Settings",
            logout: "Ba'i",
            payroll: "Kaffaltii",
            processPayroll: "Kaffaltii Hojjedhu",
            payslips: "Baatii Kaffaltii",
            taxSettings: "Saagiin Saamichaa"
        },
        am: {
            universityName: "የሀረማያ ዩኒቨርሲቲ",
            systemName: "የመገኘት እና ደመወዝ ስርዓት",
            searchPlaceholder: "ሰራተኞች፣ ደመወዝ...",
            notifications: "ማስታወቂያዎች",
            profile: "መገለጫ",
            settings: "ቅንብሮች",
            logout: "ውጣ",
            payroll: "ደመወዝ",
            processPayroll: "ደመወዝ ሂደት",
            payslips: "ደመወዝ ደብተር",
            taxSettings: "ታክስ ቅንብሮች"
        }
    };

    // Set language
    function setLanguage(lang) {
        const elements = document.querySelectorAll('[data-i18n]');
        elements.forEach(el => {
            const key = el.getAttribute('data-i18n');
            el.textContent = languageOptions[lang][key] || el.textContent;
        });
        
        // Update placeholders
        const placeholders = document.querySelectorAll('[data-i18n^="[placeholder]"]');
        placeholders.forEach(el => {
            const key = el.getAttribute('data-i18n').replace('[placeholder]', '');
            el.placeholder = languageOptions[lang][key];
        });

        // Update UI labels
        document.getElementById('university-name').textContent = languageOptions[lang].universityName;
        document.getElementById('system-name').textContent = languageOptions[lang].systemName;
        document.getElementById('current-language').textContent = 
            lang === 'en' ? 'English' : lang === 'om' ? 'Afaan Oromoo' : 'አማርኛ';
        
        // Update payroll dropdown labels if exists
        const payrollDropdown = document.getElementById('payrollDropdown');
        if (payrollDropdown) {
            payrollDropdown.innerHTML = `
                <i class="fas fa-money-bill-wave me-2"></i>${languageOptions[lang].payroll}
            `;
        }
        
        localStorage.setItem('language', lang);
    }

    // Initialize language
    const savedLang = localStorage.getItem('language') || 'en';
    setLanguage(savedLang);

    // Language selector
    document.querySelectorAll('.language-option').forEach(option => {
        option.addEventListener('click', function(e) {
            e.preventDefault();
            const lang = this.getAttribute('data-lang');
            setLanguage(lang);
        });
    });

    // ===== SEARCH FUNCTIONALITY =====
    document.getElementById('globalSearch').addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            window.location.href = `/search?q=${encodeURIComponent(this.value)}`;
        }
    });

    // ===== PAYROLL FUNCTIONALITY =====
    // Initialize payroll charts if on payroll page
    if (document.getElementById('payrollChart')) {
        initializePayrollCharts();
    }

    // Process payroll button handler
    const processPayrollBtn = document.getElementById('processPayrollBtn');
    if (processPayrollBtn) {
        processPayrollBtn.addEventListener('click', function() {
            const payrollPeriod = document.getElementById('payrollPeriod').value;
            const paymentDate = document.getElementById('paymentDate').value;
            
            // Show loading state
            const overlay = document.createElement('div');
            overlay.className = 'loading-overlay d-flex align-items-center justify-content-center';
            overlay.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border text-primary mb-2" role="status"></div>
                    <p>Processing payroll for ${payrollPeriod}...</p>
                </div>
            `;
            document.querySelector('.payroll-processing-container').appendChild(overlay);

            // Simulate processing (replace with actual API call)
            setTimeout(() => {
                overlay.remove();
                showToast('Payroll processed successfully!', 'success');
                // Refresh payroll data
                if (typeof loadPayrollData === 'function') {
                    loadPayrollData();
                }
            }, 3000);
        });
    }

    // Payslip email button handler
    const emailPayslipBtn = document.getElementById('emailPayslipBtn');
    if (emailPayslipBtn) {
        emailPayslipBtn.addEventListener('click', function() {
            // Get employee ID from data attribute or form
            const employeeId = this.dataset.employeeId || document.getElementById('employeeId').value;
            
            fetch('/api/payroll/email-payslip', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ employeeId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('Payslip emailed successfully!', 'success');
                } else {
                    showToast('Failed to email payslip', 'danger');
                }
            })
            .catch(error => {
                console.error('Error emailing payslip:', error);
                showToast('Error sending email', 'danger');
            });
        });
    }
});

// Initialize payroll charts
function initializePayrollCharts() {
    // Payroll summary chart
    const payrollCtx = document.getElementById('payrollChart').getContext('2d');
    const payrollChart = new Chart(payrollCtx, {
        type: 'bar',
        data: {
            labels: ['Basic Salary', 'Allowances', 'Bonuses', 'Deductions', 'Net Pay'],
            datasets: [{
                label: 'Amount (ETB)',
                data: [1200000, 250000, 150000, 180000, 1420000],
                backgroundColor: [
                    '#4e73df',
                    '#1cc88a',
                    '#f6c23e',
                    '#e74a3b',
                    '#36b9cc'
                ],
                borderColor: [
                    '#4e73df',
                    '#1cc88a',
                    '#f6c23e',
                    '#e74a3b',
                    '#36b9cc'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `ETB ${context.raw.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return `ETB ${value.toLocaleString()}`;
                        }
                    }
                }
            }
        }
    });

    // Department distribution chart
    const deptCtx = document.getElementById('departmentPayrollChart').getContext('2d');
    const deptChart = new Chart(deptCtx, {
        type: 'doughnut',
        data: {
            labels: ['Academic', 'Administration', 'Finance', 'HR', 'IT', 'Maintenance'],
            datasets: [{
                data: [800000, 250000, 150000, 120000, 100000, 75000],
                backgroundColor: [
                    '#4e73df',
                    '#1cc88a',
                    '#36b9cc',
                    '#f6c23e',
                    '#e74a3b',
                    '#858796'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ETB ${value.toLocaleString()} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Load payroll data
function loadPayrollData(period = 'current') {
    fetch(`/api/payroll?period=${period}`)
        .then(response => response.json())
        .then(data => {
            updatePayrollTable(data.employees);
            updatePayrollSummary(data.summary);
        })
        .catch(error => {
            console.error('Error loading payroll data:', error);
            showToast('Failed to load payroll data', 'danger');
        });
}

// Update payroll table
function updatePayrollTable(employees) {
    const tableBody = document.querySelector('#payrollTable tbody');
    tableBody.innerHTML = '';
    
    employees.forEach(employee => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <div class="d-flex align-items-center">
                    <div class="avatar avatar-sm me-2 bg-primary">${employee.initials}</div>
                    <div>${employee.name}</div>
                </div>
            </td>
            <td>ETB ${employee.basicSalary.toLocaleString()}</td>
            <td>ETB ${employee.allowances.toLocaleString()}</td>
            <td>ETB ${employee.deductions.toLocaleString()}</td>
            <td class="fw-bold">ETB ${employee.netPay.toLocaleString()}</td>
            <td>
                <span class="badge ${getStatusBadgeClass(employee.status)}">
                    ${employee.status}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-outline-primary view-payslip" data-id="${employee.id}">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-outline-success ms-1 email-payslip" data-id="${employee.id}">
                    <i class="fas fa-envelope"></i>
                </button>
            </td>
        `;
        tableBody.appendChild(row);
    });
    
    // Add event listeners to action buttons
    document.querySelectorAll('.view-payslip').forEach(btn => {
        btn.addEventListener('click', function() {
            viewPayslip(this.dataset.id);
        });
    });
    
    document.querySelectorAll('.email-payslip').forEach(btn => {
        btn.addEventListener('click', function() {
            emailPayslip(this.dataset.id);
        });
    });
}

// Update payroll summary
function updatePayrollSummary(summary) {
    document.getElementById('totalEmployees').textContent = summary.totalEmployees.toLocaleString();
    document.getElementById('payrollTotal').textContent = `ETB ${summary.totalPayroll.toLocaleString()}`;
    document.getElementById('basicSalaryTotal').textContent = `ETB ${summary.basicSalary.toLocaleString()}`;
    document.getElementById('allowancesTotal').textContent = `ETB ${summary.allowances.toLocaleString()}`;
    document.getElementById('deductionsTotal').textContent = `ETB ${summary.deductions.toLocaleString()}`;
    
    // Update progress bars
    document.querySelector('#basicSalaryProgress .progress-bar').style.width = `${summary.basicPercentage}%`;
    document.querySelector('#allowancesProgress .progress-bar').style.width = `${summary.allowancesPercentage}%`;
    document.querySelector('#deductionsProgress .progress-bar').style.width = `${summary.deductionsPercentage}%`;
}

// View payslip
function viewPayslip(employeeId) {
    fetch(`/api/payroll/payslip/${employeeId}`)
        .then(response => response.json())
        .then(data => {
            displayPayslipModal(data);
        })
        .catch(error => {
            console.error('Error loading payslip:', error);
            showToast('Failed to load payslip', 'danger');
        });
}

// Display payslip in modal
function displayPayslipModal(payslip) {
    const modal = new bootstrap.Modal(document.getElementById('payslipModal'));
    const modalBody = document.getElementById('payslipModalBody');
    
    modalBody.innerHTML = `
        <div class="payslip-container">
            <div class="payslip-header">
                <div class="row">
                    <div class="col-md-6">
                        <h2 class="mb-1">Haramaya University</h2>
                        <p class="text-muted mb-0">P.O. Box 138, Dire Dawa, Ethiopia</p>
                    </div>
                    <div class="col-md-6 text-md-end">
                        <h3 class="text-payroll mb-1">PAYSLIP</h3>
                        <p class="mb-0">Period: ${payslip.period}</p>
                        <p class="mb-0">Payment Date: ${payslip.paymentDate}</p>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-md-6">
                    <h5>Employee Information</h5>
                    <p class="mb-1"><strong>Name:</strong> ${payslip.employee.name}</p>
                    <p class="mb-1"><strong>ID:</strong> ${payslip.employee.id}</p>
                    <p class="mb-1"><strong>Department:</strong> ${payslip.employee.department}</p>
                    <p class="mb-1"><strong>Bank:</strong> ${payslip.employee.bank}</p>
                    <p class="mb-1"><strong>Account:</strong> ${payslip.employee.account}</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <h5>Pay Details</h5>
                    <p class="mb-1"><strong>Basic Salary:</strong> ETB ${payslip.earnings.basic.toLocaleString()}</p>
                    <p class="mb-1"><strong>Allowances:</strong> ETB ${payslip.earnings.allowances.toLocaleString()}</p>
                    <p class="mb-1"><strong>Gross Pay:</strong> ETB ${payslip.earnings.gross.toLocaleString()}</p>
                    <p class="mb-1"><strong>Net Pay:</strong> ETB ${payslip.netPay.toLocaleString()}</p>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-md-6">
                    <h5>Earnings</h5>
                    <table class="table table-bordered earnings-table">
                        <thead>
                            <tr>
                                <th>Type</th>
                                <th>Amount</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${Object.entries(payslip.earnings.details).map(([type, amount]) => `
                                <tr>
                                    <td>${type}</td>
                                    <td>ETB ${amount.toLocaleString()}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                <div class="col-md-6">
                    <h5>Deductions</h5>
                    <table class="table table-bordered deductions-table">
                        <thead>
                            <tr>
                                <th>Type</th>
                                <th>Amount</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${Object.entries(payslip.deductions.details).map(([type, amount]) => `
                                <tr>
                                    <td>${type}</td>
                                    <td>ETB ${amount.toLocaleString()}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="payslip-footer mt-4">
                <div class="row">
                    <div class="col-md-6">
                        <p class="mb-1"><strong>Payment Method:</strong> ${payslip.paymentMethod}</p>
                        <p class="mb-1"><strong>Bank:</strong> ${payslip.employee.bank}</p>
                        <p class="mb-1"><strong>Account:</strong> ${payslip.employee.account}</p>
                    </div>
                    <div class="col-md-6 text-md-end">
                        <p class="mb-1"><strong>Total Earnings:</strong> ETB ${payslip.earnings.gross.toLocaleString()}</p>
                        <p class="mb-1"><strong>Total Deductions:</strong> ETB ${payslip.deductions.total.toLocaleString()}</p>
                        <h4 class="text-payroll">Net Pay: ETB ${payslip.netPay.toLocaleString()}</h4>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    modal.show();
}

// Email payslip
function emailPayslip(employeeId) {
    fetch(`/api/payroll/email-payslip/${employeeId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Payslip emailed successfully!', 'success');
        } else {
            showToast('Failed to email payslip', 'danger');
        }
    })
    .catch(error => {
        console.error('Error emailing payslip:', error);
        showToast('Error sending email', 'danger');
    });
}

// Get status badge class
function getStatusBadgeClass(status) {
    switch (status.toLowerCase()) {
        case 'paid': return 'bg-success';
        case 'pending': return 'bg-warning';
        case 'processing': return 'bg-info';
        case 'rejected': return 'bg-danger';
        default: return 'bg-secondary';
    }
}

// Show toast notification
function showToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it hides
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Create toast container if it doesn't exist
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '11';
    document.body.appendChild(container);
    return container;
}

// Initialize settings tabs
document.addEventListener('DOMContentLoaded', function() {
    const settingsTabs = ['general', 'attendance', 'face-recognition', 'roles', 'leave', 'payroll', 'notifications'];
    
    // Load settings when tab changes
    $('a[data-bs-toggle="tab"]').on('shown.bs.tab', function(e) {
        const tabId = $(e.target).attr('href').substring(1);
        loadSettings(tabId);
    });
    
    // Form submission handler
    $('.settings-form').on('submit', function(e) {
        e.preventDefault();
        const formId = $(this).attr('id');
        const tabId = formId.replace('SettingsForm', '');
        const formData = $(this).serializeArray();
        
        // Convert to proper object structure
        let data = {};
        formData.forEach(item => {
            // Handle checkboxes
            if (item.name.endsWith('_checkbox')) {
                const realName = item.name.replace('_checkbox', '');
                data[realName] = item.value === 'on';
            } else {
                data[item.name] = item.value;
            }
        });
        
        // Special handling for JSON fields
        if (tabId === 'attendance') {
            data.overtime_rules = {
                after_hours: $('#overtimeAfter').val(),
                rate: $('#overtimeRate').val()
            };
        }
        
        saveSettings(tabId, data);
    });
    
    // Initialize first tab
    loadSettings(settingsTabs[0]);
});

function loadSettings(tabId) {
    const endpoint = tabId.replace('-', '_');
    fetch(`/api/settings/${endpoint}`)
        .then(response => response.json())
        .then(data => {
            const form = document.getElementById(`${tabId}SettingsForm`);
            if (!form) return;
            
            // Populate form fields
            Object.keys(data).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (!input) return;
                
                if (input.type === 'checkbox') {
                    input.checked = data[key];
                } else {
                    input.value = data[key];
                }
            });
            
            // Special handling for complex fields
            if (tabId === 'attendance' && data.overtime_rules) {
                $('#overtimeAfter').val(data.overtime_rules.after_hours);
                $('#overtimeRate').val(data.overtime_rules.rate);
            }
            
            // Special handling for payroll settings
            if (tabId === 'payroll') {
                if (data.tax_brackets) {
                    initializeTaxBracketsEditor(data.tax_brackets);
                }
            }
        })
        .catch(error => {
            console.error('Error loading settings:', error);
            showToast('Failed to load settings', 'danger');
        });
}

function saveSettings(tabId, data) {
    const endpoint = tabId.replace('-', '_');
    fetch(`/api/settings/${endpoint}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) throw new Error('Save failed');
        return response.json();
    })
    .then(() => {
        showToast('Settings saved successfully!', 'success');
        // Refresh UI if needed
        if (tabId === 'general') {
            updateSystemInfo(data);
        }
    })
    .catch(error => {
        console.error('Error saving settings:', error);
        showToast('Failed to save settings', 'danger');
    });
}

// Initialize tax brackets editor
function initializeTaxBracketsEditor(brackets) {
    const container = document.getElementById('taxBracketsContainer');
    if (!container) return;
    
    container.innerHTML = '';
    
    brackets.forEach((bracket, index) => {
        const bracketElement = document.createElement('div');
        bracketElement.className = 'row g-3 mb-3';
        bracketElement.innerHTML = `
            <div class="col-md-4">
                <label class="form-label">From Amount</label>
                <input type="number" class="form-control" name="tax_brackets[${index}][from]" value="${bracket.from}">
            </div>
            <div class="col-md-4">
                <label class="form-label">To Amount</label>
                <input type="number" class="form-control" name="tax_brackets[${index}][to]" value="${bracket.to}">
            </div>
            <div class="col-md-3">
                <label class="form-label">Rate (%)</label>
                <input type="number" class="form-control" name="tax_brackets[${index}][rate]" value="${bracket.rate}">
            </div>
            <div class="col-md-1 d-flex align-items-end">
                <button type="button" class="btn btn-danger btn-sm remove-bracket" ${brackets.length <= 1 ? 'disabled' : ''}>
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        container.appendChild(bracketElement);
    });
    
    // Add event listeners to remove buttons
    document.querySelectorAll('.remove-bracket').forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('.row').remove();
        });
    });
    
    // Add event listener to add bracket button
    const addBracketBtn = document.getElementById('addTaxBracketBtn');
    if (addBracketBtn) {
        addBracketBtn.addEventListener('click', function() {
            const index = document.querySelectorAll('#taxBracketsContainer .row').length;
            const bracketElement = document.createElement('div');
            bracketElement.className = 'row g-3 mb-3';
            bracketElement.innerHTML = `
                <div class="col-md-4">
                    <label class="form-label">From Amount</label>
                    <input type="number" class="form-control" name="tax_brackets[${index}][from]" value="0">
                </div>
                <div class="col-md-4">
                    <label class="form-label">To Amount</label>
                    <input type="number" class="form-control" name="tax_brackets[${index}][to]" value="0">
                </div>
                <div class="col-md-3">
                    <label class="form-label">Rate (%)</label>
                    <input type="number" class="form-control" name="tax_brackets[${index}][rate]" value="0">
                </div>
                <div class="col-md-1 d-flex align-items-end">
                    <button type="button" class="btn btn-danger btn-sm remove-bracket">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
            container.appendChild(bracketElement);
            
            // Add event listener to new remove button
            bracketElement.querySelector('.remove-bracket').addEventListener('click', function() {
                this.closest('.row').remove();
            });
        });
    }
}


document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});


function loadActivities() {
    const container = document.getElementById('activity-list');
    const overlay = container.closest('.card-body').querySelector('.loading-overlay');
    
    overlay.style.display = 'flex';
    
    fetch('/api/recent-activities')
        .then(response => response.json())
        .then(data => {
            container.innerHTML = '';
            
            if (data.length === 0) {
                container.innerHTML = `
                    <div class="text-center py-4 text-muted">
                        <i class="fas fa-inbox fa-2x mb-2"></i>
                        <p>No recent activities found</p>
                    </div>
                `;
                return;
            }
            
            data.slice(0, 5).forEach(item => {
                const activityItem = document.createElement('div');
                activityItem.className = 'activity-item mb-3';
                activityItem.innerHTML = `
                    <div class="d-flex">
                        <div class="activity-badge bg-${item.type === 'warning' ? 'warning' : item.type === 'error' ? 'danger' : 'primary'} me-3">
                            <i class="fas fa-${item.icon || 'bell'}"></i>
                        </div>
                        <div class="flex-grow-1">
                            <div class="d-flex justify-content-between">
                                <h6 class="mb-1">${item.title}</h6>
                                <small class="text-muted">${new Date(item.time).toLocaleTimeString()}</small>
                            </div>
                            <p class="mb-0 text-muted small">${item.description}</p>
                        </div>
                    </div>
                `;
                container.appendChild(activityItem);
            });
        })
        .catch(error => {
            console.error("Failed to load activities:", error);
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Failed to load activities. Please try again.
                </div>
            `;
        })
        .finally(() => {
            overlay.style.display = 'none';
        });
}

// Refresh activities button
document.getElementById('refreshActivities').addEventListener('click', function(e) {
    e.preventDefault();
    loadActivities();
});

// Attendance table filtering
document.querySelectorAll('#attendanceFilter + .dropdown-menu a[data-filter]').forEach(item => {
    item.addEventListener('click', function(e) {
        e.preventDefault();
        const filter = this.getAttribute('data-filter');
        
        if (filter === 'export') {
            // Handle export
            console.log('Exporting attendance data');
            return;
        }
        
        const tableBody = document.querySelector('#attendance-table tbody');
        const rows = tableBody.querySelectorAll('tr');
        const overlay = tableBody.closest('.card-body').querySelector('.loading-overlay');
        
        overlay.style.display = 'flex';
        
        // Simulate filtering with timeout
        setTimeout(() => {
            rows.forEach(row => {
                const status = row.querySelector('td:nth-child(2)').textContent.trim().toLowerCase();
                
                if (filter === 'all' || 
                    (filter === 'present' && status === 'present') ||
                    (filter === 'absent' && status === 'absent') ||
                    (filter === 'late' && row.classList.contains('late'))) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
            
            overlay.style.display = 'none';
        }, 500);
    });
});

// Chart variables
var attendanceChart, departmentChart, payrollChart, departmentPayrollChart;

// Color palette for departments
const departmentColors = [
    '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', 
    '#e74a3b', '#858796', '#6f42c1', '#fd7e14',
    '#20c997', '#17a2b8', '#ffc107', '#dc3545'
];
function updateWeekRangeLabel(range) {
    $('#weekRangeLabel').html(`
        <i class="far fa-calendar me-1"></i>${range.start} to ${range.end}
    `);
}
function loadAttendanceData(weekOffset = 0) {
    // Show loading state
    $('#attendanceChart').closest('.card-body').find('.loading-overlay').show();
    
    $.ajax({
        url: '/api/attendance/weekly',
        type: 'GET',
        data: { week_offset: weekOffset },
        dataType: 'json',
        success: function(response) {
            updateAttendanceChart(response.data);
            updateAttendanceStats(response.stats);
            updateWeekDropdown(response.available_weeks, weekOffset);
            updateAdditionalMetrics(response.metrics);
            updateWeekRangeLabel(response.week_range);
        },
        error: function(xhr) {
            console.error('Error loading attendance data:', xhr.responseText);
            showToast('Failed to load attendance data', 'danger');
        },
        complete: function() {
            $('#attendanceChart').closest('.card-body').find('.loading-overlay').hide();
        }
    });
}

function updateAttendanceChart(data) {
    const ctx = document.getElementById('attendanceChart').getContext('2d');
    
    // Destroy previous chart if exists
    if (attendanceChart) {
        attendanceChart.destroy();
    }
    
    // Create new chart
    attendanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.days,
            datasets: [
                {
                    label: 'Present',
                    data: data.present,
                    borderColor: '#4e73df',
                    backgroundColor: 'rgba(78, 115, 223, 0.05)',
                    tension: 0.3,
                    fill: true,
                    borderWidth: 2,
                    pointBackgroundColor: '#4e73df',
                    pointRadius: 4,
                    pointHoverRadius: 6
                },
                {
                    label: 'Absent',
                    data: data.absent,
                    borderColor: '#e74a3b',
                    backgroundColor: 'rgba(231, 74, 59, 0.05)',
                    tension: 0.3,
                    fill: true,
                    borderWidth: 2,
                    pointBackgroundColor: '#e74a3b',
                    pointRadius: 4,
                    pointHoverRadius: 6
                },
                {
                    label: 'Late',
                    data: data.late,
                    borderColor: '#f6c23e',
                    backgroundColor: 'rgba(246, 194, 62, 0.05)',
                    tension: 0.3,
                    fill: true,
                    borderWidth: 2,
                    pointBackgroundColor: '#f6c23e',
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    hidden: true // Initially hidden
                }
            ]
        },
        options: {
            maintainAspectRatio: false,
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 12
                        }
                    },
                    onClick: function(e, legendItem, legend) {
                        const index = legendItem.datasetIndex;
                        const ci = legend.chart;
                        const meta = ci.getDatasetMeta(index);

                        // See controller.isDatasetVisible comment
                        meta.hidden = meta.hidden === null ? !ci.data.datasets[index].hidden : null;

                        ci.update();
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 12
                    },
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw}`;
                        },
                        footer: function(tooltipItems) {
                            const total = tooltipItems.reduce((sum, item) => sum + item.raw, 0);
                            return `Total: ${total}`;
                        }
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Employees',
                        font: {
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        precision: 0
                    },
                    grid: {
                        drawBorder: false
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Day of Week
                        font: {
                            weight: 'bold'
                        }
                    },
                    grid: {
                        drawBorder: false
                    }
                }

            }
        }
    });
}

function updateAttendanceStats(stats) {
    const statsHtml = `
        <div class="col-md-4">
            <div class="stat-card bg-success bg-opacity-10 border-start border-success border-4">
                <div class="stat-content">
                    <div class="stat-label">Avg Presence</div>
                    <div class="stat-value text-success">${stats.avg_presence}%</div>
                    <div class="stat-change ${stats.attendance_change >= 0 ? 'text-success' : 'text-danger'}">
                        <i class="fas fa-arrow-${stats.attendance_change >= 0 ? 'up' : 'down'} me-1"></i>
                        ${Math.abs(stats.attendance_change)}% from last week
                    </div>
                </div>
                <div class="stat-icon">
                    <i class="fas fa-user-check text-success"></i>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="stat-card bg-primary bg-opacity-10 border-start border-primary border-4">
                <div class="stat-content">
                    <div class="stat-label">Total Present</div>
                    <div class="stat-value text-primary">${stats.total_present}</div>
                    <div class="stat-change text-primary">
                        ${stats.present_change >= 0 ? '+' : ''}${stats.present_change} from last week
                    </div>
                </div>
                <div class="stat-icon">
                    <i class="fas fa-user-clock text-primary"></i>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="stat-card bg-danger bg-opacity-10 border-start border-danger border-4">
                <div class="stat-content">
                    <div class="stat-label">Total Absent</div>
                    <div class="stat-value text-danger">${stats.total_absent}</div>
                    <div class="stat-change ${stats.absent_change <= 0 ? 'text-success' : 'text-danger'}">
                        <i class="fas fa-arrow-${stats.absent_change <= 0 ? 'down' : 'up'} me-1"></i>
                        ${Math.abs(stats.absent_change)} from last week
                    </div>
                </div>
                <div class="stat-icon">
                    <i class="fas fa-user-slash text-danger"></i>
                </div>
            </div>
        </div>
    `;
    $('#attendanceStats').html(statsHtml);
}
function updateAdditionalMetrics(metrics) {
    $('#bestDay').text(metrics.best_day.day);
    $('#bestDayPercentage').html(`${metrics.best_day.percentage}% <small class="text-success"><i class="fas fa-arrow-up"></i> ${metrics.best_day.change}%</small>`);
    
    $('#worstDay').text(metrics.worst_day.day);
    $('#worstDayPercentage').html(`${metrics.worst_day.percentage}% <small class="text-danger"><i class="fas fa-arrow-down"></i> ${metrics.worst_day.change}%</small>`);
    
    $('#consistency').text(metrics.consistency.score);
    $('#consistencyTrend').html(`
        <small class="${metrics.consistency.trend === 'up' ? 'text-success' : 'text-danger'}">
            <i class="fas fa-arrow-${metrics.consistency.trend === 'up' ? 'up' : 'down'}"></i> 
            ${metrics.consistency.change}%
        </small>
    `);
}

function updateWeekDropdown(weeks, currentWeekOffset) {
    const dropdown = $('#weekDropdown');
    dropdown.empty();
    
    // Add header
    dropdown.append('<li><div class="dropdown-header">Available Weeks</div></li>');
    
    // Add weeks
    weeks.forEach(week => {
        const activeClass = week.offset === currentWeekOffset ? 'active' : '';
        const currentBadge = week.offset === 0 ? '<span class="badge bg-primary ms-2">Current</span>' : '';
        
        dropdown.append(`
            <li>
                <a class="dropdown-item ${activeClass} d-flex justify-content-between align-items-center" href="#" data-offset="${week.offset}">
                    <span>${week.label}</span>
                    ${currentBadge}
                </a>
            </li>
        `);
    });
    function updateDepartmentChart(data) {
        const ctx = document.getElementById('departmentChart').getContext('2d');
        
        // Destroy previous chart if exists
        if (departmentChart) {
            departmentChart.destroy();
        }
        
        // Prepare data for chart
        const labels = data.map(dept => dept.name);
        const counts = data.map(dept => dept.count);
        const backgrounds = data.map((_, index) => departmentColors[index % departmentColors.length]);
        
        // Create new chart
        departmentChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: counts,
                    backgroundColor: backgrounds,
                    borderWidth: 1,
                    borderColor: '#fff'
                }]
            },
            options: {
                maintainAspectRatio: false,
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                },
                cutout: '70%'
            }
        });
    }



