``test_cli.py`` is responsible for `smoke testing
<https://www.freecodecamp.org/news/smoke-testing/>`_ the CLI, running the
application using Click's `CliRunner
<https://click.palletsprojects.com/en/7.x/testing/>`_. It also specifies the CLI
as a state machine, utilising `stateful testing
<https://hypothesis.readthedocs.io/en/latest/stateful.html>`_ to ensure the
store abstraction of the user data directory works as intended.

``randtests/`` covers the `randomness tests
<https://coinflip.readthedocs.io/en/latest/reference/randtests/index.html>`_
themselves—see its `README <./randtests/README.rst>`_ for more information.
