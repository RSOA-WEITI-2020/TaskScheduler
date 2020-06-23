import nox


@nox.session(python=False)
def tests(session):
    session.run('poetry', 'install')
    session.run('poetry', 'run', 'pytest')
