// Prediction page specific functionality

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('predictionForm');
    const errorContainer = document.getElementById('errorContainer');

    console.log('Prediction form loaded:', form);
    console.log('Error container:', errorContainer);

    // BMI Calculator
    const heightInput = document.getElementById('height');
    const weightInput = document.getElementById('weight');
    const bmiInput = document.getElementById('bmi');

    if (!form) {
        console.error('Prediction form not found!');
        return;
    }

    function calculateBMI() {
        try {
            const height = parseFloat(heightInput.value);
            const weight = parseFloat(weightInput.value);
            
            // Only calculate if both values are valid numbers
            if (!isNaN(height) && !isNaN(weight) && height > 0 && weight > 0) {
                const bmi = (weight / ((height / 100) ** 2)).toFixed(2);
                bmiInput.value = bmi;
                console.log('BMI Calculated:', bmi);
            } else {
                if (bmiInput) {
                    bmiInput.value = '';
                }
            }
        } catch (error) {
            console.error('Error calculating BMI:', error);
        }
    }

    // Add event listeners for both input (real-time) and change (when leaving field)
    if (heightInput) {
        heightInput.addEventListener('input', calculateBMI);
        heightInput.addEventListener('change', calculateBMI);
    }
    if (weightInput) {
        weightInput.addEventListener('input', calculateBMI);
        weightInput.addEventListener('change', calculateBMI);
    }

    // Form submission
    // Add event listener to form
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        console.log('Form submitted');

        // Clear previous error
        errorContainer.style.display = 'none';
        errorContainer.textContent = '';
        
        // Show loading message
        const loadingMessage = document.createElement('div');
        loadingMessage.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 40px; border-radius: 10px; box-shadow: 0 5px 30px rgba(0,0,0,0.3); z-index: 10000; text-align: center; max-width: 400px;';
        loadingMessage.innerHTML = `
            <div class="spinner" style="width: 50px; height: 50px; margin: 0 auto 20px;"></div>
            <p style="font-size: 1.2em; color: #2c3e50; margin: 20px 0;">🔍 Analyzing your health data...</p>
            <p style="color: #7f8c8d; font-size: 0.95em;">Please wait while we process your prediction...</p>
        `;
        document.body.appendChild(loadingMessage);

        try {
            // Get form data
            const formData = new FormData(form);
            const ageInYears = parseInt(formData.get('age'));
            
            // Validate required numeric fields
            if (isNaN(ageInYears) || ageInYears < 1 || ageInYears > 120) {
                throw new Error('Age must be a number between 1 and 120');
            }
            
            const gender = parseInt(formData.get('gender'));
            if (isNaN(gender) || (gender !== 1 && gender !== 2)) {
                throw new Error('Please select a valid gender');
            }
            
            const height = parseFloat(formData.get('height'));
            const weight = parseFloat(formData.get('weight'));
            const ap_hi = parseInt(formData.get('ap_hi'));
            const ap_lo = parseInt(formData.get('ap_lo'));
            
            if (isNaN(height) || isNaN(weight) || isNaN(ap_hi) || isNaN(ap_lo)) {
                throw new Error('Please fill in all required health information');
            }

            const cholesterol = parseInt(formData.get('cholesterol'));
            const gluc = parseInt(formData.get('gluc'));

            if (isNaN(cholesterol) || isNaN(gluc)) {
                throw new Error('Please select valid cholesterol and glucose levels');
            }
            
            const data = {
                age: ageInYears,
                gender: gender,
                height: height,
                weight: weight,
                ap_hi: ap_hi,
                ap_lo: ap_lo,
                cholesterol: cholesterol,
                gluc: gluc,
                smoke: formData.get('smoke') ? 1 : 0,
                alco: formData.get('alco') ? 1 : 0,
                active: formData.get('active') ? 1 : 0,
                // Patient Information (optional)
                patientName: formData.get('patientName') || undefined,
                fatherName: formData.get('fatherName') || undefined,
                bloodGroup: formData.get('bloodGroup') || undefined,
                phoneNumber: formData.get('phoneNumber') || undefined,
                altPhoneNumber: formData.get('altPhoneNumber') || undefined,
                doctorName: formData.get('doctorName') || undefined
            };

            // Make prediction
            if (!API || !API.predict) {
                throw new Error('API is not available. Please refresh the page.');
            }

            console.log('Sending prediction data:', data);
            const response = await API.predict(data);

            console.log('API Response:', response);

            // Check for API errors
            if (response.error) {
                throw new Error(response.error || 'Unknown error occurred');
            }

            // Validate success response
            if (!response.prediction_id || response.prediction_id === undefined) {
                console.error('Response object:', response);
                throw new Error('Server returned invalid response - missing prediction ID');
            }

            // Store prediction data in localStorage
            storePredictionData(response, data);
            
            // Clear form after successful prediction
            form.reset();
            bmiInput.value = ''; // Clear BMI field

            // Remove loading message
            const loader = document.querySelector('[style*="position: fixed"]');
            if (loader) loader.remove();

            // Show success message with prediction ID
            const successDiv = document.createElement('div');
            successDiv.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 40px; border-radius: 10px; box-shadow: 0 5px 30px rgba(0,0,0,0.3); z-index: 10000; text-align: center; max-width: 500px;';
            successDiv.innerHTML = `
                <div style="font-size: 3em; margin-bottom: 20px;">✅</div>
                <h2 style="color: #2ecc71; margin-bottom: 15px;">Prediction Successful!</h2>
                <p style="color: #2c3e50; font-size: 1.05em; margin-bottom: 10px;">Your cardiovascular disease prediction has been analyzed.</p>
                <p style="color: #7f8c8d; margin-bottom: 20px;"><strong>Prediction ID:</strong> <code style="background: #f0f0f0; padding: 5px 10px; border-radius: 3px;">${response.prediction_id}</code></p>
                <p style="color: #555; margin-bottom: 30px;">Redirecting to results page in 3 seconds...</p>
                <div style="display: flex; gap: 10px; justify-content: center;">
                    <button onclick="window.location.href='/dashboard'" style="padding: 12px 30px; background: #4ECDC4; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; font-weight: 600;">📊 View Results Now</button>
                    <button onclick="this.closest('div').parentElement.remove()" style="padding: 12px 30px; background: #95a5a6; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; font-weight: 600;">Close</button>
                </div>
            `;
            document.body.appendChild(successDiv);

            // Redirect to dashboard after 3 seconds
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 3000);

        } catch (error) {
            console.error('Detailed Error:', error);
            
            // Remove loading message
            const loader = document.querySelector('[style*="position: fixed"]');
            if (loader) loader.remove();
            
            errorContainer.textContent = '❌ Error: ' + (error.message || 'An unexpected error occurred');
            errorContainer.style.display = 'block';
            
            // Scroll to error
            errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    });

    function displayResults(prediction, inputData) {
        // Validate prediction object has required fields
        if (!prediction) {
            throw new Error('No prediction data received');
        }

        // Set defaults for optional fields
        const riskPercentage = prediction.risk_percentage || 50;
        const healthyPercentage = 100 - riskPercentage;
        const diseaseProbability = prediction.disease_probability || 0;
        const healthyProbability = prediction.healthy_probability || 0;

        // Destroy existing chart if it exists
        if (window.riskChart && typeof window.riskChart.destroy === 'function') {
            window.riskChart.destroy();
        }

        // Get canvas element with safety check
        const chartCanvas = document.getElementById('riskChart');
        if (!chartCanvas) {
            console.error('Canvas element riskChart not found in DOM');
            throw new Error('Chart display element not found - please refresh the page');
        }

        const ctx = chartCanvas.getContext('2d');
        if (!ctx) {
            throw new Error('Failed to get chart context');
        }

        window.riskChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Disease Risk', 'Healthy'],
                datasets: [{
                    data: [riskPercentage, healthyPercentage],
                    backgroundColor: [
                        'rgba(255, 107, 107, 0.8)',
                        'rgba(46, 204, 113, 0.8)'
                    ],
                    borderColor: [
                        'rgba(255, 107, 107, 1)',
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
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + '%';
                            }
                        }
                    }
                }
            }
        });

        // Risk summary
        const riskSummary = document.getElementById('riskSummary');
        if (!riskSummary) {
            console.error('Risk summary element not found');
            throw new Error('Results display element not found');
        }

        const riskClass = getRiskClass(riskPercentage);
        const riskLevel = prediction.risk_level || 'Unknown';
        
        riskSummary.className = `risk-summary ${riskClass}`;
        riskSummary.innerHTML = `
            <h3>Risk Assessment: <strong>${riskLevel}</strong></h3>
            <p>Disease Probability: <strong>${(riskPercentage).toFixed(2)}%</strong></p>
            <p style="font-size: 0.85em; margin-top: 10px; opacity: 0.8;">
                <strong>Prediction ID:</strong> <code>${prediction.prediction_id || 'N/A'}</code>
                <button onclick="copyToClipboard('${prediction.prediction_id || ''}')" style="margin-left: 8px; padding: 2px 8px; cursor: pointer; border: 1px solid #999; border-radius: 3px; background: #f5f5f5; font-size: 0.9em;">📋 Copy</button>
            </p>
        `;

        // Details - with safe element access
        const diseaseProbEl = document.getElementById('diseaseProbability');
        const healthyProbEl = document.getElementById('healthyProbability');
        const riskLevelEl = document.getElementById('riskLevel');

        if (diseaseProbEl) {
            diseaseProbEl.textContent = (diseaseProbability * 100).toFixed(2) + '%';
        }
        if (healthyProbEl) {
            healthyProbEl.textContent = (healthyProbability * 100).toFixed(2) + '%';
        }
        if (riskLevelEl) {
            riskLevelEl.innerHTML = `<span class="risk-badge ${riskClass}">${riskLevel}</span>`;
        }

        // Recommendations with Results page link
        const recommendations = getRecommendations(prediction, inputData);
        const recommendationsList = document.getElementById('recommendationsList');
        if (!recommendationsList) {
            console.error('Recommendations list element not found');
            throw new Error('Recommendations display element not found');
        }

        recommendationsList.innerHTML = recommendations.map(rec => 
            `<li>${rec}</li>`
        ).join('');

        // Remove any existing action buttons
        const existingButtons = document.getElementById('actionButtons');
        if (existingButtons) {
            existingButtons.remove();
        }

        // Add view/manage prediction button
        const actionButtonsHTML = `
            <div id="actionButtons" style="margin-top: 20px; display: flex; gap: 10px; flex-wrap: wrap;">
                <button type="button" id="btnDownloadPDF" class="btn-secondary" style="padding: 10px 20px; background: #e74c3c; color: white; border: none; border-radius: 5px; cursor: pointer;">📥 Download PDF</button>
                <button type="button" id="btnDownloadCSV" class="btn-secondary" style="padding: 10px 20px; background: #16a085; color: white; border: none; border-radius: 5px; cursor: pointer;">📊 Download CSV</button>
                <button type="button" id="btnPrintReport" class="btn-secondary" style="padding: 10px 20px; background: #f39c12; color: white; border: none; border-radius: 5px; cursor: pointer;">🖨️ Print Report</button>
                <a href="/results" class="btn-primary" style="display: inline-block; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; cursor: pointer;">📊 View History</a>
                <a href="/feedback" class="btn-primary" style="display: inline-block; padding: 10px 20px; background: #9b59b6; color: white; text-decoration: none; border-radius: 5px; cursor: pointer;">💬 Share Feedback</a>
            </div>
        `;

        recommendationsList.parentElement.insertAdjacentHTML('afterend', actionButtonsHTML);
        
        // Bind button events after elements are created
        const predId = prediction.prediction_id;
        setTimeout(function() {
            const btnPDF = document.getElementById('btnDownloadPDF');
            const btnCSV = document.getElementById('btnDownloadCSV');
            const btnPrint = document.getElementById('btnPrintReport');
            
            if (btnPDF) {
                btnPDF.onclick = null; // Clear any previous handlers
                btnPDF.addEventListener('click', function(e) {
                    e.preventDefault();
                    console.log('Download PDF clicked for ID:', predId);
                    downloadPredictionPDF(predId);
                });
            }
            if (btnCSV) {
                btnCSV.onclick = null; // Clear any previous handlers
                btnCSV.addEventListener('click', function(e) {
                    e.preventDefault();
                    console.log('Download CSV clicked for ID:', predId);
                    downloadPredictionCSV(predId);
                });
            }
            if (btnPrint) {
                btnPrint.onclick = null; // Clear any previous handlers
                btnPrint.addEventListener('click', function(e) {
                    e.preventDefault();
                    console.log('Print Report clicked for ID:', predId);
                    printPredictionReport(predId);
                });
            }
        }, 100);
        
        // Store prediction in localStorage for access in results page
        storePredictionData(prediction, inputData);
    }

    function storePredictionData(prediction, inputData) {
        try {
            // Get existing predictions or create new array
            let allPredictions = JSON.parse(localStorage.getItem('cardio_predictions') || '[]');
            
            // Ensure prediction has required fields
            if (!prediction.prediction_id) {
                prediction.prediction_id = 'pred_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            }
            
            // Add patient and health info to prediction
            const fullPrediction = {
                ...prediction,
                patientName: inputData.patientName || 'Unknown Patient',
                fatherName: inputData.fatherName || '',
                bloodGroup: inputData.bloodGroup || '',
                phoneNumber: inputData.phoneNumber || '',
                altPhoneNumber: inputData.altPhoneNumber || '',
                doctorName: inputData.doctorName || '',
                healthData: inputData,
                savedAt: new Date().toLocaleString(),
                timestamp: Date.now()
            };
            
            // Check if this prediction already exists and remove it
            allPredictions = allPredictions.filter(p => p.prediction_id !== prediction.prediction_id);
            
            // Add to beginning of array
            allPredictions.unshift(fullPrediction);
            
            // Keep only last 100 predictions
            if (allPredictions.length > 100) {
                allPredictions = allPredictions.slice(0, 100);
            }
            
            localStorage.setItem('cardio_predictions', JSON.stringify(allPredictions));
            console.log('Prediction stored in localStorage:', fullPrediction);
        } catch (error) {
            console.error('Error storing prediction:', error);
        }
    }

    function downloadPredictionPDF(predictionId) {
        try {
            console.log('Starting PDF download for:', predictionId);
            
            // Get prediction from localStorage
            let allPredictions = JSON.parse(localStorage.getItem('cardio_predictions') || '[]');
            let prediction = allPredictions.find(p => p.prediction_id === predictionId);
            
            if (!prediction) {
                console.error('Prediction not found. Looking for:', predictionId);
                console.log('Available predictions:', allPredictions.map(p => p.prediction_id));
                alert('❌ Prediction not found! Please try again.');
                return;
            }
            
            console.log('Found prediction:', prediction);
            
            // Create PDF content
            const healthData = prediction.healthData || {};
            const pdfContent = `
CARDIOVASCULAR DISEASE PREDICTION REPORT
==========================================
Generated: ${new Date().toLocaleString()}
Report ID: ${predictionId}

PATIENT INFORMATION
-------------------
Patient Name: ${prediction.patientName || 'Not Provided'}
Father's Name: ${prediction.fatherName || 'Not Provided'}
Blood Group: ${prediction.bloodGroup || 'Not Provided'}
Phone Number: ${prediction.phoneNumber || 'Not Provided'}
Alternative Phone: ${prediction.altPhoneNumber || 'Not Provided'}
Reference Doctor: ${prediction.doctorName || 'Not Provided'}

PREDICTION RESULTS
------------------
Risk Level: ${prediction.risk_level}
Disease Risk Percentage: ${prediction.risk_percentage.toFixed(2)}%
Disease Probability: ${(prediction.disease_probability * 100).toFixed(2)}%
Healthy Probability: ${(prediction.healthy_probability * 100).toFixed(2)}%
Prediction: ${prediction.has_disease ? 'HIGH RISK - Disease Likely' : 'LOW RISK - Healthy'}

HEALTH PARAMETERS
-----------------
Age: ${healthData.age || 'N/A'} years
Gender: ${healthData.gender === 1 ? 'Male' : healthData.gender === 2 ? 'Female' : 'Not Specified'}
Height: ${healthData.height || 'N/A'} cm
Weight: ${healthData.weight || 'N/A'} kg
BMI: ${healthData.height && healthData.weight ? (healthData.weight / ((healthData.height / 100) ** 2)).toFixed(2) : 'N/A'} kg/m²
Systolic BP: ${healthData.ap_hi || 'N/A'} mmHg
Diastolic BP: ${healthData.ap_lo || 'N/A'} mmHg
Cholesterol Level: ${healthData.cholesterol !== undefined ? healthData.cholesterol : 'N/A'}
Glucose Level: ${healthData.gluc !== undefined ? healthData.gluc : 'N/A'}
Smoker: ${healthData.smoke ? 'Yes' : 'No'}
Alcohol Consumption: ${healthData.alco ? 'Yes' : 'No'}
Physically Active: ${healthData.active ? 'Yes' : 'No'}

RECOMMENDATIONS
----------------
1. Consult with a healthcare professional about your results
2. Follow doctor's advice for lifestyle modifications
3. Maintain regular health check-ups
4. Monitor your vital parameters regularly

Report generated by: CardioPredict v2.0
`;

            // Create blob and download
            const blob = new Blob([pdfContent], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Cardio_Prediction_${predictionId}_${new Date().toISOString().slice(0, 10)}.txt`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            alert('✅ Prediction report downloaded successfully!');
        } catch (error) {
            console.error('Error downloading PDF:', error);
            alert('❌ Error downloading report: ' + error.message);
        }
    }

    function downloadPredictionCSV(predictionId) {
        try {
            console.log('Starting CSV download for:', predictionId);
            
            // Get prediction from localStorage
            let allPredictions = JSON.parse(localStorage.getItem('cardio_predictions') || '[]');
            let prediction = allPredictions.find(p => p.prediction_id === predictionId);
            
            if (!prediction) {
                console.error('Prediction not found. Looking for:', predictionId);
                alert('❌ Prediction not found! Please try again.');
                return;
            }
            
            console.log('Found prediction:', prediction);
            
            // Create CSV content
            const healthData = prediction.healthData || {};
            const csvContent = `Field,Value
Prediction ID,${predictionId}
Patient Name,${prediction.patientName || 'N/A'}
Father's Name,${prediction.fatherName || 'N/A'}
Blood Group,${prediction.bloodGroup || 'N/A'}
Phone Number,${prediction.phoneNumber || 'N/A'}
Reference Doctor,${prediction.doctorName || 'N/A'}
Generated Date,${new Date().toLocaleString()}
,
Age (years),${healthData.age || 'N/A'}
Gender,${healthData.gender === 1 ? 'Male' : healthData.gender === 2 ? 'Female' : 'N/A'}
Height (cm),${healthData.height || 'N/A'}
Weight (kg),${healthData.weight || 'N/A'}
BMI,${healthData.height && healthData.weight ? (healthData.weight / ((healthData.height / 100) ** 2)).toFixed(2) : 'N/A'}
Systolic BP,${healthData.ap_hi || 'N/A'}
Diastolic BP,${healthData.ap_lo || 'N/A'}
Cholesterol,${healthData.cholesterol !== undefined ? healthData.cholesterol : 'N/A'}
Glucose,${healthData.gluc !== undefined ? healthData.gluc : 'N/A'}
Smoker,${healthData.smoke ? 'Yes' : 'No'}
Alcohol,${healthData.alco ? 'Yes' : 'No'}
Active,${healthData.active ? 'Yes' : 'No'}
,
Risk Level,${prediction.risk_level}
Risk Percentage,${prediction.risk_percentage.toFixed(2)}%
Disease Probability,${(prediction.disease_probability * 100).toFixed(2)}%
Healthy Probability,${(prediction.healthy_probability * 100).toFixed(2)}%
Prediction,${prediction.has_disease ? 'High Risk' : 'Healthy'}`;

            // Create blob and download
            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Cardio_Prediction_${predictionId}_${new Date().toISOString().slice(0, 10)}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            alert('✅ Prediction data exported as CSV successfully!');
        } catch (error) {
            console.error('Error downloading CSV:', error);
            alert('❌ Error exporting data: ' + error.message);
        }
    }

    function printPredictionReport(predictionId) {
        try {
            console.log('Starting print for:', predictionId);
            
            // Get prediction from localStorage
            let allPredictions = JSON.parse(localStorage.getItem('cardio_predictions') || '[]');
            let prediction = allPredictions.find(p => p.prediction_id === predictionId);
            
            if (!prediction) {
                console.error('Prediction not found. Looking for:', predictionId);
                alert('❌ Prediction not found!');
                return;
            }

            console.log('Found prediction:', prediction);
            
            // Extract health data
            const healthData = prediction.healthData || {};

        // Create print window
        const printWindow = window.open('', '_blank');
        const printContent = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>CardioPredict Report - ${predictionId}</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: Arial, sans-serif; padding: 20px; background: white; }
                .header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #FF6B6B; padding-bottom: 15px; }
                h1 { color: #2c3e50; }
                .section { margin: 20px 0; }
                .section-title { background: #FF6B6B; color: white; padding: 10px; font-weight: bold; margin-bottom: 10px; }
                table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                td { padding: 8px; border: 1px solid #ddd; }
                .label { font-weight: bold; width: 40%; }
                .value { width: 60%; }
                .risk-high { color: red; font-weight: bold; }
                .risk-medium { color: orange; font-weight: bold; }
                .risk-low { color: green; font-weight: bold; }
                .footer { margin-top: 30px; text-align: center; font-size: 12px; color: #999; }
                @media print { 
                    body { padding: 0; }
                    .no-print { display: none; }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>❤️ CardioPredict Report</h1>
                <p>Cardiovascular Disease Prediction Analysis</p>
                <p>Generated: ${new Date().toLocaleString()}</p>
                <p>Report ID: ${predictionId}</p>
            </div>

            <div class="section">
                <div class="section-title">PATIENT INFORMATION</div>
                <table>
                    <tr><td class="label">Patient Name</td><td>${prediction.patientName || 'Not Provided'}</td></tr>
                    <tr><td class="label">Father's Name</td><td>${prediction.fatherName || 'Not Provided'}</td></tr>
                    <tr><td class="label">Blood Group</td><td>${prediction.bloodGroup || 'Not Provided'}</td></tr>
                    <tr><td class="label">Phone Number</td><td>${prediction.phoneNumber || 'Not Provided'}</td></tr>
                    <tr><td class="label">Alternative Phone</td><td>${prediction.altPhoneNumber || 'Not Provided'}</td></tr>
                    <tr><td class="label">Reference Doctor</td><td>${prediction.doctorName || 'Not Provided'}</td></tr>
                </table>
            </div>

            <div class="section">
                <div class="section-title">PREDICTION RESULTS</div>
                <table>
                    <tr><td class="label">Risk Assessment</td><td class="risk-${prediction.risk_level === 'High Risk' ? 'high' : prediction.risk_level === 'Moderate Risk' ? 'medium' : 'low'}">${prediction.risk_level}</td></tr>
                    <tr><td class="label">Risk Percentage</td><td>${prediction.risk_percentage.toFixed(2)}%</td></tr>
                    <tr><td class="label">Disease Probability</td><td>${(prediction.disease_probability * 100).toFixed(2)}%</td></tr>
                    <tr><td class="label">Healthy Probability</td><td>${(prediction.healthy_probability * 100).toFixed(2)}%</td></tr>
                </table>
            </div>

            <div class="section">
                <div class="section-title">HEALTH PARAMETERS</div>
                <table>
                    <tr><td class="label">Age</td><td>${healthData.age || 'N/A'} years</td></tr>
                    <tr><td class="label">Gender</td><td>${healthData.gender === 1 ? 'Male' : healthData.gender === 2 ? 'Female' : 'Not Specified'}</td></tr>
                    <tr><td class="label">Height</td><td>${healthData.height || 'N/A'} cm</td></tr>
                    <tr><td class="label">Weight</td><td>${healthData.weight || 'N/A'} kg</td></tr>
                    <tr><td class="label">BMI</td><td>${healthData.height && healthData.weight ? (healthData.weight / ((healthData.height / 100) ** 2)).toFixed(2) : 'N/A'} kg/m²</td></tr>
                    <tr><td class="label">Blood Pressure</td><td>${healthData.ap_hi || 'N/A'}/${healthData.ap_lo || 'N/A'} mmHg</td></tr>
                    <tr><td class="label">Cholesterol</td><td>${healthData.cholesterol !== undefined ? healthData.cholesterol : 'N/A'}</td></tr>
                    <tr><td class="label">Glucose</td><td>${healthData.gluc !== undefined ? healthData.gluc : 'N/A'}</td></tr>
                    <tr><td class="label">Smoker</td><td>${healthData.smoke ? 'Yes' : 'No'}</td></tr>
                    <tr><td class="label">Alcohol</td><td>${healthData.alco ? 'Yes' : 'No'}</td></tr>
                    <tr><td class="label">Physically Active</td><td>${healthData.active ? 'Yes' : 'No'}</td></tr>
                </table>
            </div>

            <div class="footer">
                <p>This report is generated by CardioPredict v2.0 - Cardiovascular Disease Prediction System</p>
                <p>Disclaimer: This is an AI-based assessment and should not replace professional medical advice.</p>
                <p>Always consult with a qualified healthcare professional for proper diagnosis and treatment.</p>
            </div>

            <div style="text-align: center; margin-top: 20px; gap: 10px;">
                <button onclick="window.print()" class="no-print" style="padding: 10px 20px; margin: 10px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 14px;">🖨️ Print</button>
                <button onclick="window.close()" class="no-print" style="padding: 10px 20px; margin: 10px; background: #95a5a6; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 14px;">Close</button>
            </div>
        </body>
        </html>`;
        
        printWindow.document.write(printContent);
        printWindow.document.close();
        setTimeout(() => { printWindow.print(); }, 250);
        } catch (error) {
            console.error('Error printing report:', error);
            alert('❌ Error printing report: ' + error.message);
        }
    }

    function getRiskClass(percentage) {
        if (percentage < 30) return 'low-risk';
        if (percentage < 60) return 'moderate-risk';
        return 'high-risk';
    }

    function getRecommendations(prediction, inputData) {
        const recommendations = [];

        if (prediction.risk_percentage >= 60) {
            recommendations.push('🔴 <strong>High Risk:</strong> Please consult with a healthcare professional immediately');
            recommendations.push('Schedule a comprehensive cardiovascular evaluation');
            recommendations.push('Discuss medications or lifestyle modifications with your doctor');
        } else if (prediction.risk_percentage >= 30) {
            recommendations.push('🟡 <strong>Moderate Risk:</strong> Consider consulting with a healthcare provider');
            recommendations.push('Monitor your blood pressure regularly');
            recommendations.push('Review and improve your lifestyle habits');
        } else {
            recommendations.push('🟢 <strong>Low Risk:</strong> Maintain your current healthy habits');
            recommendations.push('Continue regular exercise and balanced diet');
            recommendations.push('Have regular health check-ups');
        }

        // Specific recommendations based on inputs
        if (inputData.ap_hi > 140 || inputData.ap_lo > 90) {
            recommendations.push('Your blood pressure is elevated - monitor it regularly');
        }

        if (inputData.cholesterol >= 2) {
            recommendations.push('Consider dietary changes to manage cholesterol levels');
        }

        if (inputData.smoke === 1) {
            recommendations.push('Smoking cessation is strongly recommended');
        }

        if (inputData.active === 0) {
            recommendations.push('Increase physical activity - aim for 30 minutes of exercise daily');
        }

        if (inputData.weight > 80) {
            const bmi = (inputData.weight / ((inputData.height / 100) ** 2)).toFixed(2);
            if (bmi > 25) {
                recommendations.push(`Your BMI (${bmi}) is above normal - consider weight management`);
            }
        }

        return recommendations;
    }
}); // End of DOMContentLoaded event listener

