import movetree

def rotate(filename):
    move_tree = None
    try:
        move_tree = movetree.Tree(filename)
    except IOError:
        return
    output = movetree.write_sgf(move_tree, True)
    parts = filename.split('.')

    # (Everything before '.sgf') + '_turned.sgf'
    output_file = '.'.join(parts[:-1]) + '_turned.sgf'
    with open(output_file, 'w') as f:
        f.write(output)

if __name__ == "__main__":
    print("Phil's file turner")
    to_rotate = input("Enter name of file to turn : ")
    rotate(to_rotate)
    input("Press enter to exit")
