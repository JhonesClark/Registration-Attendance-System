from pathlib import Path
from flask import Flask
app = Flask(__name__, instance_relative_config=True)
print('INSTANCE_PATH=' + app.instance_path)
inst = Path(app.instance_path)
print('INST_EXISTS=' + str(inst.exists()))
print('INST_IS_DIR=' + str(inst.is_dir()))
print('INST_ABS=' + str(inst.resolve()))
db = inst / 'home_builders.db'
print('DB_PATH=' + str(db))
print('DB_EXISTS=' + str(db.exists()))
print('DB_POSIX=' + db.as_posix())
try:
    test_file = inst / 'inspect_write_test.tmp'
    test_file.write_text('test')
    print('WRITE_OK=True')
    test_file.unlink()
except Exception as e:
    print('WRITE_OK=False')
    print('WRITE_ERROR=' + repr(e))
