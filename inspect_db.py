from pathlib import Path
from app import create_app
app = create_app()
print('INSTANCE_PATH=' + app.instance_path)
inst = Path(app.instance_path)
print('INSTANCE_EXISTS=' + str(inst.exists()))
print('INSTANCE_IS_DIR=' + str(inst.is_dir()))
db_path = inst / 'home_builders.db'
print('DB_PATH=' + str(db_path))
print('DB_EXISTS=' + str(db_path.exists()))
print('SQLALCHEMY_DATABASE_URI=' + app.config['SQLALCHEMY_DATABASE_URI'])
