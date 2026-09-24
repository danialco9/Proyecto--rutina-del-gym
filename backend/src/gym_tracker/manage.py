"""Administration commands.

- ``uv run gym-admin create-user --email you@example.com``
- ``uv run gym-admin reset-password --email someone@example.com``
- ``uv run gym-admin seed-catalog``
- ``uv run gym-admin seed-demo``
"""

from __future__ import annotations

import argparse
import getpass
import io
import sys

from gym_tracker.catalog import seed_catalog
from gym_tracker.db import get_sessionmaker
from gym_tracker.demo import DEMO_EMAIL, DEMO_PASSWORD, seed_demo
from gym_tracker.users import (
    MIN_PASSWORD_LENGTH,
    UserAlreadyExistsError,
    create_user,
    get_user_by_email,
    set_password,
)


def _ask_password(parser: argparse.ArgumentParser) -> str:
    password = getpass.getpass("Contraseña: ")
    if len(password) < MIN_PASSWORD_LENGTH:
        parser.error(f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres")
    if getpass.getpass("Repite la contraseña: ") != password:
        parser.error("Las contraseñas no coinciden")
    return password


def _create_user(parser: argparse.ArgumentParser, email: str) -> None:
    password = _ask_password(parser)
    with get_sessionmaker()() as session:
        try:
            user = create_user(session, email=email, password=password)
        except UserAlreadyExistsError:
            parser.error(f"Ya existe un usuario con el email {email}")
        session.commit()
        print(f"Usuario creado: {user.email} (id {user.id})")


def _reset_password(parser: argparse.ArgumentParser, email: str) -> None:
    """Sets a new password for someone who forgot theirs; there is no reset by email yet."""
    with get_sessionmaker()() as session:
        if get_user_by_email(session, email) is None:
            parser.error(f"No existe ningún usuario con el email {email}")
        password = _ask_password(parser)
        user = set_password(session, email=email, password=password)
        session.commit()
        print(f"Contraseña cambiada: {user.email}")


def _seed_catalog() -> None:
    with get_sessionmaker()() as session:
        count = seed_catalog(session)
        session.commit()
    print(f"Catálogo actualizado: {count} ejercicios")


def _seed_demo(email: str, password: str, weeks: int) -> None:
    with get_sessionmaker()() as session:
        summary = seed_demo(session, email=email, password=password, weeks=weeks)
        session.commit()
    # A custom password (e.g. generated in CI) is never printed, so it stays out of logs.
    credentials = f"{email} / {password}" if password == DEMO_PASSWORD else email
    print(
        f"Cuenta demo lista: {credentials} "
        f"({summary.workouts} entrenos y {summary.measurements} medidas en {weeks} semanas)"
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="gym-admin", description="Tareas de administración")
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create-user", help="Crea un usuario")
    create.add_argument("--email", required=True)
    reset = commands.add_parser("reset-password", help="Cambia la contraseña de un usuario")
    reset.add_argument("--email", required=True)
    commands.add_parser("seed-catalog", help="Crea o actualiza el catálogo de ejercicios")
    demo = commands.add_parser("seed-demo", help="Crea o recrea la cuenta demo con entrenos simulados")
    demo.add_argument("--email", default=DEMO_EMAIL)
    demo.add_argument("--password", default=DEMO_PASSWORD)
    demo.add_argument("--weeks", type=int, default=12)
    args = parser.parse_args(argv)

    if isinstance(sys.stdout, io.TextIOWrapper):  # Windows consoles default to a legacy code page
        sys.stdout.reconfigure(encoding="utf-8")
    if args.command == "create-user":
        _create_user(parser, args.email)
    elif args.command == "reset-password":
        _reset_password(parser, args.email)
    elif args.command == "seed-demo":
        _seed_demo(args.email, args.password, args.weeks)
    else:
        _seed_catalog()


if __name__ == "__main__":
    main()
