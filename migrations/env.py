from app import create_app, db

app = create_app()  # Create an instance of Flask app

with app.app_context():  # Ensure migrations run inside Flask's context
    from alembic import context
    import logging
    from logging.config import fileConfig

    config = context.config
    fileConfig(config.config_file_name)
    logger = logging.getLogger('alembic.env')

    def get_engine():
        return db.get_engine()

    def get_engine_url():
        return str(get_engine().url).replace('%', '%%')

    config.set_main_option('sqlalchemy.url', get_engine_url())
    target_db = db

    def get_metadata():
        return target_db.metadata

    def run_migrations_offline():
        context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=get_metadata(), literal_binds=True)
        with context.begin_transaction():
            context.run_migrations()

    def run_migrations_online():
        connectable = get_engine()
        with connectable.connect() as connection:
            context.configure(connection=connection, target_metadata=get_metadata())
            with context.begin_transaction():
                context.run_migrations()

    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
