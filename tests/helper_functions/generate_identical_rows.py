import copy

def generate_identical_rows(single_row_data, num_rows=10):
    return [copy.deepcopy(single_row_data) for _ in range(num_rows)]
