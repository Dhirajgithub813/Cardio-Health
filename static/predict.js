// Prediction page specific functionality

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('predictionForm');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultsContainer = document.getElementById('resultsContainer');
    const errorContainer = document.getElementById('errorContainer');

    // BMI Calculator
    const heightInput = document.getElementById('height');
    const weightInput = document.getElementById('weight');
    const bmiInput = document.getElementById('bmi');

    function calculateBMI() {
        const height = parseFloat(heightInput.value);
        const weight = parseFloat(weightInput.value);
        if (height && weight) {
            const bmi = (weight / ((height / 100) ** 2)).toFixed(2);
            bmiInput.value = bmi;
        }
    }

    heightInput.addEventListener('change', calculateBMI);
    weightInput.addEventListener('change', calculateBMI);

    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Hide previous results
        resultsContainer.style.display = 'none';
        errorContainer.style.display = 'none';
        loadingSpinner.style.display = 'flex';

        try {
            // Get form data
            const formData = new FormData(form);
            const ageInYears = parseInt(formData.get('age'));
            const ageInDays = Utils.yearsToAgeDays(ageInYears);
            
            const data = {
                age: ageInDays,
                gender: parseInt(formData.get('gender')),
                height: parseFloat(formData.get('height')),
                weight: parseFloat(formData.get('weight')),
                ap_hi: parseInt(formData.get('ap_hi')),
                ap_lo: parseInt(formData.get('ap_lo')),
                cholesterol: parseInt(formData.get('cholesterol')),
                gluc: parseInt(formData.get('gluc')),
                smoke: formData.get('smoke') ? 1 : 0,
                alco: formData.get('alco') ? 1 : 0,
                active: formData.get('active') ? 1 : 0
            };

            // Make prediction
            const response = await API.predict(data);

            if (response.error) {
                throw new Error(response.error);
            }

            // Display results
            displayResults(response, data);
            loadingSpinner.style.display = 'none';
            resultsContainer.style.display = 'block';

        } catch (error) {
            console.error('Error:', error);
            errorContainer.textContent = '❌ Error: ' + error.message;
            errorContainer.style.display = 'block';
            loadingSpinner.style.display = 'none';
        }
    });

    function displayResults(prediction, inputData) {
        // Risk meter chart
        const riskPercentage = prediction.risk_percentage;
        const healthyPercentage = 100 - riskPercentage;

        // Destroy existing chart if it exists
        if (window.riskChart) {
            window.riskChart.destroy();
        }

        const ctx = document.getElementById('riskChart').getContext('2d');
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
        const riskClass = getRiskClass(riskPercentage);
        
        riskSummary.className = `risk-summary ${riskClass}`;
        riskSummary.innerHTML = `
            <h3>Risk Assessment: <strong>${prediction.risk_level}</strong></h3>
            <p>Disease Probability: <strong>${(riskPercentage).toFixed(2)}%</strong></p>
            <p style="font-size: 0.85em; margin-top: 10px; opacity: 0.8;">
                <strong>Prediction ID:</strong> <code>${prediction.prediction_id}</code>
                <button onclick="copyToClipboard('${prediction.prediction_id}')" style="margin-left: 8px; padding: 2px 8px; cursor: pointer; border: 1px solid #999; border-radius: 3px; background: #f5f5f5; font-size: 0.9em;">📋 Copy</button>
            </p>
        `;

        // Details
        document.getElementById('diseaseProbability').textContent = 
            (prediction.disease_probability * 100).toFixed(2) + '%';
        document.getElementById('healthyProbability').textContent = 
            (prediction.healthy_probability * 100).toFixed(2) + '%';
        document.getElementById('riskLevel').innerHTML = 
            `<span class="risk-badge ${riskClass}">${prediction.risk_level}</span>`;

        // Recommendations with Results page link
        const recommendations = getRecommendations(prediction, inputData);
        const recommendationsList = document.getElementById('recommendationsList');
        recommendationsList.innerHTML = recommendations.map(rec => 
            `<li>${rec}</li>`
        ).join('');

        // Add view/manage prediction button
        const actionButtonsHTML = `
            <div style="margin-top: 20px; display: flex; gap: 10px; flex-wrap: wrap;">
                <a href="/results" class="btn-primary" style="display: inline-block; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; cursor: pointer;">📊 View in Results</a>
                <button onclick="savePredictionLocalStorage('${prediction.prediction_id}', ${JSON.stringify(prediction).replace(/'/g, "\\'")})" class="btn-secondary" style="padding: 10px 20px; background: #2ecc71; color: white; border: none; border-radius: 5px; cursor: pointer;">⭐ Save Prediction</button>
                <button onclick="sharePredictionID('${prediction.prediction_id}')" class="btn-secondary" style="padding: 10px 20px; background: #9b59b6; color: white; border: none; border-radius: 5px; cursor: pointer;">🔗 Share ID</button>
            </div>
        `;

        recommendationsList.parentElement.insertAdjacentHTML('afterend', actionButtonsHTML);
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
});

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
