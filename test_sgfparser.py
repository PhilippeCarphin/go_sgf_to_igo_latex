import os
import sgfparser as sgf

if __name__ == "__main__":
    filename = os.path.join(os.getcwd(), 'edit.sgf')
    with open(filename) as f:
        file_content = f.read()

    # print('\n'.join(sgf.make_file_tokens(file_content)))

    print(sgf.make_file_tokens(file_content))
    # sgf.print_tree(sgf.make_tree(file_content))
