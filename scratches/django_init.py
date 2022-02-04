def init():
    os = __import__('os')
    sys = __import__('sys')
    django = __import__('django')

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "liquidemos.settings")

    print('Python %s on %s' % (sys.version, sys.platform))
    print('Django %s' % django.get_version())
    from django.db import connection
    db_name = connection.settings_dict['NAME']
    db_host = connection.settings_dict['HOST']
    print(f'on database "{db_name}" {":" if db_host else ""} {db_host}')

    if 'setup' in dir(django):
        django.setup()

    print("-" * 80)
