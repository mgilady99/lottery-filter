from flask import Flask, render_template, jsonify, request
from itertools import combinations

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
    <body>
        <h2>Simple Lottery Calculator</h2>
        <p>
            Total Numbers: <input type="number" id="total" value="37"><br>
            Choose: <input type="number" id="choose" value="6"><br>
            <button onclick="calculate()">Calculate</button>
        </p>
        <div id="result"></div>

        <script>
            function calculate() {
                const total = document.getElementById('total').value;
                const choose = document.getElementById('choose').value;
                
                fetch('/calculate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({total: total, choose: choose})
                })
                .then(response => response.json())
                .then(data => {
                    let html = `<p>Total combinations: ${data.total}</p>`;
                    html += '<h3>First 5 combinations:</h3>';
                    data.combinations.forEach(combo => {
                        html += `<p>${combo.join(', ')}</p>`;
                    });
                    document.getElementById('result').innerHTML = html;
                });
            }
        </script>
    </body>
    </html>
    """

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    total = int(data['total'])
    choose = int(data['choose'])
    
    # Generate combinations
    nums = list(range(1, total + 1))
    all_combos = list(combinations(nums, choose))
    
    # Convert to list format
    all_combos = [list(c) for c in all_combos]
    
    return jsonify({
        'total': len(all_combos),
        'combinations': all_combos[:5]  # Just show first 5
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
