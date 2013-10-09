from fabric.api import local, abort, sudo, env, run, put
import boto
import boto.ec2

def pick_region(region='us-west-1', key='app', tag='foliage'):
    env['cxn'] = [r for r in boto.ec2.regions() if r.name == region][0].connect()
    env.user = 'ubuntu'
    env.hosts = []
    for reservation in env['cxn'].get_all_instances():
        for instance in reservation.instances:
            if instance.state == 'running':
            # if instance.tags.get(key) == tag and instance.state == 'running':
                print instance.public_dns_name
                env.hosts.append(instance.public_dns_name)

def build():
    local('rm dist/* || true')
    local('python setup.py sdist')


def install():
    run('rm -rf dist')
    run('mkdir dist')
    sudo('apt-get install -y build-essential python-dev exiv2 python-imaging libjpeg-dev python-setuptools python-pip imagemagick libjpeg-turbo-progs')
    put('dist/*', 'dist')
    sudo('easy_install ~/dist/*.gz')
    

def simpledb_output():
    run('bigsky_simpledb_output')

def simpledb_import():
    run('&'.join(['bigsky_simpledb_import'] * 5))

#def import_originals():
#    run('&'.join(["bigsky_s3_import --url=url_o --targets=exif --source=download_originals --bucket=wnyc.org-foliage-orig"]*5))

def import_thumbs():
    run('&'.join(["bigsky_s3_import --url=url_t --source=download_thumbnails --bucket=wnyc.org-foliage-thumbs"]*5))

def exiv2():
    run('&'.join(["bigsky_exiv2 --source=download_originals --targets=foliage-lightmeter --bucket_out=wnyc.org-foliage-exif"]*3))

def find_outside():
    run("&".join(["bigsky_outside_only --source=foliage-lightmeter --targets=foliage-outdoors --bucket=wnyc.org-foliage-exif"] * 5 ))

def detect_foliage():
    run("while true;do bigsky_foliage_detection --source=foliage-outdoors --targets=foliage-outdoors2 --targets=foliage-detected --bucket=wnyc.org-foliage-thumbs;done ")

