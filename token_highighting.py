import sys
import os
import time
from termcolor import colored

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

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token("EOF", "", None, self.line))
        return self.tokens

    def is_at_end(self):
        return self.current >= len(self.source)

    def scan_token(self):
        char = self.advance()
        if char == "=":
            self.add_token("EQUAL")
        elif char == "+":
            self.add_token("PLUS")
        elif char == "-":
            self.add_token("MINUS")
        elif char == ";":
            self.add_token("SEMICOLON")
        elif char == "(":
            self.add_token("LEFT_PAREN")
        elif char == ")":
            self.add_token("RIGHT_PAREN")
        elif char.isdigit():
            self.handle_number()
        elif char.isalpha() or char == "_":
            self.handle_identifier()

    def advance(self):
        self.current += 1
        return self.source[self.current - 1]

    def handle_number(self):
        while self.peek().isdigit():
            self.advance()
        value = int(self.source[self.start:self.current])
        self.add_token("NUMBER", value)

    def handle_identifier(self):
        while self.peek().isalnum() or self.peek() == "_":
            self.advance()
        value = self.source[self.start:self.current]
        token_type = KEYWORDS.get(value, "IDENTIFIER")
        self.add_token(token_type)

    def peek(self):
        return "\0" if self.is_at_end() else self.source[self.current]

    def add_token(self, type: str, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))

# token with highlighting!
class Visualizer:
    def __init__(self, source, tokens):
        self.source = source
        self.tokens = tokens

    def display_tokens(self):
        for idx, token in enumerate(self.tokens):
            os.system("clear" if os.name == "posix" else "cls")

            highlighted_code = self.highlight_token(idx)
            print("Input Code:\n" + highlighted_code)
            print(f"\nTokens Processed:")
            
            for processed_token in self.tokens[:idx + 1]:
                print(processed_token)
            time.sleep(2)

    def highlight_token(self, current_idx):
        result = []
        for idx, token in enumerate(self.tokens):
            token_text = token.lexeme
            if idx == current_idx:
                result.append(colored(token_text, "red", attrs=["bold"]))
            else:
                result.append(token_text)
        return self.source.replace(self.tokens[current_idx].lexeme, result[current_idx], 1)

# Main function
def main():
    if len(sys.argv) < 3:
        print("Usage: python3 main.py <command> <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    with open(filename) as file:
        file_contents = file.read()

    scanner = Scanner(file_contents)
    tokens = scanner.scan_tokens()

    if command == "tokenize":
        visualizer = Visualizer(file_contents, tokens)
        visualizer.display_tokens()

if __name__ == "__main__":
    main()
