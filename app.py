from flask import Flask, render_template, request, jsonify, session
import csv
import re
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a secure secret key

# CSV Configuration
csv_file = "converted_file.csv"
header_row = True
header_col = True
prompt_cells = {f"B{i}" for i in range(2, 32)} | {f"K{i}" for i in range(2, 16)}

# Ingredient labels
LABELS = {
    "B2": "Maize", "B3": "Jowar", "B4": "B.Rice", "B5": "Wheat", "B6": "Bajra", "B7": "Ragi",
    "B8": "R.Polish", "B9": "DORB", "B10": "SFOC", "B11": "DOGN", "B12": "SOYA", "B13": "Fish Meal",
    "B14": "RSM", "B15": "LSP", "B16": "SG", "B17": "Mustard Meal", "B18": "DCP", "B19": "MOLASES",
    "B20": "MEAT AND BONE Meal", "B21": "Oil", "B22": "MGM", "B23": "Methionine", "B24": "Lysine",
    "B25": "Betaine", "B26": "Cocktail Enzyme", "B27": "Phytase", "B28": "SodaBicarb", "B29": "Salt",
    "B30": "TM MIX", "B31": "Rice DDGS",
    "K2": "Premix", "K3": "Bcomplex", "K4": "Toxin Binder", "K5": "Liver", "K6": "Dicerol",
    "K7": "Choline", "K8": "Osconite", "K9": "Anti Coccidial", "K10": "Probiotic", "K11": "Biotin 2%",
    "K12": "Vit E 50%", "K13": "AGP", "K14": "Acidifier", "K15": "Emulsifier"
}

# Load CSV data
try:
    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        sheet = list(reader)
except FileNotFoundError:
    sheet = []
    print("Error: converted_file.csv not found")

# Helper Functions
def parse_cell_ref(cell_ref):
    col_letters = ''.join(filter(str.isalpha, cell_ref)).upper()
    row_number_1based = int(''.join(filter(str.isdigit, cell_ref)))
    col_index_0based = 0
    for ch in col_letters:
        col_index_0based = col_index_0based * 26 + (ord(ch) - ord('A') + 1)
    col_index_0based -= 1
    return row_number_1based, col_index_0based, col_letters

def excel_to_csv_indices(row_number_1based, col_index_0based):
    csv_row = row_number_1based if header_row else (row_number_1based - 1)
    csv_col = (col_index_0based + 1) if header_col else col_index_0based
    return csv_row, csv_col

def parse_number(s):
    if s is None:
        return None
    s = str(s).strip()
    if s == "":
        return None
    s2 = s.replace(",", "")
    m = re.search(r"-?\d+(?:\.\d+)?", s2)
    if m:
        return float(m.group())
    return None

def get_cell_value(cell, computed_cache):
    if cell in computed_cache:
        return computed_cache[cell]
    
    if cell == "H20":
        computed_cache[cell] = 0.0
        return 0.0
    if cell == "H21":
        computed_cache[cell] = 3000.0
        return 3000.0
    
    row1b, col0b, _ = parse_cell_ref(cell)
    csv_r, csv_c = excel_to_csv_indices(row1b, col0b)
    
    try:
        raw = sheet[csv_r][csv_c]
        num = parse_number(raw)
        if num is not None:
            computed_cache[cell] = num
            return num
    except IndexError:
        pass
    
    computed_cache[cell] = 0.0
    return 0.0

def sum_range(start_cell, end_cell, computed_cache):
    start_row, start_col, col_letters = parse_cell_ref(start_cell)
    end_row, _, _ = parse_cell_ref(end_cell)
    total = 0
    for r in range(start_row, end_row + 1):
        total += get_cell_value(f"{col_letters}{r}", computed_cache)
    return total

def sumproduct(range1_start, range1_end, range2_start, range2_end, computed_cache):
    start_row1, start_col1, col_letters1 = parse_cell_ref(range1_start)
    end_row1, _, _ = parse_cell_ref(range1_end)
    start_row2, start_col2, col_letters2 = parse_cell_ref(range2_start)
    total = 0
    for i in range(end_row1 - start_row1 + 1):
        total += get_cell_value(f"{col_letters1}{start_row1 + i}", computed_cache) * get_cell_value(f"{col_letters2}{start_row2 + i}", computed_cache)
    return total

