import re


def clean_sql(sql_str: str, regex: re = r'[\n\r\t\s]+', repl: str = ' ') -> str:
    return re.sub(regex, repl, sql_str).strip()

