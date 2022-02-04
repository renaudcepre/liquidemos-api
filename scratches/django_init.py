def init():
    os = __import__('os')

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "liquidemos.settings")
    sys = __import__('sys')

    print('Python %s on %s' % (sys.version, sys.platform))
    django = __import__('django')

    print('Django %s' % django.get_version())
    sys.path.extend(['/home/rcepre/dev/liquidemos', '/home/rcepre/dev/liquidemos/apps/projects/tests',
                     '/snap/pycharm-professional/271/plugins/python/helpers/pycharm',
                     '/snap/pycharm-professional/271/plugins/python/helpers/pydev'])
    if 'setup' in dir(django):
        django.setup()
    print("-" * 80)
