from flask import Flask, jsonify, request
from itertools import combinations
import random

app = Flask(__name__)

def apply_sum_filter(combo, min_sum, max_sum):
    combo_sum = sum(combo)
    return min_sum <= combo_sum <= max_sum

def apply_consecutive_filter(combo, max_consecutive):
    sorted_combo = sorted(combo)
    consecutive_count = 1
    current_max = 1
    
    for i in range(1, len(sorted_combo)):
        if sorted_combo[i] == sorted_combo[i-1] + 1:
            consecutive_count += 1
            current_max = max(current_max, consecutive_count)
        else:
            consecutive_count = 1
            
    return current_max <= max_consecutive

def apply_even_odd_filter(combo, min_even, max_even):
    even_count = sum(1 for num in combo if num % 2 == 0)
    return min_even <= even_count <= max_even

def apply_include_filter(combinations, must_include):
    """
    New implementation of include filter using direct list comparison
    """
    if not must_include:
        return combinations
        
    filtered = []
    for combo in combinations:
        include_all = True
        for number in must_include:
            if number not in combo:
                include_all = False
                break
        if include_all:
            filtered.append(combo)
    return filtered

def apply_exclude_filter(combo, must_exclude):
    return not any(num in combo for num in must_exclude)

def random_combinations(combinations, num_sets):
    if not combinations:
        return []
    try:
        num_sets = int(num_sets)
        if num_sets <= 0:
            return []
        # Use random.sample if we want fewer sets than available
        if num_sets <= len(combinations):
            return random.sample(combinations, num_sets)
        # If we want more sets than available, repeat the process
        result = []
        while len(result) < num_sets:
            needed = min(num_sets - len(result), len(combinations))
            result.extend(random.sample(combinations, needed))
        return result
    except:
        return []

