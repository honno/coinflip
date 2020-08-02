# Recorded with the doitlive recorder
#doitlive shell: /bin/bash
#doitlive prompt: default

pwd

cd randtests

pytest test_examples.py --example "binary.*small"

pytest test_examples.py --example ".*fourier.*small"

pytest implementations/test_sgr.py implementations/test_dj.py --example ".*fourier.*small"

pytest test_comparisons.py -k "monobits" --disable-warnings -s --hypothesis-verbosity=verbose

pytest test_comparisons.py -k "frequency_within_block" --disable-warnings -s --hypothesis-verbosity=verbose

cd ..

pytest test_cli.py -k "TestCliRoutes" --disable-warnings -s --hypothesis-verbosity=debug --hypothesis-profile=fast

tox -e py37


