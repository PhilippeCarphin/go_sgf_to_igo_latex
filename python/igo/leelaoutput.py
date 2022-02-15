def parse_output(output):
    lines = output.split('\n')
    analysis_lines = get_analysis_lines(lines)
    analysis_data = [parse_analysis_line(l) for l in  analysis_lines]
    return analysis_data


def parse_analysis_line(line, player='B'):
    parsed_line = {}
    words = line.split()
    parsed_line['move'] = words[0]
    player_eval = float(words[4].strip('%)')) / 100
    parsed_line['evaluation'] = player_eval if player == 'B' else 1 - player_eval
    parsed_line['evaluation'] = float(words[4].strip('%)')) / 100
    parsed_line['likelihood'] = float(words[6].strip('%)')) / 100
    parsed_line['variation'] = words[8:]
    return parsed_line


def move_rank(move, analysis_data):
    for i in range(len(analysis_data)):
        if analysis_data[i]['move'] == move:
            return i
    return -1


def evaluation(analysis_data):
    return analysis_data[0]['evaluation']


def move_likelihood(move, analysis_data):
    for ad in analysis_data:
        if ad['move'] == move:
            return ad['likelihood']
    return 0.0


def get_analysis_lines(lines):
    analysis = []
    for line in lines:
        if is_analysis(line):
            analysis.append(line)
    return analysis


def is_playout(string):
    return 'Playouts' in string


def is_analysis(string):
    return '->' in string


if __name__ == "__main__":
    import os
    filepath = os.path.join(os.path.dirname(__file__), '..', 'test_files', 'genmove_output', 'output-1.txt')

    with open(filepath) as f:
        file_content = f.read()

    analysis_data = parse_output(file_content)
    print(move_rank('Q16', analysis_data))
    print(move_likelihood('Q16', analysis_data))
    print(evaluation(analysis_data))


