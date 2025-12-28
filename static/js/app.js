// API Base URL (configured in index.html via window.ENV_API_BASE for prod)
const API_BASE = window.ENV_API_BASE || '';

// DOM Elements
const expenseForm = document.getElementById('expenseForm');
const userIdInput = document.getElementById('userId');
const quickModeBtn = document.getElementById('quickModeBtn');
const aiModeBtn = document.getElementById('aiModeBtn');
const receiptModeBtn = document.getElementById('receiptModeBtn');
const quickModeFields = document.getElementById('quickModeFields');
const aiModeFields = document.getElementById('aiModeFields');
const receiptModeFields = document.getElementById('receiptModeFields');
const naturalInput = document.getElementById('naturalInput');
const amountInput = document.getElementById('amount');
const categoryInput = document.getElementById('category');
const customCategoryGroup = document.getElementById('customCategoryGroup');
const customCategoryInput = document.getElementById('customCategory');
const dateInput = document.getElementById('date');
const descriptionInput = document.getElementById('description');
const messageDiv = document.getElementById('message');
const expensesList = document.getElementById('expensesList');
const refreshBtn = document.getElementById('refreshBtn');
const btnText = document.getElementById('btnText');
const btnLoader = document.getElementById('btnLoader');
const totalAmountDiv = document.getElementById('totalAmount');
const receiptInput = document.getElementById('receiptInput');
const ocrPreview = document.getElementById('ocrPreview');
const receiptImage = document.getElementById('receiptImage');
const ocrProgress = document.getElementById('ocrProgress');
const ocrProgressText = document.getElementById('ocrProgressText');
const extractedData = document.getElementById('extractedData');
const extractedAmount = document.getElementById('extractedAmount');
const extractedCategory = document.getElementById('extractedCategory');
const extractedDate = document.getElementById('extractedDate');
const extractedDescription = document.getElementById('extractedDescription');
const cancelOCRBtn = document.getElementById('cancelOCR');
const skipOCRBtn = document.getElementById('skipOCRBtn');
const confirmReceiptBtn = document.getElementById('confirmReceiptBtn');
const retryOCRBtn = document.getElementById('retryOCRBtn');

// Track current mode
let currentMode = 'quick'; // 'quick', 'ai', or 'receipt'
let ocrWorker = null; // Track OCR worker for cancellation

// Set today's date as default
dateInput.valueAsDate = new Date();

// Mode Toggle Functionality
quickModeBtn.addEventListener('click', function() {
    currentMode = 'quick';
    quickModeBtn.classList.add('active');
    aiModeBtn.classList.remove('active');
    receiptModeBtn.classList.remove('active');
    quickModeFields.style.display = 'block';
    aiModeFields.style.display = 'none';
    receiptModeFields.style.display = 'none';
    
    // Set fields as required
    amountInput.required = true;
    categoryInput.required = true;
    dateInput.required = true;
    descriptionInput.required = true;
    naturalInput.required = false;
});

aiModeBtn.addEventListener('click', function() {
    currentMode = 'ai';
    aiModeBtn.classList.add('active');
    quickModeBtn.classList.remove('active');
    receiptModeBtn.classList.remove('active');
    aiModeFields.style.display = 'block';
    quickModeFields.style.display = 'none';
    receiptModeFields.style.display = 'none';
    
    // Set fields as required
    naturalInput.required = true;
    amountInput.required = false;
    categoryInput.required = false;
    dateInput.required = false;
    descriptionInput.required = false;
});

receiptModeBtn.addEventListener('click', function() {
    currentMode = 'receipt';
    receiptModeBtn.classList.add('active');
    quickModeBtn.classList.remove('active');
    aiModeBtn.classList.remove('active');
    receiptModeFields.style.display = 'block';
    quickModeFields.style.display = 'none';
    aiModeFields.style.display = 'none';
    
    // Set fields as not required
    naturalInput.required = false;
    amountInput.required = false;
    categoryInput.required = false;
    dateInput.required = false;
    descriptionInput.required = false;
});

// Show/hide custom category field
categoryInput.addEventListener('change', function() {
    if (this.value === 'Other') {
        customCategoryGroup.style.display = 'block';
        customCategoryInput.required = true;
    } else {
        customCategoryGroup.style.display = 'none';
        customCategoryInput.required = false;
        customCategoryInput.value = '';
    }
});

