#!/bin/bash

latex $1.tex
bibtex $1
latex $1.tex
latex $1.tex
dvips -Ppdf -o $1.ps $1.dvi
ps2pdf $1.ps