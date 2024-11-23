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
        parser.render_tree("static/parse_tree")  # Guarda el árbol en static/parse_tree.png

        # Agregar conteo de tokens
        token_counts = {
            'enteros': sum(1 for token in parser.lexical_tokens if token['type'] == 'entero'),
            'decimales': sum(1 for token in parser.lexical_tokens if token['type'] == 'decimal'),
            'operadores': sum(1 for token in parser.lexical_tokens if 'operador' in token['type']),
            'paréntesis apertura': sum(1 for token in parser.lexical_tokens if token['type'] == 'paréntesis apertura'),
            'paréntesis cierre': sum(1 for token in parser.lexical_tokens if token['type'] == 'paréntesis cierre'),
        }

        return jsonify({
            'message': 'Expresión válida',
            'result': expression,
            'tokens': parser.lexical_tokens,
            'token_counts': token_counts,
            'tree_image': '/static/parse_tree.png'
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
