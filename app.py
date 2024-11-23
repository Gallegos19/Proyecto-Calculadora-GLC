from flask import Flask, request, render_template, jsonify
from calculadora import CalculatorParser

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/validate_expression', methods=['POST'])
def validate_expression():
    data = request.get_json()  # Recibir el JSON del cliente
    expression = data.get('expression')

    if not expression:
        return jsonify({'error': 'No se proporcionó ninguna expresión'}), 400

    try:
        parser = CalculatorParser(expression)
        parser.parse()
        tokens = parser.analyze_lexically()  # Generar tokens léxicos

        parser.render_tree("static/parse_tree")  # Guarda el árbol en static/parse_tree.png
        return jsonify({
            'message': 'Expresión válida',
            'result': expression,
            'tree_image': '/static/parse_tree.png',
            'tokens': tokens  # Devuelve los tokens generados

            
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
