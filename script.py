import re



c = re.compile(r"(?i)SELECT (?P<fields>.+) FROM (?P<table>.+)")


def do_something(name:str) -> None:
    print(f"Hello {name}")

def parse_input(sql_data:str):
    data = c.match(sql_data)
    print(data["fields"])
    print(data["table"])