// Helper function to copy prediction ID to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('✅ Prediction ID copied to clipboard: ' + text);
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('Could not copy to clipboard');
    });
}

// Helper function to save prediction locally for reference
function savePredictionLocalStorage(predictionId, predictionData) {
    try {
        // Get existing saved predictions or create new array
        let savedPredictions = JSON.parse(localStorage.getItem('savedPredictions')) || [];
        
        // Check if already saved
        if (savedPredictions.some(p => p.prediction_id === predictionId)) {
            alert('⭐ This prediction is already saved!');
            return;
        }
        
        // Add metadata
        const predictionWithMeta = {
            ...predictionData,
            savedAt: new Date().toISOString(),
            notes: ''
        };
        
        // Add to saved predictions
        savedPredictions.unshift(predictionWithMeta);
        
        // Keep only last 50 saved predictions
        savedPredictions = savedPredictions.slice(0, 50);
        
        // Save to localStorage
        localStorage.setItem('savedPredictions', JSON.stringify(savedPredictions));
        alert('⭐ Prediction saved! You can manage saved predictions in the Results page.');
        
    } catch (error) {
        console.error('Error saving prediction:', error);
        alert('Could not save prediction locally');
    }
}

// Helper function to share prediction ID via text
function sharePredictionID(predictionId) {
    const shareText = `Check out my CardioPredict result: ${predictionId}`;
    
    if (navigator.share) {
        // Use native share if available (mobile)
        navigator.share({
            title: 'CardioPredict Result',
            text: shareText,
            url: window.location.href
        }).catch(err => console.log('Share cancelled:', err));
    } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(shareText).then(() => {
            alert('🔗 Share text copied:\n' + shareText);
        }).catch(() => {
            alert('Share text: ' + shareText);
        });
    }
}


