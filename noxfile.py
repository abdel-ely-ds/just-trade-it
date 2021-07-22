import nox


@nox.session
def test(session):
    session.install("pytest")
    session.run("pytest")


@nox.session
def lint(session):
    session.install("flake8")
    session.run("flake8")
