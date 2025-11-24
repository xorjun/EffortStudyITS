from edist.sed import sed_backtrace
from edist import edits

from edist.edits import Insertion, Deletion, Replacement

x = 'prinz'
y = 'print'
z = 'print("hello")\nprint("goodbuye")'


if __name__ == "__main__":

    # compute changes via edit distance
    alignment = sed_backtrace(x, y)
    # translate alignment to edit script
    script = edits.alignment_to_script(alignment, x, y)

    print('change from "%s" to "%s"' % (x, y))
    print(script)


    # compute changes via edit distance
    alignment = sed_backtrace(y, z)
    # translate alignment to edit script
    script = edits.alignment_to_script(alignment, y, z)

    print('change from "%s" to "%s"' % (y, z))
    print(script)

    print([x.__class__.__name__ for x in script])