// Smart Category Prediction - Feature 3
const categoryKeywords = {
    'Food': ['food', 'lunch', 'dinner', 'breakfast', 'snack', 'restaurant', 'meal', 'eat', 'coffee', 'tea', 'drink', 'grocery', 'groceries', 'vegetables', 'fruits', 'meat', 'chicken', 'fish', 'sweets', 'dessert', 'pizza', 'burger', 'biryani', 'dosa', 'idli', 'paratha', 'roti', 'rice', 'dal', 'curry', 'sweet', 'samosa', 'pakora', 'chai', 'juice', 'milk', 'bread', 'egg', 'paneer', 'mutton', 'veg', 'bakery', 'cake', 'ice cream', 'chocolate'],
    'Transport': ['transport', 'taxi', 'uber', 'ola', 'auto', 'bus', 'train', 'metro', 'flight', 'cab', 'rickshaw', 'petrol', 'diesel', 'fuel', 'parking', 'toll', 'car', 'bike', 'scooter', 'vehicle', 'rapido', 'ride', 'travel', 'commute', 'fare', 'gas', 'railway', 'airport', 'station'],
    'Shopping': ['shopping', 'clothes', 'shirt', 'shoes', 'pants', 'dress', 'jeans', 'electronics', 'phone', 'laptop', 'watch', 'bag', 'accessories', 'jewelry', 'cosmetics', 'makeup', 'beauty', 'gift', 'amazon', 'flipkart', 'online', 'purchase', 'buy', 'bought', 'store', 'mall', 'market', 'footwear', 'sandals', 'sneakers', 't-shirt', 'saree', 'kurta', 'sunglasses', 'perfume', 'wallet', 'belt'],
    'Entertainment': ['entertainment', 'movie', 'cinema', 'theatre', 'concert', 'show', 'game', 'gaming', 'netflix', 'spotify', 'prime', 'subscription', 'party', 'club', 'bar', 'pub', 'outing', 'trip', 'vacation', 'holiday', 'fun', 'amusement', 'park', 'zoo', 'museum', 'sports', 'cricket', 'football', 'tickets', 'event'],
    'Bills': ['bill', 'electricity', 'water', 'gas', 'internet', 'wifi', 'mobile', 'phone bill', 'recharge', 'rent', 'maintenance', 'utility', 'utilities', 'broadband', 'postpaid', 'prepaid', 'emi', 'insurance', 'premium', 'subscription', 'credit card', 'payment'],
    'Health': ['health', 'medical', 'doctor', 'hospital', 'medicine', 'pharmacy', 'clinic', 'dentist', 'checkup', 'consultation', 'treatment', 'surgery', 'test', 'lab', 'xray', 'scan', 'prescription', 'drug', 'tablet', 'injection', 'vaccine', 'therapy', 'gym', 'fitness', 'yoga', 'exercise', 'wellness'],
    'Education': ['education', 'school', 'college', 'university', 'course', 'class', 'tuition', 'book', 'books', 'notebook', 'stationery', 'pen', 'pencil', 'study', 'exam', 'fee', 'fees', 'training', 'workshop', 'seminar', 'certification', 'learning', 'tutorial', 'online course']
};

function predictCategory(description) {
    if (!description) return null;
    
    const text = description.toLowerCase().trim();
    let bestMatch = null;
    let maxMatches = 0;
    
    // Count keyword matches for each category
    for (const [category, keywords] of Object.entries(categoryKeywords)) {
        let matchCount = 0;
        for (const keyword of keywords) {
            if (text.includes(keyword)) {
                matchCount++;
            }
        }
        if (matchCount > maxMatches) {
            maxMatches = matchCount;
            bestMatch = category;
        }
    }
    
    return bestMatch;
}

// Auto-suggest category as user types description
let suggestionTimeout;
descriptionInput.addEventListener('input', function() {
    clearTimeout(suggestionTimeout);
    suggestionTimeout = setTimeout(() => {
        const predictedCategory = predictCategory(this.value);
        if (predictedCategory && !categoryInput.value) {
            categoryInput.value = predictedCategory;
            // Show visual feedback
            categoryInput.style.borderColor = '#667eea';
            categoryInput.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.1)';
            setTimeout(() => {
                categoryInput.style.borderColor = '';
                categoryInput.style.boxShadow = '';
            }, 1000);
        }
    }, 300); // Debounce for 300ms
});

