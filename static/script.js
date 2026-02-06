// Global script for all pages

// Smooth scroll anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href !== '#') {
            e.preventDefault();
            const element = document.querySelector(href);
            if (element) {
                element.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        }
    });
});

// API Helper Functions
const API = {
    base: 'http://localhost:5000/api',

    async predict(data) {
        try {
            const response = await fetch(`${this.base}/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            // If response is not ok, add error flag
            if (!response.ok) {
                result.error = result.error || result.message || `HTTP ${response.status}`;
            }
            
            return result;
        } catch (error) {
            console.error('Prediction fetch error:', error);
            throw error;
        }
    },

    async getStatistics() {
        try {
            const response = await fetch(`${this.base}/statistics`);
            return await response.json();
        } catch (error) {
            console.error('Statistics error:', error);
            throw error;
        }
    },

    async getModelInfo() {
        try {
            const response = await fetch(`${this.base}/model-info`);
            return await response.json();
        } catch (error) {
            console.error('Model info error:', error);
            throw error;
        }
    },

    async healthCheck() {
        try {
            const response = await fetch(`${this.base}/health`);
            return await response.json();
        } catch (error) {
            console.error('Health check error:', error);
            return { status: 'error' };
        }
    },

    // ===== Prediction Status Tracking APIs =====

    async getPredictionStatus(predictionId) {
        try {
            const response = await fetch(`${this.base}/prediction/${predictionId}`);
            return await response.json();
        } catch (error) {
            console.error('Error getting prediction status:', error);
            throw error;
        }
    },

    async getPredictionStatusSummary() {
        try {
            const response = await fetch(`${this.base}/prediction-status`);
            return await response.json();
        } catch (error) {
            console.error('Error getting prediction status summary:', error);
            throw error;
        }
    },

    async getPredictionHistory(limit = 100, offset = 0) {
        try {
            const response = await fetch(`${this.base}/prediction-history?limit=${limit}&offset=${offset}`);
            return await response.json();
        } catch (error) {
            console.error('Error getting prediction history:', error);
            throw error;
        }
    },

    async getPredictionDetailedStats() {
        try {
            const response = await fetch(`${this.base}/prediction-stats`);
            return await response.json();
        } catch (error) {
            console.error('Error getting prediction statistics:', error);
            throw error;
        }
    },

    async getPredictionHealth() {
        try {
            const response = await fetch(`${this.base}/prediction-health`);
            return await response.json();
        } catch (error) {
            console.error('Error getting prediction health:', error);
            throw error;
        }
    },

    async clearPredictionHistory() {
        try {
            const response = await fetch(`${this.base}/clear-history`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            return await response.json();
        } catch (error) {
            console.error('Error clearing prediction history:', error);
            throw error;
        }
    }
};

// Utility Functions
const Utils = {
    formatNumber(num) {
        return num.toLocaleString('en-US', { maximumFractionDigits: 2 });
    },

    calculateBMI(height, weight) {
        // height in cm, weight in kg
        const heightM = height / 100;
        return (weight / (heightM * heightM)).toFixed(2);
    },

    ageInYears(ageInDays) {
        return Math.round(ageInDays / 365.25);
    },

    yearsToAgeDays(years) {
        return Math.round(years * 365.25);
    },

    getDiseaseRisk(percentage) {
        if (percentage < 30) {
            return { level: 'Low Risk', color: 'green' };
        } else if (percentage < 60) {
            return { level: 'Moderate Risk', color: 'orange' };
        } else {
            return { level: 'High Risk', color: 'red' };
        }
    }
};

// Chart configuration
const chartConfig = {
    doughnut: {
        type: 'doughnut',
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    },
    bar: {
        type: 'bar',
        options: {
            responsive: true,
            maintainAspectRatio: true,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true
                }
            }
        }
    }
};

// Log when page loads
console.log('CardioPredict Application Loaded');
