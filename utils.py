def get_path(package_name : str) :
    package_name = package_name.replace(':', '.')
    path = package_name.split('.')
    return path