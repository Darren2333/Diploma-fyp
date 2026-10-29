import re
from flask import Flask, render_template, request

app = Flask(__name__)

def clean_price(price_str):
    price_str = price_str.replace("Price:", "").replace("RM", "").strip()
    price_str = re.sub(r"[^0-9.]", "", price_str)  # Remove non-numeric characters
    try:
        return float(price_str.split(".", 1)[0] + "." + price_str.split(".", 1)[1])
    except ValueError:
        return 0.0  # Or handle the error differently

def read_data(files):
    grocery_data = []
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
            current_item = {}
            for line in lines:
                if line.startswith("Grocery Item:"):
                    if current_item:
                        grocery_data.append(current_item)
                    current_item = {}
                    current_item['name'] = line.replace("Grocery Item:", "").strip()
                elif line.startswith("Price:"):
                    current_item['price'] = clean_price(line)
                    current_item['source'] = file
            if current_item:
                grocery_data.append(current_item)

        source_map = {
        "lotusitems.txt": "Lotus",
        "aeonitems.txt": "Aeon",
        "coldstorageitems.txt": "Cold Storage"
    }
        
    for item in grocery_data:
        item['source'] = source_map.get(item['source'], item['source'])

    return grocery_data

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query'].lower()
    files = ['lotusitems.txt', 'aeonitems.txt', 'coldstorageitems.txt']
    grocery_data = read_data(files)

    results = [item for item in grocery_data if re.search(query, item['name'], re.IGNORECASE)]

    # Sort results by price in ascending order
    results.sort(key=lambda x: x['price'])

    if results:
        cheapest_item = results[0]  # The first item is now the cheapest
    else:
        cheapest_item = None

    return render_template('index.html', results=results, cheapest_item=cheapest_item)

if __name__ == '__main__':
    app.run(debug=True)