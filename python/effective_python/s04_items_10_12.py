from dataclasses import dataclass

def to_text(value):
    if isinstance(value, str):
        return value
    elif isinstance(value, bytes):
        return value.decode("utf-8")
    else:
        raise TypeError("Input must be a string or bytes.")
    

def to_bytes(value):
    if isinstance(value, bytes):
        return value
    elif isinstance(value, str):
        return value.encode("utf-8")
    else:
        raise TypeError("Input must be a string or bytes.")


# item 11: f-strings

def format_ingestion_summary(source, rows, error_rate):
    return f"Source: {source}, Rows: {rows:,}, Error Rate: {error_rate:.2%}"


# item 12: understand the difference between str and repr

@dataclass
class IngestionRun:
    source: str
    rows: int
    status: str

    def __str__(self):
        return f'{self.source}: {self.rows} rows - {self.status}'