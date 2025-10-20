// DevBhoomi JavaScript - Enhanced UI Interactions

// ===== MODAL MANAGEMENT =====
/**
 * Shows A Modal By ID
 * @param {string} modalId - The ID Of The Modal To Show
 */
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
    }
}

/**
 * Hides A Modal By ID
 * @param {string} modalId - The ID Of The Modal To Hide
 */
function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// ===== GLOBAL MODAL CLOSE HANDLER =====
window.onclick = function(event) {
    const modals = document.getElementsByClassName('Modal');
    for (let modal of modals) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    }
};

// ===== FORM VALIDATION =====
/**
 * Validates A Form By Checking Required Fields
 * @param {string} formId - The ID Of The Form To Validate
 * @returns {boolean} - True If Valid, False Otherwise
 */
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;

    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');

    for (let input of inputs) {
        if (!input.value.trim()) {
            const fieldName = input.name || input.placeholder || 'This field';
            showNotification(`${fieldName} Is Required`, 'error');
            input.focus();
            return false;
        }
    }

    return true;
}

// ===== API UTILITIES =====
/**
 * Makes An APIRequest With Default Settings
 * @param {string} url - The API Endpoint
 * @param {object} options - Fetch Options
 * @returns {Promise} - Response JSON
 */
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    try {
        const response = await fetch(url, { ...defaultOptions, ...options });

        if (!response.ok) {
            throw new Error(`API Request Failed: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

// ===== REPOSITORY OPERATIONS =====
/**
 * Creates A New Repository
 * @param {string} name - Repository Name
 * @param {string} description - Repository Description
 * @param {boolean} isPrivate - Whether The Repo Is Private
 * @returns {Promise} - API Response
 */
async function createRepository(name, description, isPrivate) {
    try {
        const response = await apiRequest('/api/repo', {
            method: 'POST',
            body: JSON.stringify({
                name: name,
                description: description,
                isPrivate: isPrivate
            })
        });
        showNotification('Repository Created Successfully!', 'success');
        return response;
    } catch (error) {
        console.error('Error Creating Repository:', error);
        showNotification('Failed To Create Repository', 'error');
        throw error;
    }
}

// ===== BRANCH OPERATIONS =====
/**
 * Creates A New Branch
 * @param {number} repoId - Repository ID
 * @param {string} branchName - Branch Name
 * @returns {Promise} - API Response
 */
async function createBranch(repoId, branchName) {
    try {
        const response = await apiRequest(`/api/repo/${repoId}/branch`, {
            method: 'POST',
            body: JSON.stringify({
                name: branchName
            })
        });
        showNotification('Branch Created Successfully!', 'success');
        return response;
    } catch (error) {
        console.error('Error Creating Branch:', error);
        showNotification('Failed To Create Branch', 'error');
        throw error;
    }
}

/**
 * Deletes A Branch
 * @param {number} repoId - Repository ID
 * @param {string} branchName - Branch Name
 * @returns {Promise} - Success Status
 */
async function deleteBranch(repoId, branchName) {
    try {
        await apiRequest(`/api/repo/${repoId}/branch/${branchName}`, {
            method: 'DELETE'
        });
        showNotification('Branch Deleted Successfully!', 'success');
        return true;
    } catch (error) {
        console.error('Error Deleting Branch:', error);
        showNotification('Failed To Delete Branch', 'error');
        throw error;
    }
}

// ===== COMMIT OPERATIONS =====
/**
 * Fetches Commits For A Repository
 * @param {number} repoId - Repository ID
 * @param {string} branch - Branch Name (Optional)
 * @returns {Promise} - Commits Data
 */
async function getCommits(repoId, branch = null) {
    try {
        const url = branch ? `/api/repo/${repoId}/commits?branch=${branch}` : `/api/repo/${repoId}/commits`;
        const response = await apiRequest(url);
        return response;
    } catch (error) {
        console.error('Error Fetching Commits:', error);
        showNotification('Failed To Load Commits', 'error');
        throw error;
    }
}

// ===== UTILITY FUNCTIONS =====
/**
 * Formats A Date String For Display
 * @param {string} dateString - ISO Date String
 * @returns {string} - Formatted Date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Truncates Text To A Maximum Length
 * @param {string} text - Text To Truncate
 * @param {number} maxLength - Maximum Length
 * @returns {string} - Truncated Text
 */
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// ===== CLIPBOARD UTILITIES =====
/**
 * Copies Text To Clipboard With Notification
 * @param {string} text - Text To Copy
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Copied To Clipboard!', 'success');
    } catch (error) {
        console.error('Failed To Copy:', error);
        // Fallback For Older Browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('Copied To Clipboard!', 'success');
    }
}

// ===== NOTIFICATION SYSTEM =====
/**
 * Shows A Notification Message
 * @param {string} message - Message To Display
 * @param {string} type - Type Of Notification (success, error, warning, info)
 */
function showNotification(message, type = 'info') {
    // Remove Existing Notifications Of Same Type
    const existing = document.querySelectorAll(`.FlashMessage.${type}`);
    existing.forEach(el => el.remove());

    const notification = document.createElement('div');
    notification.className = `FlashMessage ${type}`;
    notification.textContent = message;

    const container = document.querySelector('.MainContent') || document.body;
    container.insertBefore(notification, container.firstChild);

    // Auto-Hide After 3 Seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ===== BRANCH PROTECTION MODAL =====
let currentBranchId = null;

function showProtectionModal(branchId, branchName) {
    currentBranchId = branchId;
    const modal = document.getElementById('ProtectionModal');
    const branchNameElement = document.getElementById('ProtectionBranchName');
    
    if (!modal || !branchNameElement) {
        console.error('Protection Modal Elements Not Found');
        return;
    }
    
    branchNameElement.textContent = `Configure Protection For Branch: ${branchName}`;
    modal.style.display = 'block';

    // Load Current Rules
    fetch(`/api/repo/${encodeURIComponent(window.location.pathname.split('/')[2])}/branch/${branchId}/protection`)
        .then(response => response.json())
        .then(rules => {
            const noForcePush = document.getElementById('NoForcePush');
            const reviewRequired = document.getElementById('ReviewRequired');
            const requireStatusChecks = document.getElementById('RequireStatusChecks');
            const requireUpToDate = document.getElementById('RequireUpToDate');
            const restrictPushes = document.getElementById('RestrictPushes');
            const linearHistory = document.getElementById('LinearHistory');
            
            if (noForcePush) noForcePush.checked = rules.some(r => r.type === 'no_force_push' && r.value);
            if (reviewRequired) reviewRequired.checked = rules.some(r => r.type === 'review_required' && r.value);
            if (requireStatusChecks) requireStatusChecks.checked = rules.some(r => r.type === 'require_status_checks' && r.value);
            if (requireUpToDate) requireUpToDate.checked = rules.some(r => r.type === 'require_up_to_date' && r.value);
            if (restrictPushes) restrictPushes.checked = rules.some(r => r.type === 'restrict_pushes' && r.value);
            if (linearHistory) linearHistory.checked = rules.some(r => r.type === 'linear_history' && r.value);
        })
        .catch(error => {
            console.error('Error Loading Branch Protection Rules:', error);
        });
}

function hideProtectionModal() {
    const modal = document.getElementById('ProtectionModal');
    if (modal) {
        modal.style.display = 'none';
    }
    currentBranchId = null;
}

// Handle Protection Form Submission
document.addEventListener('DOMContentLoaded', function() {
    const protectionForm = document.getElementById('ProtectionForm');
    if (protectionForm) {
        protectionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            if (!currentBranchId) return;

            const rules = [
                { type: 'no_force_push', value: document.getElementById('NoForcePush')?.checked || false },
                { type: 'review_required', value: document.getElementById('ReviewRequired')?.checked || false },
                { type: 'require_status_checks', value: document.getElementById('RequireStatusChecks')?.checked || false },
                { type: 'require_up_to_date', value: document.getElementById('RequireUpToDate')?.checked || false },
                { type: 'restrict_pushes', value: document.getElementById('RestrictPushes')?.checked || false },
                { type: 'linear_history', value: document.getElementById('LinearHistory')?.checked || false }
            ];

            // Save Rules
            fetch(`/api/repo/${encodeURIComponent(window.location.pathname.split('/')[2])}/branch/${currentBranchId}/protection`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(rules)
            })
            .then(response => {
                if (response.ok) {
                    hideProtectionModal();
                    location.reload();
                } else {
                    console.error('Error Saving Branch Protection Rules');
                }
            })
            .catch(error => {
                console.error('Error Saving Branch Protection Rules:', error);
            });
        });
    }
});

// Toggle README textarea On Create Repository Page
document.addEventListener('DOMContentLoaded', function() {
    const initReadme = document.getElementById('InitReadme');
    const readmeRow = document.getElementById('ReadmeRow');
    if (initReadme && readmeRow) {
        initReadme.addEventListener('change', function() {
            readmeRow.style.display = this.checked ? 'block' : 'none';
        });
    }
});

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    // Enhanced Form Validation With Event Delegation
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form.id)) {
                e.preventDefault();
                return false;
            }
        });
    });

    // Auto-Hide Flash Messages With Smooth Animation
    const flashMessages = document.querySelectorAll('.FlashMessage');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.transition = 'opacity 0.3s ease';
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 8000); // Increased From 5000 To 8000 milliseconds
    });

    // Delegate Protect Button Clicks To Open Branch Protection Modal
    document.body.addEventListener('click', function(e) {
        const btn = e.target.closest && e.target.closest('.protect-btn');
        if (btn) {
            const branchId = btn.getAttribute('data-branch-id');
            const branchName = btn.getAttribute('data-branch-name');
            if (branchId) {
                // BranchId From Template Is Numeric String; Convert To Number When Calling
                showProtectionModal(Number(branchId), branchName);
            }
        }
    });

});

// ===== PROFILE EDITING =====
document.addEventListener('DOMContentLoaded', function() {
    const editProfileBtn = document.getElementById('editProfileBtn');
    const editProfileForm = document.getElementById('editProfileForm');
    const cancelEditBtn = document.getElementById('cancelEditBtn');

    if (editProfileBtn && editProfileForm) {
        // Show Edit Form
        editProfileBtn.addEventListener('click', function() {
            editProfileForm.style.display = 'block';
            editProfileBtn.style.display = 'none';
        });

        // Hide Edit Form
        if (cancelEditBtn) {
            cancelEditBtn.addEventListener('click', function() {
                editProfileForm.style.display = 'none';
                editProfileBtn.style.display = 'inline-block';
            });
        }
    }
});

    // ===== MARKDOWN PREVIEW =====
    /**
     * Updates The Markdown Preview When Editing/Creating Files.
     * Shows The Preview Pane Only For Filenames Ending With .md Or .markdown
     */
    function updatePreview() {
        try {
            const filenameEl = document.getElementById('filename') || document.querySelector('[name="filename"]');
            const contentEl = document.getElementById('content');
            if (!contentEl) return;

            const previewWrapper = document.getElementById('markdownPreview');
            const previewContent = document.getElementById('mdPreviewContent');

            const fname = filenameEl ? (filenameEl.value || filenameEl.innerText || '') : '';
            const isMarkdown = /\.(md|markdown)$/i.test(fname.trim());

            if (previewWrapper) {
                previewWrapper.style.display = isMarkdown ? 'block' : 'none';
            }

            if (previewContent && isMarkdown) {
                const raw = contentEl.value || '';
                try {
                    if (window.marked) {
                        const html = window.marked.parse(raw);
                        if (window.DOMPurify) {
                            previewContent.innerHTML = window.DOMPurify.sanitize(html);
                        } else {
                            previewContent.innerHTML = html;
                        }
                    } else {
                        // Simple Fallback: Escape HTML
                        previewContent.textContent = raw;
                    }
                } catch (err) {
                    previewContent.textContent = raw;
                }
            }
        } catch (err) {
            console.error('Update Preview Error', err);
        }
    }