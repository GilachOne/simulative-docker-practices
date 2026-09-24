import os
from pathlib import Path
import secrets

root = Path(__file__).resolve().parent
if (root / '.env').exists():
    raise SystemExit('.env already exists; leaving local settings unchanged')
password = secrets.token_urlsafe(24)
(root / '.env').write_text('POSTGRES_PASSWORD=' + password + '\nPGADMIN_PASSWORD=' + secrets.token_urlsafe(24) + '\n')
(root / '.env').chmod(0o600)
(root / 'work').mkdir(exist_ok=True)
pgpass = root / 'work/pgpass'
pgpass.write_text('postgres:5432:practice:practice:' + password + '\n')
pgpass.chmod(0o600)
if hasattr(os, 'geteuid') and os.geteuid() == 0:
    os.chown(pgpass, 5050, 5050)
print('Local configuration created; passwords are not printed')
