import sys
import os
import time
import mysql.connector
from datetime import datetime
from termcolor import colored
from dotenv import load_dotenv

load_dotenv()

def init_db():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conn.cursor()

    # make tokenizerLog table which will have details on the input file, timestamp, code length, status, etc.
    # honestly status could be a bool - should change
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TokenizerLog (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            timestamp DATETIME,
            length_of_code INT,
            status VARCHAR(50),
            total_tokens INT,
            lines_processed INT,
            error_message TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tokens (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tokenizer_log_id INT,
            token_type VARCHAR(50),
            lexeme VARCHAR(255),
            literal TEXT,
            line INT,
            FOREIGN KEY (tokenizer_log_id) REFERENCES TokenizerLog(id)
        )
    ''')
    conn.commit()
    conn.close()

# file data in
def log_tokenizer_entry(name, length_of_code, status, total_tokens=0, lines_processed=0, error_message=None):
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO TokenizerLog (name, timestamp, length_of_code, status, total_tokens, lines_processed, error_message)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), length_of_code, status, total_tokens, lines_processed, error_message))
    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id

# tokens deets in
def log_tokens(log_id, tokens):
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conn.cursor()
    for token in tokens:
        cursor.execute('''
            INSERT INTO Tokens (tokenizer_log_id, token_type, lexeme, literal, line)
            VALUES (%s, %s, %s, %s, %s)
        ''', (log_id, token.type, token.lexeme, str(token.literal), token.line))
    conn.commit()
    conn.close()

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

def main():
    init_db()
    
    if len(sys.argv) < 3:
        print("Usage: python3 main.py <command> <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    with open(filename) as file:
        file_contents = file.read()

    scanner = Scanner(file_contents)
    tokens = scanner.scan_tokens()

    visualizer = Visualizer(file_contents, tokens)
    visualizer.display_tokens()

if __name__ == "__main__":
    main()
