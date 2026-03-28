import classyclick


class Who(classyclick.Group):
    """autodiscover fixture root"""

    __config__ = classyclick.Group.Config(name='who')
