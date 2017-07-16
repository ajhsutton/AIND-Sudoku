import itertools
import copy

assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'

def cartesian_product(a, b):
    return [ai + bj for ai in a for bj in b]

boxes = cartesian_product(rows, cols)
row_units = [cartesian_product(r, cols) for r in rows]
col_units = [cartesian_product(rows, c) for c in cols]
minirows = ('ABC','DEF','GHI')
minicols = ('123','456','789')
square_units = [cartesian_product(mr, mc) for mr in minirows for mc in minicols ]
diag_unit_1 = [item[0] + item[1] for item in list(zip(rows, cols))]
diag_unit_2 = [item[0] + item[1] for item in list(zip(rows, list(reversed(cols))))]
all_units = row_units + col_units + square_units + [diag_unit_1, diag_unit_2]

peer_sets = {}
for b in boxes:
    peer_sets[b] = []

for unit in all_units:
    for box in unit:
        peer_sets[box].append(unit)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values        

def get_twins(values):
    '''Filter values to find candidates shared by 2 boxes within a common peer set.
       '''
    # Identify boxes with only 2 value options.
    twin_candidates = {box: values[box] for box in boxes if len(values[box]) == 2} 
    
     # List of Naked Twins
    naked_twins_list = []
    
    # For each candidate box "box_i", check if any peers are also twin candidates.
    for box_i in twin_candidates:
        for peer_unit in peer_sets[box_i]:
            for box_j in peer_unit:
                if box_j in twin_candidates and box_i != box_j and values[box_i] == values[box_j]:
                    # Valid naked twin pair found
                    naked_twins_list.append((box_i, box_j, values[box_i]))
    return naked_twins_list

def clear_twin_peers(box_i, box_j, val, puzzle):
    # Helper method for clearing "val" from only the common peers for boxes i & j
    units_i = peer_sets[box_i]
    for unit in units_i:
        if box_i in unit and box_j in unit:
            for target in unit:
                if target != box_i and target != box_j:
                    for v in val:
                        puzzle = assign_value(puzzle, target, puzzle[target].replace(v, ''))
    return puzzle

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    naked_twins_list = get_twins(values)

    # Valid naked Twins found, remove twin values from all peers
    for box_i, box_j, val in naked_twins_list:
        values = clear_twin_peers(box_i, box_j, val, values)
    return values
    
def cross(A, B):
    "Cross product of elements in A and elements in B."
    pass

def grid_values(encoded_puzzle):
    grid = {}
    for i in range(0, len(boxes)):
        val = encoded_puzzle[i]
        if val == '.':
            val = '123456789'
        grid[boxes[i]] = val
    return grid

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def clear_peers(box, val, puzzle):
    units = peer_sets[box]
    for unit in units:
        for target in unit:
            if target != box:
                puzzle[target] = puzzle[target].replace(val, '')
    return puzzle

def eliminate(puzzle_dict):
    fixed_dict = puzzle_dict
    for box, val in puzzle_dict.items():
        if len(val) == 1:
            fixed_dict = clear_peers(box, val, puzzle_dict)
    return fixed_dict

def only_choice(puzzle_dict):
    for unit in all_units:
        for digit in cols:
            place_count = [box for box in unit if digit in puzzle_dict[box]]
            if len(place_count) == 1:
                puzzle_dict[place_count[0]] = digit
    return puzzle_dict

def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values) # Naked Twins constraint added

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    # First, reduce the puzzle using the previous function
    reduced = reduce_puzzle(values)
    min_option_count = 10
    min_option_square = 'A1'
    for k, v in values.items():
        if len(v) < min_option_count and len(v) != 1:
            min_option_count = len(v)
            min_option_square = k

    if min_option_count <= 0:
        return False

    if min_option_count == 10:
        # solved
        return reduced

    for i in range(min_option_count):
        test_values = copy.deepcopy(values)
        test_values[min_option_square] = values[min_option_square][i]
        possibility = search(test_values)
        if possibility:
            return possibility

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    puzzle_dict = grid_values(grid)
    return search(puzzle_dict)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
