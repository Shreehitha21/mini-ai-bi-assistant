document.addEventListener('DOMContentLoaded', () => {
    fetchDataQuality();
});

function setQuestion(text) {
    document.getElementById('questionInput').value = text;
    askQuestion();
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        askQuestion();
    }
}

async function fetchDataQuality() {
    try {
        const response = await fetch('/api/data-quality');
        const data = await response.json();
        const stats = data.statistics;
        
        let html = `<p>Processed ${stats.rows_processed} rows. Successfully imported: ${stats.successfully_imported}. Rejected: ${stats.rejected_rows}.</p>`;
        
        if (stats.rejection_reasons.length > 0) {
            html += `<ul>`;
            stats.rejection_reasons.forEach(reason => {
                // Ensure text is safely rendered
                html += `<li>${escapeHTML(reason)}</li>`;
            });
            html += `</ul>`;
        }
        
        document.getElementById('qualityStats').innerHTML = html;
    } catch (error) {
        document.getElementById('qualityStats').innerText = "Unable to load data quality report.";
    }
}

async function askQuestion() {
    const input = document.getElementById('questionInput');
    const question = input.value.trim();
    
    if (!question) return;

    // UI State: Loading
    document.getElementById('results').style.display = 'none';
    document.getElementById('limitationsBox').style.display = 'none';
    document.getElementById('dataVisualization').style.display = 'none';
    document.getElementById('loading').style.display = 'block';

    try {
        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question })
        });

        const data = await response.json();
        
        // UI State: Done
        document.getElementById('loading').style.display = 'none';
        document.getElementById('results').style.display = 'block';

        if (data.success) {
            document.getElementById('answerText').innerText = data.answer;
            document.getElementById('intentText').innerText = data.intent;
            document.getElementById('sqlText').innerText = data.sql_operation || "N/A";
            
            renderSupportingData(data.intent, data.supporting_data);

        } else {
            document.getElementById('answerText').innerText = "Error: " + (data.error || data.answer);
            document.getElementById('intentText').innerText = data.intent || "Unknown";
            document.getElementById('sqlText').innerText = "";
            
            if (data.limitations && data.limitations.length > 0) {
                document.getElementById('limitationsBox').style.display = 'block';
                document.getElementById('limitationsText').innerText = data.limitations.join(', ');
            }
        }
    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('results').style.display = 'block';
        document.getElementById('answerText').innerText = "A network error occurred while connecting to the server.";
        document.getElementById('intentText').innerText = "N/A";
        document.getElementById('sqlText').innerText = "";
    }
}

function renderSupportingData(intent, data) {
    const vizBox = document.getElementById('dataVisualization');
    vizBox.innerHTML = '';
    
    if (!data) return;

    let html = '<h3>Data Breakdown</h3><table class="data-table"><thead><tr>';
    
    // Very simple table rendering based on intent
    if (intent === 'monthly_revenue_trend' && Array.isArray(data.supporting_data)) {
        html += '<th>Month</th><th>Revenue (₹)</th></tr></thead><tbody>';
        data.supporting_data.forEach(row => {
            html += `<tr><td>${escapeHTML(row.month)}</td><td>${row.revenue.toLocaleString()}</td></tr>`;
        });
    } else if (intent === 'highest_revenue_product' && Array.isArray(data)) {
        html += '<th>Product</th><th>Revenue (₹)</th></tr></thead><tbody>';
        data.forEach(row => {
            html += `<tr><td>${escapeHTML(row.product)}</td><td>${row.revenue.toLocaleString()}</td></tr>`;
        });
    } else if (intent === 'highest_revenue_region' && Array.isArray(data)) {
        html += '<th>Region</th><th>Revenue (₹)</th></tr></thead><tbody>';
        data.forEach(row => {
            html += `<tr><td>${escapeHTML(row.region)}</td><td>${row.revenue.toLocaleString()}</td></tr>`;
        });
    } else if (intent === 'total_revenue') {
        html += '<th>Metric</th><th>Value</th></tr></thead><tbody>';
        html += `<tr><td>Transactions</td><td>${data.transaction_count}</td></tr>`;
        html += `<tr><td>Units Sold</td><td>${data.total_units_sold}</td></tr>`;
        html += `<tr><td>Rules</td><td>${escapeHTML(data.inclusion_rules)}</td></tr>`;
    } else if (intent === 'revenue_comparison') {
        html += '<th>Metric</th><th>Value</th></tr></thead><tbody>';
        html += `<tr><td>${escapeHTML(data.month1)} Revenue</td><td>₹${data.month1_revenue.toLocaleString()}</td></tr>`;
        html += `<tr><td>${escapeHTML(data.month2)} Revenue</td><td>₹${data.month2_revenue.toLocaleString()}</td></tr>`;
        html += `<tr><td>Absolute Change</td><td>₹${data.absolute_change.toLocaleString()}</td></tr>`;
        html += `<tr><td>% Change</td><td>${data.percentage_change}%</td></tr>`;
    } else {
        return; // No structured data to show
    }

    html += '</tbody></table>';
    vizBox.innerHTML = html;
    vizBox.style.display = 'block';
}

// Security: Prevent Cross-Site Scripting (XSS)
function escapeHTML(str) {
    if (!str) return '';
    return str.toString()
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}