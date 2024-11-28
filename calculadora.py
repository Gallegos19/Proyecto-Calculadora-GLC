import re
from graphviz import Digraph

class CalculatorParser:
    def __init__(self, expression):
        # Tokenizar la expresión (incluye decimales como un solo token)
        self.tokens = re.findall(r'\d+\.\d+|\d+|\+|\-|\*|\/|\(|\)', expression)
        self.current_token_index = 0
        self.dot = Digraph()
        self.node_count = 0
        self.lexical_tokens = []  # Almacena los tokens analizados léxicamente
        self.token_counts = {     # Almacena el conteo de cada tipo de token
            "enteros": 0,
            "decimales": 0,
            "operadores": 0,
            "paréntesis apertura": 0,
            "paréntesis cierre": 0,
            "desconocidos": 0
        }

    def get_current_token(self):
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return None

    def get_next_token(self):
        if self.current_token_index + 1 < len(self.tokens):
            return self.tokens[self.current_token_index + 1]
        return None

    def consume_token(self):
        self.current_token_index += 1

    def create_node(self, label):
        node_name = f"node{self.node_count}"
        self.dot.node(node_name, label)
        self.node_count += 1
        return node_name

    def add_edge(self, parent, child):
        self.dot.edge(parent, child)

    def validate_parentheses(self):
        """
        Valida si los paréntesis están correctamente balanceados.
        """
        stack = []
        for token in self.tokens:
            if token == '(':
                stack.append(token)
            elif token == ')':
                if not stack:
                    raise ValueError("Error: Paréntesis de cierre sin apertura")
                stack.pop()
        if stack:
            raise ValueError("Error: Paréntesis abiertos sin cerrar")

    def handle_implicit_multiplication(self):
        """
        Detecta multiplicaciones implícitas (ej. 2(3) o 4.5(6)) y ajusta los tokens.
        """
        new_tokens = []
        for i in range(len(self.tokens)):
            current_token = self.tokens[i]
            new_tokens.append(current_token)

            if i < len(self.tokens) - 1:
                next_token = self.tokens[i + 1]

                # Detectar patrones de multiplicación implícita
                if (re.match(r'\d+(\.\d+)?', current_token) or current_token == ')') and \
                   (re.match(r'\d+(\.\d+)?', next_token) or next_token == '('):
                    new_tokens.append('*')  # Insertar operador de multiplicación implícita
        self.tokens = new_tokens

    def classify_token(self, token):
        """
        Clasifica un token en base a su tipo: número entero, número decimal, operador, etc.
        """
        if re.match(r'^\d+\.\d+$', token):
            return 'decimal'
        elif re.match(r'^\d+$', token):
            return 'entero'
        elif token in ['+', '-', '*', '/']:
            return 'operador'
        elif token == '(':
            return 'paréntesis apertura'
        elif token == ')':
            return 'paréntesis cierre'
        else:
            return 'desconocido'

    def analyze_lexically(self):
        """
        Realiza el análisis léxico de los tokens y actualiza el conteo de cada tipo.
        """
        self.lexical_tokens = []  # Limpia los tokens léxicos
        self.token_counts = {  # Reinicia los conteos
            "enteros": 0,
            "decimales": 0,
            "operadores": 0,
            "paréntesis apertura": 0,
            "paréntesis cierre": 0,
            "desconocidos": 0
        }

        for token in self.tokens:
            token_type = self.classify_token(token)
            self.lexical_tokens.append({'token': token, 'type': token_type})

            # Actualiza el conteo según el tipo del token
            if token_type == 'entero':
                self.token_counts["enteros"] += 1
            elif token_type == 'decimal':
                self.token_counts["decimales"] += 1
            elif token_type == 'operador':
                self.token_counts["operadores"] += 1
            elif token_type == 'paréntesis apertura':
                self.token_counts["paréntesis apertura"] += 1
            elif token_type == 'paréntesis cierre':
                self.token_counts["paréntesis cierre"] += 1
            else:
                self.token_counts["desconocidos"] += 1

        return self.lexical_tokens

    def get_token_counts(self):
        """
        Retorna el conteo de cada tipo de token.
        """
        return self.token_counts

    def parse_S(self):
        node = self.create_node('S')
        child = self.parse_A()
        self.add_edge(node, child)
        return node

    def parse_A(self):
        node = self.create_node('A')
        left_child = self.parse_B()
        self.add_edge(node, left_child)
        while self.get_current_token() in ['+', '-']:
            operator = self.get_current_token()
            op_node = self.create_node(operator)
            self.add_edge(node, op_node)
            self.consume_token()
            right_child = self.parse_B()
            self.add_edge(node, right_child)
        return node

    def parse_B(self):
        node = self.create_node('B')
        left_child = self.parse_C()
        self.add_edge(node, left_child)
        while self.get_current_token() in ['*', '/']:
            operator = self.get_current_token()
            op_node = self.create_node(operator)
            self.add_edge(node, op_node)
            self.consume_token()
            right_child = self.parse_C()
            self.add_edge(node, right_child)
        return node

    def parse_C(self):
        node = self.create_node('C')
        token = self.get_current_token()
        if token == '(':
            self.consume_token()
            child = self.parse_A()
            self.add_edge(node, child)
            if self.get_current_token() == ')':
                self.consume_token()
                return node
            else:
                raise ValueError("Error: Paréntesis abiertos sin cerrar al final")
        child = self.parse_D()
        self.add_edge(node, child)
        return node

    def parse_D(self):
        node = self.create_node('D')
        token = self.get_current_token()
        if token and re.match(r'\d+(\.\d+)?', token):  # Reconocer números enteros y decimales
            self.consume_token()
            token_node = self.create_node(token)
            self.add_edge(node, token_node)
            return node
        raise ValueError(f"Error: Se esperaba un número, pero se encontró '{token}'")

    def parse(self):
        # Validar paréntesis antes de analizar
        self.validate_parentheses()

        # Manejar multiplicaciones implícitas
        self.handle_implicit_multiplication()

        # Realizar análisis léxico
        self.analyze_lexically()

        # Iniciar el análisis sintáctico
        root = self.parse_S()
        if self.get_current_token() is not None:
            raise ValueError("Error: Entrada no válida después del final de la expresión")
        return root
 
    def render_tree(self, output_filename="static/parse_tree"):
        self.dot.render(output_filename, format="png", cleanup=True)
