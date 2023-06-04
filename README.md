# whipper-zipper
Silly spreadsheet app

# named relative refs

    =sum(above)
    =sum(below)
    =sum(left)
    =sum(right)

# typed values?
Everything is a double by default

But I can do:

    A1 = i8(127)
    A2 = u8(255)
    A3 = A1 + A2


# Use a Worksheet as a User Defined Function (UDF)
Don't use VBA like excel, use worksheets!

Define some cells as input, some as output and everything else is fair game.

param('name', default_value)
then the worksheet name becomes the function

# auto name cells using the cell to their left

|#|A         |B                      |
|-|----------|-----------------------|
|1|first-name|will                   |
|2|last-name |br                     |
|3|name      |=first-name + last-name|
|4|          |                       |
|5|          |                       |

# JIT compiler
I need to learn about X86 assembly

# show code and output at the same time

$output :: $formula


# modal editing
vi keys

# use space as tab

type:

    first-name will

and it creates values over two columns
