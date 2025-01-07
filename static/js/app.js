let currentCombinations = [];

function generateCombinations() {
    const totalNumbers = parseInt(document.getElementById('total_numbers').value);
    const choose = parseInt(document.getElementById('choose').value);

    if (isNaN(totalNumbers) || isNaN(choose)) {
        alert('Please enter valid numbers');
        return;
    }

    const data = {
        total_numbers: totalNumbers,
        choose: choose,
        filters: {}
    };

    console.log('Sending request:', data);

    fetch('/filter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Received data:', data);
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        currentCombinations = data.combinations;
        updateResults(data);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error generating combinations: ' + error);
    });
}

function applyFilter(filterType) {
    const totalNumbers = parseInt(document.getElementById('total_numbers').value);
    const choose = parseInt(document.getElementById('choose').value);

    if (isNaN(totalNumbers) || isNaN(choose)) {
        alert('Please generate combinations first');
        return;
    }

    let filterData = {};

    try {
        switch (filterType) {
            case 'sum':
                const minSum = parseInt(document.getElementById('min_sum').value);
                const maxSum = parseInt(document.getElementById('max_sum').value);
                if (isNaN(minSum) || isNaN(maxSum)) {
                    alert('Please enter valid sum range');
                    return;
                }
                filterData = { sum: { min_sum: minSum, max_sum: maxSum } };
                break;

            case 'even_odd':
                const minEven = parseInt(document.getElementById('min_even').value);
                const maxEven = parseInt(document.getElementById('max_even').value);
                if (isNaN(minEven) || isNaN(maxEven)) {
                    alert('Please enter valid even/odd range');
                    return;
                }
                filterData = { even_odd: { min_even: minEven, max_even: maxEven } };
                break;

            case 'distance':
                const minDist = parseInt(document.getElementById('min_distance').value);
                const maxDist = parseInt(document.getElementById('max_distance').value);
                if (isNaN(minDist) || isNaN(maxDist)) {
                    alert('Please enter valid distance range');
                    return;
                }
                filterData = { distance: { min_distance: minDist, max_distance: maxDist } };
                break;

            case 'include':
                const includeStr = document.getElementById('include_numbers').value;
                const includeNums = includeStr.split(',').map(n => parseInt(n.trim())).filter(n => !isNaN(n));
                if (includeNums.length === 0) {
                    alert('Please enter valid numbers to include');
                    return;
                }
                filterData = { include: { numbers: includeNums } };
                break;

            case 'exclude':
                const excludeStr = document.getElementById('exclude_numbers').value;
                const excludeNums = excludeStr.split(',').map(n => parseInt(n.trim())).filter(n => !isNaN(n));
                if (excludeNums.length === 0) {
                    alert('Please enter valid numbers to exclude');
                    return;
                }
                filterData = { exclude: { numbers: excludeNums } };
                break;

            case 'random':
                const count = parseInt(document.getElementById('random_count').value);
                if (isNaN(count) || count < 1) {
                    alert('Please enter a valid number of combinations');
                    return;
                }
                filterData = { random: { count: count } };
                break;
        }

        console.log('Applying filter:', filterType, filterData);

        const data = {
            total_numbers: totalNumbers,
            choose: choose,
            filters: filterData
        };

        fetch('/filter', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Filter response:', data);
            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }
            currentCombinations = data.combinations;
            updateResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error applying filter: ' + error);
        });
    } catch (error) {
        console.error('Error:', error);
        alert('Error processing filter: ' + error);
    }
}

function updateResults(data) {
    const resultsDiv = document.getElementById('combinations');
    const totalDiv = document.getElementById('total_combinations');

    if (data.total === 0) {
        resultsDiv.innerHTML = '<div class="alert alert-warning">No combinations found matching the criteria.</div>';
    } else {
        let html = `<div class="alert alert-success">Found ${data.total} combinations</div>`;
        html += '<div class="combinations-list">';
        data.combinations.forEach((combo, index) => {
            if (index < 10) { // Show only first 10 combinations
                html += `<div class="combination-item">${combo.join(', ')}</div>`;
            }
        });
        if (data.total > 10) {
            html += `<div class="more-combinations">... and ${data.total - 10} more combinations</div>`;
        }
        html += '</div>';
        resultsDiv.innerHTML = html;
    }
    
    totalDiv.textContent = data.total;
}
