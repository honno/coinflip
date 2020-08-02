# Recorded with the doitlive recorder
#doitlive shell: /bin/bash
#doitlive prompt: default

coinflip --help

coinflip ls

gedit "rng_output.txt" &

coinflip load "rng_output.txt" --name example

coinflip ls

coinflip run example

gedit "rng_output2.txt" &

coinflip load "rng_output2.txt" --name example2

coinflip ls

coinflip run example2 --test binary_matrix_rank

coinflip rm example2

coinflip ls

coinflip rm-all

coinflip ls

firefox https://coinflip.readthedocs.io/

