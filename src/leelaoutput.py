import os

def best_moves(analysis_output):
    """
    Takes the whole output of a genmove command and returns a list of the
    moves chosen by leela-zero
    """
    return ['A4']

def evaluation(analysis_output):
    """
    Finds leela-zero's evaluation of the position from it's output for a
    genmove command.
    """
    return 50.001

if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), '..', 'test_files', 'genmove_output', 'output-1.txt')

    with open(filepath) as f:
        analysis = f.read()

    expected = [
        'Q16',
        'R16',
        'Q17',
        'Q3',
        'D16',
        'Q4',
        'R4',
        'C16',
        'D17',
        'C3',
    ]
    if best_moves(analysis) != expected:
        print("function best_moves failed for input" + filepath)

    expected = '52.21'
    if evaluation(analysis) != expected:
        print("Function evaluation() did not owrk for input" + filepath)
