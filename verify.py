"""Реальные опыты Docker Engine на Linux. Запуск: python3 verify.py.

Создает и удаляет только собственные временные контейнеры/сети/тома.
Пароли передаются по имени переменной окружения и не записываются в журнал.
"""
import json
import os
from pathlib import Path
import secrets
import shlex
import subprocess
import time

ROOT = Path(__file__).resolve().parent
PREFIX = 'de-practice-' + secrets.token_hex(3)
containers, networks, volumes = [], [], []
log = None
os.environ['POSTGRES_PASSWORD'] = secrets.token_urlsafe(24)
os.environ['DB_PASSWORD'] = os.environ['POSTGRES_PASSWORD']


def run(*args, fail=False, data=None):
    result = subprocess.run(list(args), input=data, text=True, capture_output=True, timeout=240)
    if log:
        log.write('$ ' + shlex.join(args) + '\n')
        log.write(result.stdout + result.stderr + f'\n[exit={result.returncode}]\n\n')
        log.flush()
    if fail:
        assert result.returncode != 0, 'Expected failure: ' + shlex.join(args)
    elif result.returncode:
        raise RuntimeError('Command failed: ' + shlex.join(args) + '\n' + result.stderr[-1000:])
    return result.stdout.strip()


def docker(*args, **kwargs):
    return run('docker', *args, **kwargs)


def begin(folder):
    global log
    if log:
        log.close()
    target = ROOT / folder / 'evidence'
    target.mkdir(exist_ok=True)
    log = (target / 'verification.txt').open('w')
    log.write('Verified on Linux Docker Engine, 2026-09-24\n\n')
    print(folder, 'started', flush=True)


def build(folder, image, *extra):
    docker('build', *extra, '-t', image, str(ROOT / folder))


def new_name(suffix):
    name = PREFIX + '-' + suffix
    containers.append(name)
    return name


def network(suffix):
    name = PREFIX + '-' + suffix
    docker('network', 'create', '--driver', 'bridge', name)
    networks.append(name)
    return name


def remove(name):
    docker('rm', '-f', name)
    containers.remove(name)


def pg(name, *options):
    docker('run', '-d', '--name', name, '--memory', '192m', *options,
           '-e', 'POSTGRES_USER=practice', '-e', 'POSTGRES_DB=practice',
           '-e', 'POSTGRES_PASSWORD', 'gilachone/simulative-practice-postgres:1.0')
    for _ in range(40):
        result = subprocess.run(['docker','exec',name,'pg_isready','-U','practice','-d','practice'],
                                capture_output=True)
        if result.returncode == 0:
            # pg_isready also succeeds during the init server; wait for actual TCP server.
            result = subprocess.run(['docker','exec',name,'pg_isready','-h','127.0.0.1','-U','practice','-d','practice'],capture_output=True)
            if result.returncode == 0:
                return
        time.sleep(1)
    raise RuntimeError('Postgres did not become ready')


def sql(name, statement):
    return docker('exec', name, 'psql', '-X', '-v', 'ON_ERROR_STOP=1', '-U', 'practice', '-d', 'practice', '-At', '-c', statement)


def pg_volume(name):
    return docker('inspect', '--format', '{{range .Mounts}}{{if eq .Destination "/var/lib/postgresql/data"}}{{.Name}}{{end}}{{end}}', name)


def images():
    begin('01-images')
    image = 'gilachone/simulative-practice-images'
    ids = []
    for version in ['1.0', '2.0']:
        build('01-images/v' + version, image + ':' + version)
        assert ('version ' + version) in docker('run', '--rm', image + ':' + version)
        ids.append(docker('image', 'inspect', '--format', '{{.Id}}', image + ':' + version))
    assert ids[0] != ids[1]
    docker('image', 'ls', image)
    docker('history', image + ':2.0')
    alias = image + ':temporary-check'
    docker('tag', image + ':2.0', alias)
    assert docker('image', 'inspect', '--format', '{{.Id}}', alias) == ids[1]
    saved = str(ROOT / 'work' / 'image.tar')
    docker('save', '-o', saved, alias)
    docker('image', 'rm', alias)
    docker('load', '-i', saved)
    assert docker('image', 'inspect', '--format', '{{.Id}}', alias) == ids[1]
    docker('image', 'rm', alias)


