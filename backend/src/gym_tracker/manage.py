"""Administration commands.

- ``uv run gym-admin create-user --email you@example.com``
- ``uv run gym-admin seed-catalog``
"""

from __future__ import annotations

import argparse
import getpass
import io
import sys

from gym_tracker.catalog import seed_catalog
from gym_tracker.db import get_sessionmaker
from gym_tracker.users import MIN_PASSWORD_LENGTH, UserAlreadyExistsError, create_user


def _create_user(parser: argparse.ArgumentParser, email: str) -> None:
    password = getpass.getpass("Contraseña: ")
    if len(password) < MIN_PASSWORD_LENGTH:
        parser.error(f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres")
    if getpass.getpass("Repite la contraseña: ") != password:
        parser.error("Las contraseñas no coinciden")

    with get_sessionmaker()() as session:
        try:
            user = create_user(session, email=email, password=password)
        except UserAlreadyExistsError:
            parser.error(f"Ya existe un usuario con el email {email}")
        session.commit()
        print(f"Usuario creado: {user.email} (id {user.id})")


def _seed_catalog() -> None:
    with get_sessionmaker()() as session:
        count = seed_catalog(session)
        session.commit()
    print(f"Catálogo actualizado: {count} ejercicios")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="gym-admin", description="Tareas de administración")
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create-user", help="Crea un usuario")
    create.add_argument("--email", required=True)
    commands.add_parser("seed-catalog", help="Crea o actualiza el catálogo de ejercicios")
    args = parser.parse_args(argv)

    if isinstance(sys.stdout, io.TextIOWrapper):  # Windows consoles default to a legacy code page
        sys.stdout.reconfigure(encoding="utf-8")
    if args.command == "create-user":
        _create_user(parser, args.email)
    else:
        _seed_catalog()


if __name__ == "__main__":
    main()
