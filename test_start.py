import start


def test_expandvars():
    env = {"NAME": "Fry"}

    tests = [
        # just vars
        ('$NAME', b'Fry', env),
        ('${NAME}', b'Fry', env),
        ('${NAME:-Zoidberg}', b'Fry', env),
        ('${NAME:-Zoidberg}', b'Zoidberg', {}),

        # quoted
        ('"$NAME"', b'"Fry"', env),
        ('"${NAME}"', b'"Fry"', env),
        ('"${NAME:-Zoidberg}"', b'"Fry"', env),
        ('"${NAME:-Zoidberg}"', b'"Zoidberg"', {}),

        # single quoted
        ("'$NAME'", b"'Fry'", env),

        # multiple vars and special characters
        (
            '$FRY ${ZOIDBERG:-whoopwhoop} ${NOTZOIDBERG:-whoopwhoop}',
            b'Fry Zoidberg whoopwhoop',
            {
                'FRY': "Fry",
                "AMY": "Amy",
                "ZOIDBERG": "Zoidberg",
            }
        ),

        # inside echo statements
        ('echo "Hi $NAME"', b'echo "Hi Fry"', env),
        ('echo "Hi ${NAME}"', b'echo "Hi Fry"', env),
        ('echo "Hi ${NAME:-Zoidberg}"', b'echo "Hi Fry"', env),
        ('echo "Hi ${NAME:-Zoidberg}"', b'echo "Hi Zoidberg"', {}),

        # unquoted echo statements
        ('echo Hi $NAME', b'echo Hi Fry', env),
        ('echo Hi ${NAME}', b'echo Hi Fry', env),
        ('echo Hi ${NAME:-default}', b'echo Hi Fry', env),
        ('echo Hi ${NAME:-default}', b'echo Hi default', {}),

        # special cases
        ('${LS_CMD} -lAF', b'ls -lAF', {'LS_CMD': "ls"}),
        ('\\', b'\\', {}),
        ('\\\\', b'\\\\', {}),
    ]
    for test in tests:
        assert test[1] == start.expandvars(test[0], env=test[2])


def test_parse_command():
    env = {"NAME": "Fry"}
    tests = [
        # just vars
        ('"$NAME"', [b'Fry'], env),
        ('${NAME}', [b'Fry'], env),
        ('${NAME:-Zoidberg}', [b'Fry'], env),
        ('${NAME:-Zoidberg}', [b'Zoidberg'], {}),

        # inside echo statements
        ('echo "Hi $NAME"', [b'echo', b'Hi Fry'], env),
        ('echo "Hi ${NAME}"', [b'echo', b'Hi Fry'], env),
        ('echo "Hi ${NAME:-Zoidberg}"', [b'echo', b'Hi Fry'], env),
        ('echo "Hi ${NAME:-Zoidberg}"', [b'echo', b'Hi Zoidberg'], {}),

        # unquoted echo statements
        ('echo Hi $NAME', [b'echo', b'Hi', b'Fry'], env),
        ('echo Hi ${NAME}', [b'echo', b'Hi', b'Fry'], env),
        ('echo Hi ${NAME:-Zoidberg}', [b'echo', b'Hi', b'Fry'], env),
        ('echo Hi ${NAME:-Zoidberg}', [b'echo', b'Hi', b'Zoidberg'], {}),

        # special cases
        ('${LS_CMD} -lAF', [b'ls', b'-lAF'], {'LS_CMD': "ls"}),

        # tricky cases
        # ------------

        # shell string concatenation
        (
            ''' echo 'I want a single quote here: -> '"'"' <- ' '''.strip(),
            [b'echo', b"I want a single quote here: -> ' <- "],
            {}
        ),
        # shell string concatenation II
        (
            ''' echo "I want a single quote here: -> ' <- " '''.strip(),
            [b'echo', b"I want a single quote here: -> ' <- "],
            {}
        ),
        # shell string concatenation III
        (
            ''' echo "I want a double quote here: -> \\" <- " '''.strip(),
            [b'echo', b'I want a double quote here: -> " <- '],
            {}
        ),
        # subshell
        (
            ''' echo "I want a command result here: -> `cd /;pwd` <- " '''.strip(),
            [b'echo', b'I want a command result here: -> / <- '],
            {}
        ),

    ]
    for test in tests:
        assert test[1] == start.parse_command(test[0], env=test[2])


def test_procfile_parsing():
    procfile_tests = [
        (
            (
                'web: echo "Hi"\n'
                '# comment for other\n'
                'other: echo "other"'
            ),
            {
                'web': 'echo "Hi"',
                'other': 'echo "other"',
            }
        ),
        (
            (
                'web: run --concurrency=${CONCURRENCY:-4}\n'
                'other: echo "other"'
            ),
            {
                'web': 'run --concurrency=${CONCURRENCY:-4}',
                'other': 'echo "other"',
            }
        ),
    ]
    for procfile_test in procfile_tests:
        parsed_procfile = start.parse_procfile(procfile_test[0])
        for service, command in procfile_test[1].items():
            assert parsed_procfile.processes[service] == command