def dockerfile():
    begin('02-dockerfile')
    image = 'gilachone/simulative-practice-dockerfile:1.0'
    build('02-dockerfile', image, '--build-arg', 'APP_VERSION=1.0')
    assert 'Hello, student!' in docker('run', '--rm', image)
    assert 'Hello, Analyst!' in docker('run', '--rm', image, '--name', 'Analyst')
    # Replacing CMD with no --name allows the environment default to take effect.
    result = docker('run', '--rm', '-e', 'APP_NAME=Environment', '--entrypoint', 'python', image, 'app.py')
    assert 'Hello, Environment!' in result
    assert docker('run', '--rm', '--entrypoint', 'python', image, '-c',
                  "from pathlib import Path; assert not Path('/app/ignored.txt').exists(); print('dockerignore OK')") == 'dockerignore OK'
    docker('image', 'inspect', '--format', '{{json .Config.Labels}}', image)
    docker('image', 'inspect', '--format', '{{json .Config.Entrypoint}} {{json .Config.Cmd}} {{.Config.User}}', image)


def lifecycle():
    begin('03-containers')
    image = 'gilachone/simulative-practice-containers:1.0'
    build('03-containers', image)
    name = new_name('run')
    docker('run', '-d', '--name', name, image, '--wait')
    docker('exec', name, 'python', '-c', "from pathlib import Path; Path('/tmp/check.txt').write_text('container data')")
    docker('cp', name + ':/tmp/check.txt', str(ROOT/'work'/'check.txt'))
    assert (ROOT/'work'/'check.txt').read_text() == 'container data'
    docker('diff', name)
    docker('top', name)
    docker('stats', '--no-stream', '--format', '{{.Name}} {{.MemUsage}}', name)
    docker('pause', name)
    assert docker('inspect','--format','{{.State.Paused}}',name) == 'true'
    docker('unpause', name)
    docker('restart', name)
    docker('stop', name)
    assert docker('inspect','--format','{{.State.Status}}',name) == 'exited'
    docker('start', name)
    renamed = new_name('renamed')
    docker('rename', name, renamed)
    containers.remove(name)
    docker('logs', renamed)
    remove(renamed)
    created = new_name('created')
    docker('create', '--name', created, image, '--name', 'Created')
    assert docker('inspect','--format','{{.State.Status}}',created) == 'created'
    assert 'Hello, Created!' in docker('start','-a',created)
    remove(created)