@app.route('/')
def home():
    return """
    <html>
    <head>
        <title>Lottery Filter</title>
        <style>
            body { font-family: Arial; margin: 40px; }
            .filter {
                margin: 20px 0;
                padding: 20px;
                background: #f8f8f8;
                display: flex;
                align-items: center;
                gap: 20px;
            }
            .filter-controls {
                min-width: 300px;
                flex-shrink: 0;
            }
            .filter-buttons {
                margin-top: 10px;
                display: flex;
                gap: 10px;
            }
            .btn-run {
                background: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                cursor: pointer;
                border-radius: 4px;
            }
            .btn-skip {
                background: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                cursor: pointer;
                border-radius: 4px;
            }
            .filter-result {
                flex-grow: 1;
                padding: 10px;
                background: #fff;
                border-radius: 4px;
                border: 1px solid #ddd;
            }
            .number-grid {
                display: grid;
                grid-template-columns: repeat(6, 30px);
                gap: 3px;
                margin: 10px 0;
            }
            .number-btn {
                padding: 5px;
                border: 1px solid #ccc;
                background: white;
                cursor: pointer;
                border-radius: 3px;
                font-size: 12px;
            }
            .number-btn.selected {
                background: #007bff;
                color: white;
            }
            .number-btn:hover {
                background: #e9ecef;
            }
            .number-btn.selected:hover {
                background: #0056b3;
            }
            .status {
                margin-left: 10px;
                padding: 4px 8px;
                border-radius: 4px;
                background: #e9ecef;
                font-size: 0.9em;
            }
            .combo {
                background: #f8f9fa;
                padding: 8px;
                margin: 5px 0;
                border-radius: 4px;
            }
            .stats {
                color: #666;
                font-size: 0.9em;
            }
            .initial-setup {
                background: #e3f2fd;
                padding: 20px;
                border-radius: 4px;
                margin-bottom: 30px;
            }
            .filter-title {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .help-icon {
                cursor: help;
                color: #666;
                font-size: 18px;
                position: relative;
            }
            .tooltip {
                visibility: hidden;
                background-color: #333;
                color: white;
                text-align: center;
                padding: 10px;
                border-radius: 6px;
                position: absolute;
                z-index: 1;
                width: 220px;
                top: 100%;
                left: 50%;
                transform: translateX(-50%);
                margin-top: 5px;
                font-size: 14px;
                line-height: 1.4;
            }
            .help-icon:hover .tooltip {
                visibility: visible;
            }
        </style>
    </head>
    <body>
        <div class="initial-setup">
            <h2>Lottery Filter</h2>
            <label>Total Numbers:</label>
            <input type="number" id="total" value="11" min="1">
            
            <label style="margin-left: 20px;">Choose:</label>
            <input type="number" id="choose" value="6" min="1">
            
            <button class="btn-run" onclick="calculate()" style="margin-left: 20px;">Calculate Initial Combinations</button>
            <div class="filter-result" id="initial-result">
                <span class="status">Waiting for calculation...</span>
            </div>
        </div>

        <div class="filter">
            <div class="filter-controls">
                <div class="filter-title">
                    <h3>Must Include Numbers</h3>
                    <span class="help-icon">?
                        <span class="tooltip">Select numbers that MUST appear in your combinations. Only combinations containing ALL selected numbers will be shown.</span>
                    </span>
                </div>
                <div class="number-grid" id="includeGrid"></div>
                <div class="filter-buttons">
                    <button class="btn-run" onclick="runIncludeFilter()">Run</button>
                    <button class="btn-skip" onclick="skipIncludeFilter()">Skip</button>
                </div>
            </div>
            <div class="filter-result" id="include-result">
                <span class="status">Waiting...</span>
            </div>
        </div>

        <div class="filter">
            <div class="filter-controls">
                <div class="filter-title">
                    <h3>Must Exclude Numbers</h3>
                    <span class="help-icon">?
                        <span class="tooltip">Select numbers that should NOT appear in your combinations. Combinations containing ANY of these numbers will be removed.</span>
                    </span>
                </div>
                <div class="number-grid" id="excludeGrid"></div>
                <div class="filter-buttons">
                    <button class="btn-run" onclick="runFilter('exclude')">Run</button>
                    <button class="btn-skip" onclick="skipFilter('exclude')">Skip</button>
                </div>
            </div>
            <div class="filter-result" id="exclude-result">
                <span class="status">Waiting...</span>
            </div>
        </div>

        <div class="filter">
            <div class="filter-controls">
                <div class="filter-title">
                    <h3>Sum Filter</h3>
                    <span class="help-icon">?
                        <span class="tooltip">Control the total sum of your numbers. Set minimum and maximum values to filter combinations based on their sum.</span>
                    </span>
                </div>
                <label>Min Sum:</label>
                <input type="number" id="minSum" value="21"><br><br>
                <label>Max Sum:</label>
                <input type="number" id="maxSum" value="66">
                <div class="filter-buttons">
                    <button class="btn-run" onclick="runFilter('sum')">Run</button>
                    <button class="btn-skip" onclick="skipFilter('sum')">Skip</button>
                </div>
            </div>
            <div class="filter-result" id="sum-result">
                <span class="status">Waiting...</span>
            </div>
        </div>

        <div class="filter">
            <div class="filter-controls">
                <div class="filter-title">
                    <h3>Consecutive Numbers</h3>
                    <span class="help-icon">?
                        <span class="tooltip">Control how many consecutive numbers can appear in your combinations. For example, setting to 3 allows sequences like 1,2,3 but not 1,2,3,4.</span>
                    </span>
                </div>
                <label>Max Consecutive:</label>
                <input type="number" id="maxConsecutive" value="3" min="1" max="6">
                <div class="filter-buttons">
                    <button class="btn-run" onclick="runFilter('consecutive')">Run</button>
                    <button class="btn-skip" onclick="skipFilter('consecutive')">Skip</button>
                </div>
            </div>
            <div class="filter-result" id="consecutive-result">
                <span class="status">Waiting...</span>
            </div>
        </div>

        <div class="filter">
            <div class="filter-controls">
                <div class="filter-title">
                    <h3>Even/Odd Distribution</h3>
                    <span class="help-icon">?
                        <span class="tooltip">Control the balance between even and odd numbers. Set minimum and maximum number of even numbers to include.</span>
                    </span>
                </div>
                <label>Min Even:</label>
                <input type="number" id="minEven" value="2" min="0" max="6"><br><br>
                <label>Max Even:</label>
                <input type="number" id="maxEven" value="4" min="0" max="6">
                <div class="filter-buttons">
                    <button class="btn-run" onclick="runFilter('even_odd')">Run</button>
                    <button class="btn-skip" onclick="skipFilter('even_odd')">Skip</button>
                </div>
            </div>
            <div class="filter-result" id="even_odd-result">
                <span class="status">Waiting...</span>
            </div>
        </div>

        <div class="filter">
            <div class="filter-controls">
                <div class="filter-title">
                    <h3>Random Number Sets</h3>
                    <span class="help-icon">?
                        <span class="tooltip">Generate random sets from your filtered combinations. Enter how many sets you want to generate.</span>
                    </span>
                </div>
                <label>Number of Sets:</label>
                <input type="number" id="numSets" value="5" min="1">
                <div class="filter-buttons">
                    <button class="btn-run" onclick="runFilter('random')">Generate Random Sets</button>
                </div>
            </div>
            <div class="filter-result" id="random-result">
                <span class="status">Waiting...</span>
            </div>
        </div>

        <script>
            let currentCombinations = [];
            let totalNumbers = 11;
            const filterOrder = ['include', 'exclude', 'sum', 'consecutive', 'even_odd', 'random'];
            let currentFilterIndex = 0;
            
            window.onload = function() {
                disableAllFilters();
            }
            
            function createNumberGrid(gridId) {
                const grid = document.getElementById(gridId);
                grid.innerHTML = '';
                const total = parseInt(document.getElementById('total').value);
                
                for (let i = 1; i <= total; i++) {
                    const btn = document.createElement('button');
                    btn.className = 'number-btn';
                    btn.textContent = i;
                    btn.onclick = function() {
                        this.classList.toggle('selected');
                    };
                    grid.appendChild(btn);
                }
            }

            function disableAllFilters() {
                filterOrder.forEach(filter => {
                    const buttons = document.querySelectorAll(`button[onclick*="${filter}"]`);
                    buttons.forEach(btn => {
                        btn.disabled = true;
                        btn.classList.add('disabled');
                    });
                });
            }
            
            function getSelectedNumbers(gridId) {
                const buttons = document.querySelectorAll(`#${gridId} .number-btn.selected`);
                const numbers = Array.from(buttons).map(btn => parseInt(btn.textContent));
                console.log(`Selected numbers from ${gridId}:`, numbers);
                return numbers;
            }

            function calculate() {
                const total = parseInt(document.getElementById('total').value);
                const choose = parseInt(document.getElementById('choose').value);
                totalNumbers = total;
                
                createNumberGrid('includeGrid');
                createNumberGrid('excludeGrid');
                
                fetch('/calc', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({total: total, choose: choose})
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert(data.error);
                        return;
                    }
                    currentCombinations = data.combinations;
                    updateFilterResult('initial', data.total, data.combinations);
                    enableNextFilter(0);
                });
            }

            function runIncludeFilter() {
                console.log('Running include filter...');
                const selectedNumbers = getSelectedNumbers('includeGrid');
                console.log('Selected numbers:', selectedNumbers);
                
                const data = {
                    combinations: currentCombinations,
                    filterType: 'include',
                    mustInclude: selectedNumbers
                };
                
                fetch('/filter', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Filter response:', data);
                    if (data.error) {
                        console.error('Filter error:', data.error);
                        updateStatus('include', 'Error: ' + data.error);
                        return;
                    }
                    currentCombinations = data.combinations;
                    updateFilterResult('include', data.total, data.combinations);
                    updateStatus('include', 'Done');
                    moveToNextFilter('include');
                })
                .catch(error => {
                    console.error('Filter request error:', error);
                    updateStatus('include', 'Error');
                });
            }

            function skipIncludeFilter() {
                console.log('Skipping include filter...');
                updateStatus('include', 'Skipped');
                moveToNextFilter('include');
            }

            function runFilter(filterType) {
                if (filterType === 'include') {
                    runIncludeFilter();
                    return;
                }
                
                updateStatus(filterType, 'Running...');
                let data = {
                    combinations: currentCombinations,
                    filterType: filterType
                };

                if (filterType === 'exclude') {
                    data.mustExclude = getSelectedNumbers('excludeGrid');
                } else if (filterType === 'sum') {
                    data.minSum = parseInt(document.getElementById('minSum').value);
                    data.maxSum = parseInt(document.getElementById('maxSum').value);
                } else if (filterType === 'consecutive') {
                    data.maxConsecutive = parseInt(document.getElementById('maxConsecutive').value);
                } else if (filterType === 'even_odd') {
                    data.minEven = parseInt(document.getElementById('minEven').value);
                    data.maxEven = parseInt(document.getElementById('maxEven').value);
                } else if (filterType === 'random') {
                    data.numSets = parseInt(document.getElementById('numSets').value);
                }
                
                console.log('Sending filter request:', data);
                
                fetch('/filter', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Filter response:', data);
                    if (data.error) {
                        console.error('Filter error:', data.error);
                        updateStatus(filterType, 'Error: ' + data.error);
                        return;
                    }
                    currentCombinations = data.combinations;
                    updateFilterResult(filterType, data.total, data.combinations);
                    updateStatus(filterType, 'Done');
                    if (filterType !== 'random') {
                        moveToNextFilter(filterType);
                    }
                })
                .catch(error => {
                    console.error('Filter request error:', error);
                    updateStatus(filterType, 'Error');
                });
            }

            function skipFilter(filterType) {
                updateStatus(filterType, 'Skipped');
                moveToNextFilter(filterType);
            }

            function updateStatus(filterType, status) {
                const resultDiv = document.getElementById(`${filterType}-result`);
                const statusSpan = resultDiv.querySelector('.status');
                statusSpan.textContent = status;
            }

            function updateFilterResult(filterType, total, combinations) {
                const resultDiv = document.getElementById(`${filterType}-result`);
                let html = `<span class="status">Done</span>`;
                html += `<p>Matching: ${total}</p>`;
                html += '<div style="max-height: 300px; overflow-y: auto;">';
                combinations.forEach(combo => {
                    const sum = combo.reduce((a, b) => a + b, 0);
                    const evens = combo.filter(n => n % 2 === 0).length;
                    const odds = combo.length - evens;
                    const low = combo.filter(n => n >= 1 && n <= 5).length;
                    const high = combo.filter(n => n >= 6 && n <= 11).length;
                    
                    html += `<div class="combo">
                        ${combo.join(', ')}
                        <div class="stats">
                            Sum: ${sum} | Even: ${evens}, Odd: ${odds} | Low: ${low}, High: ${high}
                        </div>
                    </div>`;
                });
                html += '</div>';
                resultDiv.innerHTML = html;
            }

            function enableNextFilter(currentIndex) {
                if (currentIndex < filterOrder.length - 1) {
                    const nextFilter = filterOrder[currentIndex + 1];
                    const buttons = document.querySelectorAll(`button[onclick*="${nextFilter}"]`);
                    buttons.forEach(btn => {
                        btn.disabled = false;
                        btn.classList.remove('disabled');
                    });
                }
            }

            function moveToNextFilter(currentFilter) {
                const currentIndex = filterOrder.indexOf(currentFilter);
                if (currentIndex < filterOrder.length - 1) {
                    enableNextFilter(currentIndex);
                }
            }
        </script>
    </body>
    </html>
    """

