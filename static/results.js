// Results page specific functionality

document.addEventListener('DOMContentLoaded', function() {
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultsContent = document.getElementById('resultsContent');
    const errorContainer = document.getElementById('errorContainer');

    try {
        // Load predictions from localStorage
        loadPredictionsFromLocalStorage();
        
        loadingSpinner.style.display = 'none';
        resultsContent.style.display = 'block';

    } catch (error) {
        console.error('Error loading results:', error);
        errorContainer.textContent = '❌ Error: ' + error.message;
        errorContainer.style.display = 'block';
        loadingSpinner.style.display = 'none';
    }

    // Load more button
    document.getElementById('loadMoreBtn').addEventListener('click', function() {
        displayMorePredictions();
    });

    // Clear history button
    document.getElementById('clearHistoryBtn').addEventListener('click', function() {
        if (confirm('Are you sure you want to clear all prediction history? This cannot be undone!')) {
            localStorage.removeItem('cardio_predictions');
            alert('✅ Prediction history cleared!');
            location.reload();
        }
    });

    function loadPredictionsFromLocalStorage() {
        try {
            let allPredictions = JSON.parse(localStorage.getItem('cardio_predictions') || '[]');
            
            if (allPredictions.length === 0) {
                document.getElementById('totalPredictions').textContent = '0';
                document.getElementById('highRiskCount').textContent = '0';
                document.getElementById('moderateRiskCount').textContent = '0';
                document.getElementById('lowRiskCount').textContent = '0';
                document.getElementById('predictionTableBody').innerHTML = 
                    '<tr><td colspan="8" style="text-align: center; padding: 20px;">No predictions yet. <a href="/predict">Make a prediction</a></td></tr>';
                return;
            }

            // Calculate statistics
            calculateAndDisplayStatistics(allPredictions);
            
            // Display first 10 predictions
            displayPredictionsInTable(allPredictions.slice(0, 10));

        } catch (error) {
            console.error('Error loading predictions from localStorage:', error);
            document.getElementById('predictionTableBody').innerHTML = 
                '<tr><td colspan="8" style="text-align: center; padding: 20px; color: red;">Error loading data</td></tr>';
        }
    }

    function calculateAndDisplayStatistics(predictions) {
        const highRisk = predictions.filter(p => p.risk_percentage >= 60).length;
        const moderateRisk = predictions.filter(p => p.risk_percentage >= 30 && p.risk_percentage < 60).length;
        const lowRisk = predictions.filter(p => p.risk_percentage < 30).length;

        const diseaseCount = predictions.filter(p => p.has_disease).length;
        const healthyCount = predictions.length - diseaseCount;
        const diseaseRate = ((diseaseCount / predictions.length) * 100).toFixed(2);
        
        const avgRisk = (predictions.reduce((sum, p) => sum + p.risk_percentage, 0) / predictions.length).toFixed(2);
        const avgAge = (predictions.reduce((sum, p) => sum + (p.age_years || 0), 0) / predictions.length).toFixed(1);
        const avgWeight = (predictions.reduce((sum, p) => sum + (p.weight || 0), 0) / predictions.length).toFixed(2);

        // Update stat cards
        document.getElementById('totalPredictions').textContent = predictions.length;
        document.getElementById('highRiskCount').textContent = highRisk;
        document.getElementById('moderateRiskCount').textContent = moderateRisk;
        document.getElementById('lowRiskCount').textContent = lowRisk;

        // Update detailed stats
        document.getElementById('diseaseCount').textContent = diseaseCount;
        document.getElementById('healthyCount').textContent = healthyCount;
        document.getElementById('diseaseRate').textContent = diseaseRate + '%';
        document.getElementById('avgRisk').textContent = avgRisk + '%';
        document.getElementById('avgAge').textContent = avgAge + ' years';
        document.getElementById('avgWeight').textContent = avgWeight + ' kg';

        // Display risk distribution chart
        displayRiskDistributionChart(highRisk, moderateRisk, lowRisk);
    }

    function displayRiskDistributionChart(highRisk, moderateRisk, lowRisk, ) {
        const ctx = document.getElementById('riskDistributionChart');
        if (!ctx) return;

        const canvasContext = ctx.getContext('2d');
        if (window.riskDistChart) {
            window.riskDistChart.destroy();
        }

        window.riskDistChart = new Chart(canvasContext, {
            type: 'pie',
            data: {
                labels: ['High Risk', 'Moderate Risk', 'Low Risk'],
                datasets: [{
                    data: [highRisk, moderateRisk, lowRisk],
                    backgroundColor: [
                        'rgba(255, 107, 107, 0.8)',
                        'rgba(243, 156, 18, 0.8)',
                        'rgba(46, 204, 113, 0.8)'
                    ],
                    borderColor: [
                        'rgba(255, 107, 107, 1)',
                        'rgba(243, 156, 18, 1)',
                        'rgba(46, 204, 113, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    function displayPredictionsInTable(predictions) {
        const tableBody = document.getElementById('predictionTableBody');
        tableBody.innerHTML = '';

        predictions.forEach(pred => {
            addRowToTable(pred, tableBody);
        });
    }

    function displayMorePredictions() {
        let allPredictions = JSON.parse(localStorage.getItem('cardio_predictions') || '[]');
        const table = document.getElementById('predictionTableBody');
        const currentRows = table.querySelectorAll('tr').length;
        
        const nextPredictions = allPredictions.slice(currentRows, currentRows + 10);
        
        nextPredictions.forEach(pred => {
            addRowToTable(pred, table);
        });

        // Hide Load More button if no more predictions
        if (currentRows + nextPredictions.length >= allPredictions.length) {
            document.getElementById('loadMoreBtn').style.display = 'none';
        }
    }

    function addRowToTable(pred, tableBody = document.getElementById('predictionTableBody')) {
        const row = document.createElement('tr');
        const riskColor = pred.risk_percentage >= 60 ? '#FF6B6B' : pred.risk_percentage >= 30 ? '#F39C12' : '#2ECC71';
        
        row.innerHTML = `
            <td>
                <strong>${pred.prediction_id}</strong>
                ${pred.patientName ? `<br/><small>${pred.patientName}</small>` : ''}
            </td>
            <td>${pred.savedAt || (pred.timestamp ? new Date(pred.timestamp).toLocaleString() : 'N/A')}</td>
            <td>${pred.age_years}</td>
            <td><strong>${pred.risk_percentage.toFixed(2)}%</strong></td>
            <td><span style="background-color: ${riskColor}; color: white; padding: 5px 10px; border-radius: 3px;">${pred.risk_level}</span></td>
            <td>${pred.has_disease ? '⚠️ Yes' : '✅ No'}</td>
            <td>${pred.bp_systolic}/${pred.bp_diastolic}</td>
            <td>
                <button onclick="viewPredictionDetails('${pred.prediction_id}')" style="padding: 5px 10px; background: #3498db; color: white; border: none; border-radius: 3px; cursor: pointer; margin: 2px;">👁️ View</button>
                <button onclick="downloadPredictionPDF('${pred.prediction_id}', ${JSON.stringify(pred).replace(/"/g, '&quot;')})" style="padding: 5px 10px; background: #e74c3c; color: white; border: none; border-radius: 3px; cursor: pointer; margin: 2px;">📥 PDF</button>
                <button onclick="deletePrediction('${pred.prediction_id}')" style="padding: 5px 10px; background: #95a5a6; color: white; border: none; border-radius: 3px; cursor: pointer; margin: 2px;">🗑️ Delete</button>
            </td>
        `;
        
        tableBody.appendChild(row);
    }
});

function viewPredictionDetails(predictionId) {
    let allPredictions = JSON.parse(localStorage.getItem('cardio_predictions') || '[]');
    let prediction = allPredictions.find(p => p.prediction_id === predictionId);
    
    if (!prediction) {
        alert('❌ Prediction not found!');
        return;
    }

    // Create modal or detailed view
    const detailsHTML = `
    <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 10000;">
        <div style="background: white; padding: 30px; border-radius: 10px; max-width: 900px; max-height: 90vh; overflow-y: auto; box-shadow: 0 5px 30px rgba(0,0,0,0.3);">
            <h2>Prediction Details - ${predictionId}</h2>
            <button onclick="this.closest('div').parentElement.remove()" style="float: right; padding: 10px 15px; background: #95a5a6; color: white; border: none; border-radius: 5px; cursor: pointer;">✕ Close</button>
            
            <h3 style="color: #FF6B6B; margin-top: 20px;">👤 Patient Information</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Patient Name</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${prediction.patientName || 'Not Provided'}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Father's Name</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${prediction.fatherName || 'Not Provided'}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Blood Group</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${prediction.bloodGroup || 'Not Provided'}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Phone</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${prediction.phoneNumber || 'Not Provided'}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Doctor</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${prediction.doctorName || 'Not Provided'}</td></tr>
            </table>

            ${prediction.patientComments ? `
            <h3 style="color: #FF6B6B; margin-top: 20px;">📝 Patient Notes & Comments</h3>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #FF6B6B; margin-bottom: 20px;">
                <p style="white-space: pre-wrap; line-height: 1.6; color: #333;">${prediction.patientComments}</p>
            </div>
            ` : ''}

            <h3 style="color: #FF6B6B; margin-top: 20px;">📊 Prediction Results</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Risk Level</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${prediction.risk_level}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Risk Percentage</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${prediction.risk_percentage.toFixed(2)}%</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Disease Probability</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${(prediction.disease_probability * 100).toFixed(2)}%</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Prediction</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${prediction.has_disease ? '⚠️ High Risk - Disease Likely' : '✅ Good - Healthy'}</td></tr>
            </table>

            <h3 style="color: #FF6B6B; margin-top: 20px;">🏥 Health Parameters</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Age</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${prediction.age_years} years</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Gender</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${prediction.gender === 1 ? 'Female' : 'Male'}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Height</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${prediction.height} cm</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Weight</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${prediction.weight} kg</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>BMI</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${(prediction.weight / ((prediction.height / 100) ** 2)).toFixed(2)} kg/m²</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Blood Pressure</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${prediction.bp_systolic}/${prediction.bp_diastolic} mmHg</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Cholesterol</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${prediction.cholesterol}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Glucose</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${prediction.gluc}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Smoker</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${prediction.smoke ? 'Yes' : 'No'}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Alcohol</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${prediction.alco ? 'Yes' : 'No'}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Active</strong></td><td style="padding: 8px; border: 1px solid #ddd;">${prediction.active ? 'Yes' : 'No'}</td></tr>
            </table>

            <div style="margin-top: 20px; text-align: center;">
                <button onclick="downloadPredictionPDF('${prediction.prediction_id}', ${JSON.stringify(prediction).replace(/"/g, '&quot;')})" style="padding: 10px 20px; background: #e74c3c; color: white; border: none; border-radius: 5px; cursor: pointer; margin: 10px;">📥 Download PDF</button>
                <button onclick="downloadPredictionCSV('${prediction.prediction_id}', ${JSON.stringify(prediction).replace(/"/g, '&quot;')})" style="padding: 10px 20px; background: #16a085; color: white; border: none; border-radius: 5px; cursor: pointer; margin: 10px;">📊 Download CSV</button>
                <button onclick="this.closest('div').parentElement.remove()" style="padding: 10px 20px; background: #95a5a6; color: white; border: none; border-radius: 5px; cursor: pointer; margin: 10px;">Close</button>
            </div>
        </div>
    </div>
    `;

    document.body.insertAdjacentHTML('beforeend', detailsHTML);
}

function deletePrediction(predictionId) {
    if (confirm('Are you sure you want to delete this prediction?')) {
        let allPredictions = JSON.parse(localStorage.getItem('cardio_predictions') || '[]');
        allPredictions = allPredictions.filter(p => p.prediction_id !== predictionId);
        localStorage.setItem('cardio_predictions', JSON.stringify(allPredictions));
        alert('✅ Prediction deleted!');
        location.reload();
    }
}
