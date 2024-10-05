from .handlers import ppxc, ppxc_list

urls = [
    {'method': 'GET', 'path': '/ppxc', 'handler': ppxc},
    {'method': 'GET', 'path': '/ppxc_list', 'handler': ppxc_list},
]