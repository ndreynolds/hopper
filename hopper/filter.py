class Filter(object):
    '''
    Filter a list of objects by the values of their attributes.

    This is only a collection of static methods that each return
    the filtered list. As lists are mutable, you don't even need
    to assign the return list to anything.

    Doesn't do any type checking.
    '''

    @staticmethod
    def greater_than(arr, attr, val):
        return filter(lambda x: getattr(x, attr) > val, arr)

    @staticmethod
    def less_than(arr, attr, val):
        return filter(lambda x: getattr(x, attr) < val, arr)

    @staticmethod
    def equal_to(arr, attr, val):
        return filter(lambda x: getattr(x, attr) == val, arr)

    @staticmethod
    def close_to(arr, attr, val, d):
        '''
        Return objects whose attribute, attr, falls inclusively 
        within the range:

            (val - d), (val + d)
        '''
        return filter(lambda x: getattr(x, attr) < (val + d) and \
                getattr(x, attr) > (val - d))

    @staticmethod
    def contains(arr, attr, string):
        return filter(lambda x: string in getattr(x, attr), arr)

    @staticmethod
    def starts_with(arr, attr, string):
        return filter(lambda x: getattr(x, attr).startswith(string), arr)

    @staticmethod
    def ends_with(arr, attr, string):
        return filter(lambda x: getattr(x, attr).endswith(string), arr)
