import distutils.sysconfig
import multiprocessing
import os
import sys
import tempfile
import zipfile

import nose
import requests


DATA_DIR = os.path.join(tempfile.gettempdir(), 'iris-conda-data')


def fetch_data(prefix, git_ref):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    zip_name = prefix + '.zip'
    zip_path = os.path.join(DATA_DIR, zip_name)
    if os.path.exists(zip_path):
        print('Skipping download/unzip for', prefix)
    else:
        url_fmt = 'https://github.com/SciTools/{}/archive/{}.zip'
        url = url_fmt.format(prefix, git_ref)
        print('Downloading', url)
        response = requests.get(url, stream=True)
        with open(zip_path, 'wb') as zip_file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                zip_file.write(chunk)
                sys.stdout.write('.')
                sys.stdout.flush()
            print()

        print('Unzipping', zip_path)
        with zipfile.ZipFile(zip_path, 'r') as data_zip:
            data_zip.extractall(DATA_DIR)

        unzipped_dir = prefix + '-' + git_ref.replace('v', '')
        os.rename(os.path.join(DATA_DIR, unzipped_dir),
                  os.path.join(DATA_DIR, prefix))


def create_site_cfg():
    site_package_dir = distutils.sysconfig.get_python_lib()
    config_path = os.path.join(site_package_dir, 'iris', 'etc', 'site.cfg')
    print('Creating', config_path)
    with open(config_path, 'w') as site_cfg:
        site_cfg.write('[System]\n')
        fmt = 'udunits2_path = {}/lib/libudunits2.so\n'
        site_cfg.write(fmt.format(os.environ['PREFIX']))

        site_cfg.write('[Resources]\n')
        fmt = 'sample_data_dir = {}/iris-sample-data/sample_data\n'
        site_cfg.write(fmt.format(DATA_DIR))
        fmt = 'test_data_dir = {}/iris-test-data/test_data\n'
        site_cfg.write(fmt.format(DATA_DIR))


def run_tests():
    regexp_pat = r'--match=^([Tt]est(?![Mm]ixin)|[Ss]ystem)'
    n_processors = max(multiprocessing.cpu_count() - 1, 1)

    print('Running tests with {} processes'.format(n_processors))

    args = ['', 'iris.tests', '--processes=%s' % n_processors,
            '--stop', # XXX Remove me?
            '--verbosity=2', regexp_pat, '--process-timeout=250']
    result = nose.run(argv=args)
    print('nose result:', result)
    return result


if __name__ == '__main__':
    print('os.getcwd(): ', os.getcwd())
    fetch_data('iris-test-data', '3378fe68c00ca7f31895ab6630a59a39ccef94e3')
    fetch_data('iris-sample-data', '1ed3e26606366717e2053bacc12bf5e8d8fa2704')
    create_site_cfg()
    if not run_tests():
        exit(1)
