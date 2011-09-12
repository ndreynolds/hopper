class BadReference(Exception):
    '''No object matches the identifier'''
    pass

class AmbiguosReference(Exception):
    '''Multiple objects match the identifier'''
    pass
