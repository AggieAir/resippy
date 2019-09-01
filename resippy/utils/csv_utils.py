import csv


def read_csv_with_header(csv_fname,         # type: str
                         delimiter=',',     # type: str
                         ):                 # type: (...) -> tuple
    with open(csv_fname) as f:
        reader = csv.reader(f, delimiter=delimiter)
        csv_data = [r for r in reader]
        header = csv_data[0]
        csv_data.pop(0) # remove header
    return header, csv_data