@app.route('/calc', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        total = int(data['total'])
        choose = int(data['choose'])
        
        if total < choose:
            return jsonify({
                'error': 'Total numbers must be greater than numbers to choose',
                'total': 0,
                'combinations': []
            })
        
        nums = list(range(1, total + 1))
        all_combos = list(combinations(nums, choose))
        combos_list = [list(c) for c in all_combos]
        
        return jsonify({
            'total': len(combos_list),
            'combinations': combos_list
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'total': 0,
            'combinations': []
        })

@app.route('/filter', methods=['POST'])
def apply_filter():
    try:
        data = request.get_json()
        combos = data['combinations']
        filter_type = data['filterType']
        
        if filter_type == 'include':
            must_include = data.get('mustInclude', [])
            # Convert string numbers to integers if needed
            must_include = [int(x) if isinstance(x, str) else x for x in must_include]
            print(f"Processing include filter with numbers: {must_include}")
            print(f"Initial combinations count: {len(combos)}")
            
            filtered = apply_include_filter(combos, must_include)
            
            print(f"Filtered combinations count: {len(filtered)}")
            if filtered:
                print(f"First filtered combination: {filtered[0]}")
                print(f"Does it contain all numbers? {all(num in filtered[0] for num in must_include)}")
            
            return jsonify({
                'filterName': f"Must Include Filter ({', '.join(map(str, must_include))})",
                'total': len(filtered),
                'combinations': filtered
            })
            
        elif filter_type == 'exclude':
            must_exclude = data['mustExclude']
            filtered = [combo for combo in combos if not any(num in combo for num in must_exclude)]
            return jsonify({
                'filterName': f"Must Exclude Filter ({', '.join(map(str, must_exclude))})",
                'total': len(filtered),
                'combinations': filtered
            })
            
        elif filter_type == 'sum':
            min_sum = int(data['minSum'])
            max_sum = int(data['maxSum'])
            filtered = [combo for combo in combos if apply_sum_filter(combo, min_sum, max_sum)]
            return jsonify({
                'filterName': f"Sum Filter ({min_sum}-{max_sum})",
                'total': len(filtered),
                'combinations': filtered
            })
            
        elif filter_type == 'consecutive':
            max_consecutive = int(data['maxConsecutive'])
            filtered = [combo for combo in combos if apply_consecutive_filter(combo, max_consecutive)]
            return jsonify({
                'filterName': f"Consecutive Filter (max {max_consecutive})",
                'total': len(filtered),
                'combinations': filtered
            })
            
        elif filter_type == 'even_odd':
            min_even = int(data['minEven'])
            max_even = int(data['maxEven'])
            filtered = [combo for combo in combos if apply_even_odd_filter(combo, min_even, max_even)]
            return jsonify({
                'filterName': f"Even/Odd Filter ({min_even}-{max_even} evens)",
                'total': len(filtered),
                'combinations': filtered
            })
            
        elif filter_type == 'random':
            num_sets = int(data['numSets'])
            filtered = random_combinations(combos, num_sets)
            return jsonify({
                'filterName': f"Random Sets (selected {num_sets})",
                'total': len(filtered),
                'combinations': filtered
            })
            
    except Exception as e:
        return jsonify({
            'error': str(e),
            'total': 0,
            'combinations': []
        })

if __name__ == '__main__':
    app.run(debug=True, port=5001)
