import sys

# Keywords mapping
KEYWORDS = {
    "and": "AND",
    "class": "CLASS",
    "else": "ELSE",
    "false": "FALSE",
    "for": "FOR",
    "fun": "FUN",
    "if": "IF",
    "nil": "NIL",
    "or": "OR",
    "print": "PRINT",
    "return": "RETURN",
    "super": "SUPER",
    "this": "THIS",
    "true": "TRUE",
    "var": "VAR",
    "while": "WHILE",
}

# Token class
class Token:
    def __init__(self, type: str, lexeme: str, literal, line: int):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        if self.type == "NUMBER":
            num = float(self.literal)
            literal_str = f"{num:.1f}" if num.is_integer() else str(num)
        else:
            literal_str = "null" if self.literal is None else str(self.literal)
        return f"{self.type} {self.lexeme} {literal_str}"

# Scanner class
class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.errors = []

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token("EOF", "", None, self.line))
        return self.tokens, self.errors

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def scan_token(self):
        char = self.advance()
        if char == "(":
            self.add_token("LEFT_PAREN")
        elif char == ")":
            self.add_token("RIGHT_PAREN")
        elif char == "{":
            self.add_token("LEFT_BRACE")
        elif char == "}":
            self.add_token("RIGHT_BRACE")
        elif char == ",":
            self.add_token("COMMA")
        elif char == ".":
            self.add_token("DOT")
        elif char == "-":
            self.add_token("MINUS")
        elif char == "+":
            self.add_token("PLUS")
        elif char == ";":
            self.add_token("SEMICOLON")
        elif char == "*":
            self.add_token("STAR")
        elif char == "=":
            self.add_token("EQUAL_EQUAL" if self.match("=") else "EQUAL")
        elif char == "!":
            self.add_token("BANG_EQUAL" if self.match("=") else "BANG")
        elif char == ">":
            self.add_token("GREATER_EQUAL" if self.match("=") else "GREATER")
        elif char == "<":
            self.add_token("LESS_EQUAL" if self.match("=") else "LESS")
        elif char == "/":
            self.handle_slash()
        elif char == '"':
            self.handle_string()
        elif char.isdigit():
            self.handle_number()
        elif char.isalpha() or char == "_":
            self.handle_identifier()
        elif char in " \r\t":  # Skip whitespace
            pass
        elif char == "\n":  # Handle newlines
            self.line += 1
        else:
            self.error(f"Unexpected character: {char}")

    def match(self, expected: str) -> bool:
        if self.is_at_end() or self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def handle_slash(self):
        if self.match("/"):  # Single-line comments
            while self.peek() != "\n" and not self.is_at_end():
                self.advance()
        else:
            self.add_token("SLASH")

    def handle_string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.is_at_end():
            self.error("Unterminated string.")
            return

        # Consume the closing quote
        self.advance()

        # Extract the string value, excluding the surrounding quotes
        value = self.source[self.start + 1: self.current - 1]
        self.add_token("STRING", value)

    def handle_number(self):
        while self.peek().isdigit():
            self.advance()
        
        # Check if it's a float
        if self.peek() == "." and self.peek_next().isdigit():
            self.advance()  # Consume the dot
            while self.peek().isdigit():
                self.advance()
            value = float(self.source[self.start:self.current])
        else:
            # It's an integer
            value = int(self.source[self.start:self.current])
            
        self.add_token("NUMBER", value)

    def handle_identifier(self):
        while self.peek().isalnum() or self.peek() == "_":
            self.advance()
        value = self.source[self.start:self.current]
        token_type = KEYWORDS.get(value, "IDENTIFIER")
        self.add_token(token_type)

    def advance(self) -> str:
        self.current += 1
        return self.source[self.current - 1]

    def peek(self) -> str:
        return "\0" if self.is_at_end() else self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def add_token(self, type: str, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))

    def error(self, message: str):
        self.errors.append(f"[line {self.line}] Error: {message}")

# Parser class
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.expression())
        return statements

    def expression(self):
        return self.equality()

    def equality(self):
        expr = self.comparison()
        while self.match("BANG_EQUAL", "EQUAL_EQUAL"):
            operator = self.previous()
            right = self.comparison()
            expr = f"({operator.lexeme} {expr} {right})"
        return expr

    def comparison(self):
        expr = self.term()
        while self.match("GREATER", "GREATER_EQUAL", "LESS", "LESS_EQUAL"):
            operator = self.previous()
            right = self.term()
            expr = f"({operator.lexeme} {expr} {right})"
        return expr

    def term(self):
        expr = self.factor()
        while self.match("PLUS", "MINUS"):
            operator = self.previous()
            right = self.factor()
            expr = f"({operator.lexeme} {expr} {right})"
        return expr

    def factor(self):
        expr = self.unary()
        while self.match("STAR", "SLASH"):
            operator = self.previous()
            right = self.unary()
            expr = f"({operator.lexeme} {expr} {right})"
        return expr

    def unary(self):
        if self.match("MINUS", "BANG"):
            operator = self.previous()
            right = self.unary()
            return f"({operator.lexeme} {right})"
        return self.primary()

    def primary(self):
        if self.match("NUMBER"):
            return f"{float(self.previous().literal):.1f}"
        elif self.match("STRING"):
            return self.previous().literal
        elif self.match("LEFT_PAREN"):
            expr = self.expression()
            self.consume("RIGHT_PAREN", "Expect ')' after expression.")
            return f"(group {expr})"
        self.error("Expected expression.")
        return None

    def match(self, *types):
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def check(self, token_type):
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().type == "EOF"

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def consume(self, token_type, message):
        if self.check(token_type):
            return self.advance()
        self.error(message)

    def error(self, message: str):
        print(f"Error: {message}")

# Main function
def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh <command> <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command not in ["tokenize", "parse"]:
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)

    with open(filename) as file:
        file_contents = file.read()

    scanner = Scanner(file_contents)
    tokens, errors = scanner.scan_tokens()

    if command == "tokenize":
        for token in tokens:
            print(token)
        for error in errors:
            print(error, file=sys.stderr)
    elif command == "parse":
        parser = Parser(tokens)
        ast = parser.parse()
        for node in ast:
            print(node)

    if errors:
        exit(65)  # Indicate failure

if __name__ == "__main__":
    main()
