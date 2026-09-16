"""Administration commands: ``uv run gym-admin create-user --email you@example.com``."""

from __future__ import annotations

import argparse
import getpass

from gym_tracker.db import get_sessionmaker
from gym_tracker.users import MIN_PASSWORD_LENGTH, UserAlreadyExistsError, create_user


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="gym-admin", description="Tareas de administración")
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create-user", help="Crea un usuario")
    create.add_argument("--email", required=True)
    args = parser.parse_args(argv)

    password = getpass.getpass("Contraseña: ")
    if len(password) < MIN_PASSWORD_LENGTH:
        parser.error(f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres")
    if getpass.getpass("Repite la contraseña: ") != password:
        parser.error("Las contraseñas no coinciden")

    with get_sessionmaker()() as session:
        try:
            user = create_user(session, email=args.email, password=password)
        except UserAlreadyExistsError:
            parser.error(f"Ya existe un usuario con el email {args.email}")
        session.commit()
        print(f"Usuario creado: {user.email} (id {user.id})")


if __name__ == "__main__":
    main()
