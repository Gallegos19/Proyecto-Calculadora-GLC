import re
from graphviz import Digraph

class CalculatorParser:
    def __init__(self, expression):
        self.tokens = re.findall(r'\d+|\+|\-|\*|\/|\(|\)|\.', expression)
        self.current_token_index = 0
        self.dot = Digraph()
        self.node_count = 0

    def get_current_token(self):
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
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
                raise ValueError("Error: Paréntesis desbalanceados")
        child = self.parse_D()
        self.add_edge(node, child)
        return node

    def parse_D(self):
        node = self.create_node('D')
        child = self.parse_E()
        self.add_edge(node, child)
        while self.get_current_token() == '.':
            dot_node = self.create_node('.')
            self.add_edge(node, dot_node)
            self.consume_token()
            next_child = self.parse_E()
            self.add_edge(node, next_child)
        return node

    def parse_E(self):
        node = self.create_node('E')
        token = self.get_current_token()
        if token and re.match(r'\d+', token):
            self.consume_token()
            token_node = self.create_node(token)
            self.add_edge(node, token_node)
            return node
        raise ValueError(f"Error: Se esperaba un número, pero se encontró '{token}'")

    def parse(self):
        root = self.parse_S()
        if self.get_current_token() is not None:
            raise ValueError("Error: Entrada no válida después del final de la expresión")
        return root

    def render_tree(self, output_filename="static/parse_tree"):
        self.dot.render(output_filename, format="png", cleanup=True)
