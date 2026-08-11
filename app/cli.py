import click

from app import db
from app.models.usuario import Usuario, RolUsuario


def registrar_comandos_cli(app):
    @app.cli.command("crear-admin")
    @click.argument("correo")
    def crear_admin(correo):
        """Promueve a un usuario ya registrado (por correo) al rol de administrador."""
        usuario = Usuario.query.filter_by(correo=correo.strip().lower()).first()
        if not usuario:
            click.echo(f"No existe ningún usuario registrado con el correo {correo}")
            return

        usuario.rol = RolUsuario.ADMIN
        db.session.commit()
        click.echo(f"{usuario.nombre_completo} ({usuario.correo}) ahora es administrador")