// Load expenses on page load
let currentUserId = localStorage.getItem('userId') || '';
if (currentUserId) {
    userIdInput.value = currentUserId;
    loadExpenses(currentUserId);
}

// Form submission
expenseForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const userId = userIdInput.value.trim();
    
    if (!userId) {
        showMessage('Please enter User ID', 'error');
        return;
    }
    
    // Save userId to localStorage
    localStorage.setItem('userId', userId);
    currentUserId = userId;
    
    // Disable form
    setLoading(true);
    
    let requestBody;
    
    if (currentMode === 'ai') {
        // AI Mode: Send natural language text
        const text = naturalInput.value.trim();
        
        if (!text) {
            showMessage('Please describe your expense', 'error');
            setLoading(false);
            return;
        }
        
        requestBody = {
            user_id: userId,
            text: text
        };
    } else {
        // Quick Mode: Send structured data
        const amount = amountInput.value.trim();
        let category = categoryInput.value;
        const date = dateInput.value;
        const description = descriptionInput.value.trim();
        
        // Use custom category if "Other" is selected
        if (category === 'Other' && customCategoryInput.value.trim()) {
            category = customCategoryInput.value.trim();
        }
        
        if (!amount || !category || !date || !description) {
            showMessage('Please fill in all fields', 'error');
            setLoading(false);
            return;
        }
        
        requestBody = {
            user_id: userId,
            amount: parseFloat(amount),
            category: category,
            date: date,
            description: description
        };
    }
    
    try {
        const response = await fetch(`${API_BASE}/expenses/add/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('✅ Expense added successfully!', 'success');
            // Clear form except user ID
            if (currentMode === 'ai') {
                naturalInput.value = '';
            } else {
                amountInput.value = '';
                categoryInput.value = '';
                customCategoryGroup.style.display = 'none';
                customCategoryInput.value = '';
                dateInput.valueAsDate = new Date();
                descriptionInput.value = '';
            }
            loadExpenses(userId);
        } else {
            showMessage(`❌ Error: ${data.error || 'Failed to add expense'}`, 'error');
        }
    } catch (error) {
        showMessage(`❌ Network error: ${error.message}`, 'error');
    } finally {
        setLoading(false);
    }
});

// Refresh button
refreshBtn.addEventListener('click', () => {
    const userId = userIdInput.value.trim();
    if (userId) {
        loadExpenses(userId);
    } else {
        showMessage('Please enter a User ID first', 'error');
    }
});

// Load expenses function
async function loadExpenses(userId) {
    try {
        expensesList.innerHTML = '<p class="empty-state">Loading...</p>';
        
        const response = await fetch(`${API_BASE}/expenses/list/${userId}/`);
        const expenses = await response.json();
        
        if (response.ok && expenses.length > 0) {
            displayExpenses(expenses);
        } else {
            expensesList.innerHTML = '<p class="empty-state">No expenses found. Add your first expense!</p>';
            totalAmountDiv.innerHTML = '';
        }
    } catch (error) {
        expensesList.innerHTML = '<p class="empty-state">Error loading expenses. Please try again.</p>';
        console.error('Error loading expenses:', error);
    }
}

// Display expenses
function displayExpenses(expenses) {
    // Sort by date (newest first)
    expenses.sort((a, b) => new Date(b.date) - new Date(a.date));
    
    let total = 0;
    
    const expensesHTML = expenses.map(expense => {
        total += parseFloat(expense.amount);
        
        return `
            <div class="expense-item">
                <div class="expense-header">
                    <span class="expense-category">${escapeHtml(expense.category)}</span>
                    <span class="expense-amount">₹${Math.round(parseFloat(expense.amount))}</span>
                </div>
                <div class="expense-details">${escapeHtml(expense.description)}</div>
                <div class="expense-date">📅 ${formatDate(expense.date)}</div>
            </div>
        `;
    }).join('');
    
    expensesList.innerHTML = expensesHTML;
    
    // Show total
    totalAmountDiv.innerHTML = `Total Expenses: ₹${Math.round(total)}`;
}

// Helper functions
function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    
    setTimeout(() => {
        messageDiv.className = 'message';
    }, 5000);
}

function setLoading(loading) {
    const submitBtn = expenseForm.querySelector('button[type="submit"]');
    submitBtn.disabled = loading;
    
    if (loading) {
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline-block';
    } else {
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ===== FEATURE 4: RECEIPT OCR SCANNER =====

// Store extracted receipt data
let extractedReceiptData = null;

// Handle receipt image upload
receiptInput.addEventListener('change', async function(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    // Compress and display preview
    const compressedDataURL = await compressImage(file);
    receiptImage.src = compressedDataURL;
    ocrPreview.style.display = 'block';
    extractedData.style.display = 'none';
    
    // Perform OCR with compressed image
    await performOCR(compressedDataURL);
});

// Handle OCR cancellation
cancelOCRBtn.addEventListener('click', function() {
    ocrProgress.style.display = 'none';
    showMessage('Receipt scanning cancelled.', 'error');
});

// Handle confirm receipt data
confirmReceiptBtn.addEventListener('click', async function() {
    if (!extractedReceiptData) {
        showMessage('No receipt data to save', 'error');
        return;
    }
    
    const userId = userIdInput.value.trim();
    if (!userId) {
        showMessage('Please enter your User ID', 'error');
        userIdInput.focus();
        return;
    }
    
    // Save the expense
    setBusy(true);
    try {
        const response = await fetch(`${API_BASE}/expenses/add/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId,
                amount: extractedReceiptData.amount,
                category: extractedReceiptData.category,
                date: extractedReceiptData.date,
                description: extractedReceiptData.description
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage('✓ Expense saved successfully!', 'success');
            loadExpenses();
            
            // Reset receipt mode
            receiptInput.value = '';
            ocrPreview.style.display = 'none';
            extractedData.style.display = 'none';
            extractedReceiptData = null;
        } else {
            throw new Error(result.error || 'Failed to save expense');
        }
    } catch (error) {
        showMessage(`Error: ${error.message}`, 'error');
    } finally {
        setBusy(false);
    }
});