def networking():
    begin('04-networks')
    build('04-networks/postgres', 'gilachone/simulative-practice-postgres:1.0')
    build('04-networks/python', 'gilachone/simulative-practice-networks:1.0')
    netshoot='nicolaka/netshoot:latest'
    docker('pull', netshoot)
    docker('image','inspect','--format','{{json .RepoDigests}}',netshoot)
    docker('network','ls','--format','{{.Name}} {{.Driver}}')
    a,b=new_name('net-a'),new_name('net-b')
    for name in [a,b]:
        docker('run','-d','--name',name,netshoot,'sleep','infinity')
    ipb=docker('inspect','--format','{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',b)
    docker('exec',a,'ping','-c','1','-W','2',ipb)
    docker('exec',a,'ping','-c','1','-W','2',b,fail=True)
    net1,net2=network('bridge1'),network('bridge2')
    for name in [a,b]:
        docker('network','connect',net1,name)
        docker('network','disconnect','bridge',name)
    docker('exec',a,'ping','-c','1','-W','2',b)
    docker('network','inspect','--format','{{.Name}} {{.Driver}} {{len .Containers}}',net1)
    docker('network','connect',net2,b)
    docker('inspect','--format','{{json .NetworkSettings.Networks}}',b)
    docker('network','disconnect',net1,b)
    ipb=docker('inspect','--format','{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',b)
    docker('exec',a,'ping','-c','1','-W','2',ipb,fail=True)
    docker('network','connect',net2,a)
    docker('network','disconnect',net1,a)
    docker('exec',a,'ping','-c','1','-W','2',b)
    docker('run','--rm','--network','host',netshoot,'ping','-c','1','127.0.0.1')
    isolated=new_name('none')
    docker('run','-d','--name',isolated,'--network','none',netshoot,'sleep','infinity')
    docker('exec',isolated,'ip','-brief','address')
    docker('exec',isolated,'ping','-c','1','-W','2',ipb,fail=True)
    docker('network','connect',net2,isolated,fail=True)
    remove(isolated)
    isolated=new_name('none-recreated')
    docker('run','-d','--name',isolated,'--network',net2,netshoot,'sleep','infinity')
    docker('exec',isolated,'ping','-c','1','-W','2',b)
    db=new_name('db')
    pg(db,'--network',net1,'-p','127.0.0.1:15439:5432')
    volumes.append(pg_volume(db))
    app='gilachone/simulative-practice-networks:1.0'
    args=['-e','DB_PASSWORD','-e','DB_HOST='+db]
    result=docker('run','--rm','--network',net1,*args,app)
    assert json.loads(result)==[[1,'Anna'],[2,'Boris'],[3,'Vera']]
    docker('run','--rm','--network',net1,*args,app)
    assert sql(db,'SELECT count(*) FROM users')=='3'
    docker('run','--rm','--network',net2,*args,app,fail=True)
    docker('run','--rm','--network','none',*args,app,fail=True)
    docker('run','--rm','--network','host','-e','DB_PASSWORD','-e','DB_HOST=127.0.0.1','-e','DB_PORT=15439',app)
    for name in [db,a,b,isolated]:
        remove(name)


def storage():
    begin('05-volumes')
    build('05-volumes', 'gilachone/simulative-practice-postgres:1.0')
    seed=(ROOT/'05-volumes'/'seed.sql').read_text()
    name=new_name('no-mount-1')
    pg(name)
    old=pg_volume(name)
    volumes.append(old)
    sql(name,seed)
    remove(name)
    name=new_name('no-mount-2')
    pg(name)
    new=pg_volume(name)
    volumes.append(new)
    assert old != new
    assert sql(name,"SELECT to_regclass('public.practice_marker') IS NULL")=='t'
    remove(name)
    for kind in ['named','anonymous','bind']:
        name=new_name(kind+'-1')
        if kind=='named':
            source=PREFIX+'-data'
            docker('volume','create',source)
            volumes.append(source)
            mount=['--mount',f'type=volume,source={source},target=/var/lib/postgresql/data']
        elif kind=='anonymous':
            mount=['--mount','type=volume,target=/var/lib/postgresql/data']
        else:
            source=str(ROOT/'work'/PREFIX/'bind')
            Path(source).mkdir(parents=True)
            mount=['--mount',f'type=bind,source={source},target=/var/lib/postgresql/data']
        pg(name,*mount)
        sql(name,seed)
        if kind=='anonymous':
            source=pg_volume(name)
            volumes.append(source)
            mount=['--mount',f'type=volume,source={source},target=/var/lib/postgresql/data']
        if kind!='bind':
            docker('volume','inspect','--format','{{.Name}} {{.Driver}}',source)
        else:
            docker('inspect','--format','{{range .Mounts}}{{.Type}} {{.Destination}}{{end}}',name)
        remove(name)
        name=new_name(kind+'-2')
        pg(name,*mount)
        assert sql(name,'SELECT note FROM practice_marker WHERE id=1')=='saved data'
        remove(name)


if __name__=='__main__':
    (ROOT/'work').mkdir(exist_ok=True)
    try:
        for task in [images,dockerfile,lifecycle,networking,storage]:
            task()
            log.write('RESULT: PASS\n')
            log.flush()
            print(task.__name__, 'PASS',flush=True)
    finally:
        if log:
            log.close()
            log=None
        for name in containers:
            subprocess.run(['docker','rm','-f',name],capture_output=True)
        for name in networks:
            subprocess.run(['docker','network','rm',name],capture_output=True)
        for name in volumes:
            subprocess.run(['docker','volume','rm',name],capture_output=True)
