// Analytics page functionality

document.addEventListener('DOMContentLoaded', async function() {
    const analyticsContent = document.getElementById('analyticsContent');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const errorContainer = document.getElementById('errorContainer');

    try {
        // Fetch statistics
        const stats = await API.getStatistics();

        if (stats.error) {
            throw new Error(stats.error);
        }

        // Display statistics
        displayStatistics(stats);
        loadingSpinner.style.display = 'none';
        analyticsContent.style.display = 'block';

    } catch (error) {
        console.error('Error loading analytics:', error);
        errorContainer.textContent = '❌ Error: ' + error.message;
        errorContainer.style.display = 'block';
        loadingSpinner.style.display = 'none';
    }

    function displayStatistics(stats) {
        // Update stat cards
        document.getElementById('totalRecords').textContent = 
            Utils.formatNumber(stats.total_records);
        document.getElementById('diseaseCount').textContent = 
            Utils.formatNumber(stats.disease_cases);
        document.getElementById('healthyCount').textContent = 
            Utils.formatNumber(stats.healthy_cases);
        document.getElementById('diseasePercentage').textContent = 
            stats.disease_percentage.toFixed(2) + '%';

        // Disease distribution chart
        const diseaseCtx = document.getElementById('diseaseChart').getContext('2d');
        if (window.diseaseChart && typeof window.diseaseChart.destroy === 'function') {
            window.diseaseChart.destroy();
        }

        window.diseaseChart = new Chart(diseaseCtx, {
            type: 'doughnut',
            data: {
                labels: ['With Disease', 'Healthy'],
                datasets: [{
                    data: [stats.disease_cases, stats.healthy_cases],
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
                    }
                }
            }
        });

        // Age distribution chart
        const ageCtx = document.getElementById('ageChart').getContext('2d');
        if (window.ageChart && typeof window.ageChart.destroy === 'function') {
            window.ageChart.destroy();
        }

        // Age ranges for demonstration
        const ageMin = Utils.ageInYears(stats.features.age.min);
        const ageMax = Utils.ageInYears(stats.features.age.max);
        const ageMean = Utils.ageInYears(stats.features.age.mean);

        window.ageChart = new Chart(ageCtx, {
            type: 'bar',
            data: {
                labels: ['Min', 'Average', 'Max'],
                datasets: [{
                    label: 'Age (years)',
                    data: [ageMin, ageMean, ageMax],
                    backgroundColor: [
                        'rgba(78, 205, 196, 0.8)',
                        'rgba(255, 107, 107, 0.8)',
                        'rgba(76, 175, 80, 0.8)'
                    ],
                    borderColor: [
                        'rgba(78, 205, 196, 1)',
                        'rgba(255, 107, 107, 1)',
                        'rgba(76, 175, 80, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
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
        });

        // Feature statistics
        const features = stats.features;

        document.getElementById('ageMin').textContent = Utils.ageInYears(features.age.min) + ' years';
        document.getElementById('ageMax').textContent = Utils.ageInYears(features.age.max) + ' years';
        document.getElementById('ageMean').textContent = Utils.ageInYears(features.age.mean) + ' years';

        document.getElementById('weightMin').textContent = features.weight.min.toFixed(1) + ' kg';
        document.getElementById('weightMax').textContent = features.weight.max.toFixed(1) + ' kg';
        document.getElementById('weightMean').textContent = features.weight.mean.toFixed(1) + ' kg';

        document.getElementById('heightMin').textContent = features.height.min.toFixed(0) + ' cm';
        document.getElementById('heightMax').textContent = features.height.max.toFixed(0) + ' cm';
        document.getElementById('heightMean').textContent = features.height.mean.toFixed(0) + ' cm';

        // Update insights
        document.getElementById('insightTotal').textContent = 
            Utils.formatNumber(stats.total_records);
        document.getElementById('insightPercent').textContent = 
            stats.disease_percentage.toFixed(1);
        document.getElementById('insightAge').textContent = 
            Utils.ageInYears(features.age.mean);
        
        // Calculate average BMI
        const avgBMI = (features.weight.mean / ((features.height.mean / 100) ** 2)).toFixed(1);
        document.getElementById('insightBMI').textContent = avgBMI;
    }
});