// Handle retry OCR
retryOCRBtn.addEventListener('click', function() {
    receiptInput.value = '';
    ocrPreview.style.display = 'none';
    extractedData.style.display = 'none';
    extractedReceiptData = null;
    receiptInput.click(); // Open file picker again
});

// Handle skip OCR - go directly to manual entry with smart defaults
skipOCRBtn.addEventListener('click', function() {
    // Switch to quick mode
    currentMode = 'quick';
    quickModeBtn.classList.add('active');
    receiptModeBtn.classList.remove('active');
    quickModeFields.style.display = 'block';
    receiptModeFields.style.display = 'none';
    aiModeFields.style.display = 'none';
    
    // Set today's date
    dateInput.value = new Date().toISOString().split('T')[0];
    
    // Focus on amount field for quick entry
    amountInput.focus();
    
    showMessage('💡 Enter your receipt details below. AI will suggest the category as you type!', 'success');
});

async function performOCR(imageDataURL) {
    try {
        ocrProgress.style.display = 'block';
        ocrProgressText.textContent = '🤖 AI is reading your receipt...';
        
        const response = await fetch(`${API_BASE}/expenses/scan-receipt/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ image: imageDataURL })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Failed to scan receipt');
        }
        
        ocrProgress.style.display = 'none';
        
        const extractedInfo = result.data;
        
        // Store the extracted data
        extractedReceiptData = extractedInfo;
        
        // Display extracted data
        extractedAmount.textContent = extractedInfo.amount;
        extractedCategory.textContent = extractedInfo.category;
        extractedDate.textContent = extractedInfo.date;
        extractedDescription.textContent = extractedInfo.description;
        
        extractedData.style.display = 'block';
        
        showMessage('✓ Receipt scanned successfully! Review and confirm.', 'success');
        
    } catch (error) {
        ocrProgress.style.display = 'none';
        console.error('Receipt scanning error:', error);
        showMessage('⚠️ Failed to scan receipt: ' + error.message + '. Please try again or enter manually.', 'error');
    }
}

function extractReceiptData(ocrText) {
    const text = ocrText.toLowerCase();
    const lines = ocrText.split('\n').filter(line => line.trim());
    
    const result = {
        amount: null,
        date: null,
        description: null,
        category: null
    };
    
    // Extract amount - look for rupee symbols or numbers with currency indicators
    const amountPatterns = [
        /(?:rs\.?|₹|inr)\s*(\d+(?:,\d{3})*(?:\.\d{2})?)/i,
        /(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:rs\.?|₹|inr)/i,
        /total[:\s]+(?:rs\.?|₹)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)/i,
        /amount[:\s]+(?:rs\.?|₹)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)/i,
        /grand\s+total[:\s]+(?:rs\.?|₹)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)/i
    ];
    
    for (const pattern of amountPatterns) {
        const match = ocrText.match(pattern);
        if (match) {
            result.amount = parseFloat(match[1].replace(/,/g, ''));
            break;
        }
    }
    
    // Extract date
    const datePatterns = [
        /(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})/,
        /(\d{2,4}[-\/]\d{1,2}[-\/]\d{1,2})/,
        /(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{2,4})/i
    ];
    
    for (const pattern of datePatterns) {
        const match = ocrText.match(pattern);
        if (match) {
            try {
                const parsedDate = new Date(match[1]);
                if (!isNaN(parsedDate.getTime())) {
                    result.date = parsedDate.toISOString().split('T')[0];
                    break;
                }
            } catch (e) {
                // Try next pattern
            }
        }
    }
    
    // If no date found, use today
    if (!result.date) {
        result.date = new Date().toISOString().split('T')[0];
    }
    
    // Extract merchant/description
    const merchantKeywords = ['restaurant', 'cafe', 'store', 'shop', 'mart', 'mall', 'pvt', 'ltd', 'inc'];
    for (const line of lines.slice(0, 5)) { // Check first 5 lines
        for (const keyword of merchantKeywords) {
            if (line.toLowerCase().includes(keyword)) {
                result.description = line.trim().substring(0, 50);
                break;
            }
        }
        if (result.description) break;
    }
    
    // If no merchant found, use first non-empty line
    if (!result.description && lines.length > 0) {
        result.description = lines[0].trim().substring(0, 50) || 'Receipt expense';
    }
    
    // Predict category based on text content
    result.category = predictCategory(ocrText);
    
    return result;
}

function displayExtractedData(rawText, extractedInfo) {
    extractedData.style.display = 'block';
    
    let html = '<strong>Raw OCR Text:</strong><br>' + escapeHtml(rawText.substring(0, 500));
    if (rawText.length > 500) html += '...<br><em>(truncated)</em>';
    
    html += '<br><br><strong>Extracted Data:</strong><br>';
    html += `Amount: ₹${extractedInfo.amount || 'Not found'}<br>`;
    html += `Date: ${extractedInfo.date || 'Not found'}<br>`;
    html += `Description: ${extractedInfo.description || 'Not found'}<br>`;
    html += `Category: ${extractedInfo.category || 'Not predicted'}<br>`;
    
    extractedText.innerHTML = html;
}

// Fallback: Basic extraction without full OCR
function performBasicExtraction(imageFile) {
    // For demo purposes, show manual entry with helper
    ocrPreview.style.display = 'none';
    
    // Switch to quick mode
    currentMode = 'quick';
    quickModeBtn.classList.add('active');
    receiptModeBtn.classList.remove('active');
    quickModeFields.style.display = 'block';
    receiptModeFields.style.display = 'none';
    
    // Set today's date as default
    dateInput.value = new Date().toISOString().split('T')[0];
    
    showMessage('⚠️ Please enter receipt details manually. OCR will be faster next time after initialization.', 'error');
}

// Compress image to reduce upload size
async function compressImage(file, maxWidth = 1200, quality = 0.8) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = new Image();
            img.onload = function() {
                const canvas = document.createElement('canvas');
                let width = img.width;
                let height = img.height;
                
                // Resize if image is too large
                if (width > maxWidth) {
                    height = (height * maxWidth) / width;
                    width = maxWidth;
                }
                
                canvas.width = width;
                canvas.height = height;
                
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);
                
                // Convert to JPEG with compression
                const compressedDataURL = canvas.toDataURL('image/jpeg', quality);
                resolve(compressedDataURL);
            };
            img.onerror = reject;
            img.src = e.target.result;
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}