# Calculation Functions
class Calculator:
    def __init__(self, ingredient_list):
        self.ingredient_list = ingredient_list
        self.computed_cache = {}
        for cell in prompt_cells:
            self.computed_cache[cell] = ingredient_list.get(cell, {}).get('quantity', 0.0)
    
    def calc_F1(self):
        val = sum_range("B2", "B41", self.computed_cache)
        self.computed_cache["F1"] = val
        return val
    
    def calc_C83(self):
        val = sumproduct("B2", "B41", "C43", "C82", self.computed_cache)
        self.computed_cache["C83"] = val
        return val
    
    def calc_F83(self):
        val = sumproduct("B2", "B41", "F43", "F82", self.computed_cache)
        self.computed_cache["F83"] = val
        return val
    
    def calc_D83(self):
        val = sumproduct("B2", "B41", "D43", "D82", self.computed_cache)
        self.computed_cache["D83"] = val
        return val
    
    def calc_J83(self):
        val = sumproduct("B2", "B41", "J43", "J82", self.computed_cache)
        self.computed_cache["J83"] = val
        return val
    
    def calc_K83(self):
        val = sumproduct("B2", "B41", "K43", "K82", self.computed_cache)
        self.computed_cache["K83"] = val
        return val
    
    def calc_L83(self):
        val = sumproduct("B2", "B41", "L43", "L82", self.computed_cache)
        self.computed_cache["L83"] = val
        return val
    
    def calc_M83(self):
        val = sumproduct("B2", "B41", "M43", "M82", self.computed_cache)
        self.computed_cache["M83"] = val
        return val
    
    def calc_G83(self):
        val = sumproduct("B2", "B41", "G43", "G82", self.computed_cache)
        self.computed_cache["G83"] = val
        return val
    
    def calc_H83(self):
        val = sumproduct("B2", "B41", "H43", "H82", self.computed_cache)
        self.computed_cache["H83"] = val
        return val
    
    def calc_I83(self):
        val = sumproduct("B2", "B41", "I43", "I82", self.computed_cache)
        self.computed_cache["I83"] = val
        return val
    
    def calc_W83(self):
        val = sumproduct("B2", "B41", "W43", "W82", self.computed_cache)
        self.computed_cache["W83"] = val
        return val
    
    def calc_X83(self):
        val = sumproduct("B2", "B41", "X43", "X82", self.computed_cache)
        self.computed_cache["X83"] = val
        return val
    
    def calc_Y83(self):
        val = sumproduct("B2", "B41", "Y43", "Y82", self.computed_cache)
        self.computed_cache["Y83"] = val
        return val
    
    def calc_Z83(self):
        val = sumproduct("B2", "B41", "Z43", "Z82", self.computed_cache)
        self.computed_cache["Z83"] = val
        return val
    
    def calc_AA83(self):
        val = sumproduct("B2", "B41", "AA43", "AA82", self.computed_cache)
        self.computed_cache["AA83"] = val
        return val
    
    def calc_AB83(self):
        val = sumproduct("B2", "B41", "AB43", "AB82", self.computed_cache)
        self.computed_cache["AB83"] = val
        return val
    
    def calc_AC83(self):
        val = sumproduct("B2", "B41", "AC43", "AC82", self.computed_cache)
        self.computed_cache["AC83"] = val
        return val
    
    def calc_AD83(self):
        val = sumproduct("B2", "B41", "AD43", "AD82", self.computed_cache)
        self.computed_cache["AD83"] = val
        return val
    
    def calc_AE83(self):
        val = sumproduct("B2", "B41", "AE43", "AE82", self.computed_cache)
        self.computed_cache["AE83"] = val
        return val
    
    def calc_AF83(self):
        val = sumproduct("B2", "B41", "AF43", "AF82", self.computed_cache)
        self.computed_cache["AF83"] = val
        return val
    
    def calc_N83(self):
        val = sumproduct("B2", "B41", "N43", "N82", self.computed_cache)
        self.computed_cache["N83"] = val
        return val
    
    def calc_O83(self):
        val = sumproduct("B2", "B41", "O43", "O82", self.computed_cache)
        self.computed_cache["O83"] = val
        return val
    
    def calc_P83(self):
        val = sumproduct("B2", "B41", "P43", "P82", self.computed_cache)
        self.computed_cache["P83"] = val
        return val
    
    def calc_Q83(self):
        val = sumproduct("B2", "B41", "Q43", "Q82", self.computed_cache)
        self.computed_cache["Q83"] = val
        return val
    
    def calc_R83(self):
        val = sumproduct("B2", "B41", "R43", "R82", self.computed_cache)
        self.computed_cache["R83"] = val
        return val
    
    def calc_S83(self):
        val = sumproduct("B2", "B41", "S43", "S82", self.computed_cache)
        self.computed_cache["S83"] = val
        return val
    
    def calc_T83(self):
        val = sumproduct("B2", "B41", "T43", "T82", self.computed_cache)
        self.computed_cache["T83"] = val
        return val
    
    def calc_U83(self):
        val = sumproduct("B2", "B41", "U43", "U82", self.computed_cache)
        self.computed_cache["U83"] = val
        return val
    
    def calc_V83(self):
        val = sumproduct("B2", "B41", "V43", "V82", self.computed_cache)
        self.computed_cache["V83"] = val
        return val
    
    def calc_AS83(self):
        val = sumproduct("B2", "B41", "AS43", "AS82", self.computed_cache)
        self.computed_cache["AS83"] = val
        return val
    
    def calc_E83(self):
        val = sumproduct("B2", "B41", "E43", "E82", self.computed_cache)
        self.computed_cache["E83"] = val
        return val
    
    def calc_F2(self):
        return self.calc_C83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F3(self):
        return self.calc_F83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F4(self):
        return (self.calc_F3() / self.calc_F2() * 1000) if self.calc_F2() != 0 else 0.0
    
    def calc_F5(self):
        return self.calc_D83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F6(self):
        return self.calc_J83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F7(self):
        return self.calc_K83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F8(self):
        return self.calc_L83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F9(self):
        return self.calc_F7() + self.calc_F8()
    
    def calc_F10(self):
        return self.calc_M83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F11(self):
        return self.calc_G83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F12(self):
        return self.calc_H83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F13(self):
        return self.calc_I83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F24(self):
        return self.calc_W83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F25(self):
        return self.calc_X83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F26(self):
        return self.calc_Y83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F27(self):
        return self.calc_Z83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F28(self):
        return self.calc_AA83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F29(self):
        return self.calc_AB83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F30(self):
        return self.calc_AC83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F31(self):
        return self.calc_AD83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F32(self):
        return self.calc_AE83() / 1000
    
    def calc_F33(self):
        return self.calc_AF83() / 1000
    
    def calc_F17(self):
        return self.calc_F24() / 10
    
    def calc_F18(self):
        return self.calc_F25() / 10
    
    def calc_F16(self):
        return self.calc_F26() / self.calc_F25() if self.calc_F25() != 0 else 0.0
    
    def calc_F15(self):
        return self.calc_F17() / self.calc_F18() if self.calc_F18() != 0 else 0.0
    
    def calc_F19(self):
        return self.calc_F26() / 10
    
    def calc_F14(self):
        return (self.calc_F25() / 23 + self.calc_F26() / 39 - self.calc_F24() / 35) * 100
    
    def calc_F20(self):
        for cell in self.ingredient_list:
            if self.ingredient_list[cell].get('cost', 0) <= 0:
                return "NA"
        
        total_cost = 0
        for cell, data in self.ingredient_list.items():
            total_cost += data['quantity'] * data['cost']
        
        total_quantity = self.calc_F1()
        if total_quantity == 0:
            return "NA"
        
        return total_cost / total_quantity
    
    def calc_F21(self):
        cost_per_kg = self.calc_F20()
        if cost_per_kg == "NA":
            return "NA"
        return cost_per_kg * 75
    
    def calc_F22(self):
        cost_per_bag = self.calc_F21()
        if cost_per_bag == "NA":
            return "NA"
        return get_cell_value("H21", self.computed_cache) - cost_per_bag
    
    def calc_F34(self):
        user_quantity_k2 = self.ingredient_list.get("K2", {}).get('quantity', 0)
        return user_quantity_k2 * 82500 / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F35(self):
        user_quantity_k3 = self.ingredient_list.get("K3", {}).get('quantity', 0)
        user_quantity_k12 = self.ingredient_list.get("K12", {}).get('quantity', 0)
        return (user_quantity_k3 * 40 + user_quantity_k12 * 0.5 * 1000) / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F36(self):
        user_quantity_k2 = self.ingredient_list.get("K2", {}).get('quantity', 0)
        return user_quantity_k2 * 10 / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F37(self):
        user_quantity_k11 = self.ingredient_list.get("K11", {}).get('quantity', 0)
        return user_quantity_k11 * 0.02 * 1000 * 1000 / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F38(self):
        user_quantity_k7 = self.ingredient_list.get("K7", {}).get('quantity', 0)
        return user_quantity_k7 * 0.6
    
    def calc_F39(self):
        user_quantity_k3 = self.ingredient_list.get("K3", {}).get('quantity', 0)
        return user_quantity_k3 * 3 / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F40(self):
        user_quantity_k3 = self.ingredient_list.get("K3", {}).get('quantity', 0)
        return user_quantity_k3 * 60 / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_F41(self):
        user_quantity_k3 = self.ingredient_list.get("K3", {}).get('quantity', 0)
        return user_quantity_k3 * 40 / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_H24(self):
        return self.calc_N83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_H25(self):
        return self.calc_O83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_H26(self):
        return self.calc_P83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_H27(self):
        return self.calc_Q83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_H28(self):
        return self.calc_R83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_H29(self):
        return self.calc_S83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_H30(self):
        return self.calc_T83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_H31(self):
        return self.calc_U83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_H32(self):
        return self.calc_V83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_H33(self):
        return self.calc_AS83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_H34(self):
        return self.calc_E83() / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_H35(self):
        user_quantity_k3 = self.ingredient_list.get("K3", {}).get('quantity', 0)
        return user_quantity_k3 * 8 / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_H36(self):
        user_quantity_k2 = self.ingredient_list.get("K2", {}).get('quantity', 0)
        return user_quantity_k2 * 50 / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_H37(self):
        user_quantity_k3 = self.ingredient_list.get("K3", {}).get('quantity', 0)
        return user_quantity_k3 * 4 / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_H38(self):
        user_quantity_k3 = self.ingredient_list.get("K3", {}).get('quantity', 0)
        return user_quantity_k3 * 40 / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calc_H39(self):
        user_quantity_k2 = self.ingredient_list.get("K2", {}).get('quantity', 0)
        user_quantity_k6 = self.ingredient_list.get("K6", {}).get('quantity', 0)
        return (user_quantity_k2 * 12000 + user_quantity_k6 * 600000) / self.calc_F1() if self.calc_F1() != 0 else 0.0
    
    def calculate_all(self):
        results = {
            "Total Quantity": self.calc_F1(),
            "Crude Protein (%)": self.calc_F2(),
            "ME (Mcal/Kg)": self.calc_F3(),
            "Calorie:Protein Ratio": self.calc_F4(),
            "Crude Fibre (%)": self.calc_F5(),
            "Lysine (%)": self.calc_F6(),
            "Methionine (%)": self.calc_F7(),
            "Cystine (%)": self.calc_F8(),
            "MET+CYS (%)": self.calc_F9(),
            "Arginine (%)": self.calc_F10(),
            "Calcium (%)": self.calc_F11(),
            "Total Phosphorus (%)": self.calc_F12(),
            "Available Phosphorus (%)": self.calc_F13(),
            "Na+K-Cl (mEq/kg)": self.calc_F14(),
            "Na:Cl Ratio": self.calc_F15(),
            "Na:K Ratio": self.calc_F16(),
            "Chloride (%)": self.calc_F17(),
            "Sodium (%)": self.calc_F18(),
            "Potassium (%)": self.calc_F19(),
            "Cost per kg": self.calc_F20(),
            # "Cost per Bag": self.calc_F21(),
            "Margin": self.calc_F22(),
            "Chloride (mg/kg)": self.calc_F24(),
            "Sodium (mg/kg)": self.calc_F25(),
            "Potassium (mg/kg)": self.calc_F26(),
            "Manganese (mg/kg)": self.calc_F27(),
            "Zinc (mg/kg)": self.calc_F28(),
            "Selenium (mg/kg)": self.calc_F29(),
            "Iron (mg/kg)": self.calc_F30(),
            "Copper (mg/kg)": self.calc_F31(),
            "Cobalt (mg/kg)": self.calc_F32(),
            "Iodine (mg/kg)": self.calc_F33(),
            "Vitamin A (IU/kg)": self.calc_F34(),
            "Vitamin E (IU/kg)": self.calc_F35(),
            "Vitamin K (mg/kg)": self.calc_F36(),
            "Biotin (mcg/kg)": self.calc_F37(),
            "Choline (mg/kg)": self.calc_F38(),
            "Folicacid": self.calc_F39(),
            "Niacin": self.calc_F40(),
            "Panthothenicacid": self.calc_F41(),
            "Histidine": self.calc_H24(),
            "Leucine": self.calc_H25(),
            "Isoleucine": self.calc_H26(),
            "P.Alanine": self.calc_H27(),
            "Threonine": self.calc_H28(),
            "Tryoptophan": self.calc_H29(),
            "Tyrosine": self.calc_H30(),
            "Valine": self.calc_H31(),
            "Serine": self.calc_H32(),
            "Linoleicacid": self.calc_H33(),
            "AFT": self.calc_H34(),
            "B6": self.calc_H35(),
            "B2": self.calc_H36(),
            "B1": self.calc_H37(),
            "B12": self.calc_H38(),
            "D3": self.calc_H39()
        }
        return results

# Routes
@app.route('/')
def index():
    sorted_cells = sorted(prompt_cells)
    ingredients = [(cell, LABELS.get(cell, cell)) for cell in sorted_cells]
    return render_template('index.html', ingredients=ingredients)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    ingredient_list = data.get('ingredients', {})
    
    if not ingredient_list:
        return jsonify({'error': 'No ingredients provided'}), 400
    
    try:
        calculator = Calculator(ingredient_list)
        results = calculator.calculate_all()
        
        # Format results
        formatted_results = {}
        for key, value in results.items():
            if value == "NA":
                formatted_results[key] = "NA"
            else:
                formatted_results[key] = round(value, 4)
        
        return jsonify({'results': formatted_results})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear_session():
    session.clear()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)
