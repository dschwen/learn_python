#!/usr/bin/env python3

import sys
import json
from markdownify import markdownify

if len(sys.argv) != 3 :
    print("Usage:\n", sys.argv[0], "infile.html outfile.ipynb")
    sys.exit(1)

def tomarkdown(block):
    md = markdownify(''.join(block)).rstrip().split('\n')
    return [l+'\n' for l in md]

def tosource(block):
    src = ''.join(block).strip().split('\n')
    src = [l+'\n' for l in src]
    src[-1] = src[-1].rstrip()
    return src

infile = sys.argv[1]
outfile = sys.argv[2]

with open(infile, 'r') as file:
    htmlfile = file.readlines()

cells = []
block = []
incode = False
head = True

for line in htmlfile :
    # still in header?
    if head :
        if line == '</H1>\n' :
            head = False
        continue

    # end of page
    if line == '<DIV CLASS="navigation"><HR>\n' :
        break

    # preprocess line
    line = line.replace('<PRE  CLASS="verbatim">', '<PRE>')

    # start of a code block
    if line[:len('<PRE>')] == '<PRE>' :
        if not incode:
            cells.append({"source": tomarkdown(block), "cell_type": "markdown", "metadata": {}})

            incode = True
            block = []
        line = line[len('<PRE>'):]

    # end of a code block
    if line[:len('</PRE>')] == '</PRE>' :
        if incode:
            cells.append({"source": tosource(block), "cell_type": "code", "metadata": {}, "outputs": [], "execution_count": None})
            incode = False
            block = []
        line = line[len('</PRE>'):]

    if incode :
        # preprocess code
        line = line.replace('&gt;', '>')
        line = line.replace('&lt;', '<')
    else:
        # preprocess text
        line = line.replace('`', "'")

    # add regular text
    block.append(line)

# final block
if not incode:
    cells.append({"source": tomarkdown(block), "cell_type": "markdown", "metadata": {}})
else :
    cells.append({"source": tosource(block), "cell_type": "code", "metadata": {}, "outputs": [], "execution_count": None})

# write notebook
with open(outfile, 'w') as file:
    file.write(json.dumps({
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.10"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4}))
