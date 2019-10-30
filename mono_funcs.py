from lab_chit.var_class import *


def _mono_function(x, name_func: str, name_func_for_numpy: str = None,
                   real_name: str = None):
    """
    На случай, если вам захочется сделать свою функцию, которая есть в numpy и sympy.
    """
    if name_func_for_numpy is None:
        name_func_for_numpy = name_func
    if real_name is None:
        real_name = name_func
    if isinstance(x, GroupVar):
        return tuple(_all_funcs[real_name](var) for var in x)
    if isinstance(x, AbstractVar):
        return AbstractVar(getattr(sp, name_func)(x.story), len(x))
    else:
        return getattr(np, name_func_for_numpy)(x)


def sqrt(x):
    return _mono_function(x, 'sqrt')


def sin(x):
    return _mono_function(x, 'sin')


def cos(x):
    return _mono_function(x, 'cos')


def tg(x):
    return _mono_function(x, 'tan', real_name='tg')


def ctg(x):
    if isinstance(x, AbstractVar):
        return AbstractVar(sp.tan(sp.pi / 2 - x.story), x.len)
    elif isinstance(x, GroupVar):
        return _mono_function(x, 'ctg', real_name='ctg')
    else:
        return np.tan(np.pi / 2 - x)


def arctg(x):
    return _mono_function(x, 'atan', name_func_for_numpy='arctan', real_name='arctg')


def arcctg(x):
    if isinstance(x, AbstractVar):
        return AbstractVar(sp.pi / 2 - sp.atan(x.story), x.len)
    elif isinstance(x, GroupVar):
        return _mono_function(x, 'ctg', real_name='arcctg')
    else:
        return np.pi / 2 - np.arctan(x)


def arcsin(x):
    return _mono_function(x, 'asin', name_func_for_numpy='arcsin', real_name='arcsin')


def arccos(x):
    return _mono_function(x, 'acos', name_func_for_numpy='arccos', real_name='arccos')


def sh(x):
    return _mono_function(x, 'sinh', real_name='sh')


def ch(x):
    return _mono_function(x, 'cosh', real_name='ch')


def th(x):
    return _mono_function(x, 'tanh', real_name='th')


def cth(x):
    if isinstance(x, GroupVar):
        return _mono_function(x, 'cth', real_name='cth')
    return 1 / th(x)


def arcth(x):
    return _mono_function(x, 'atanh', name_func_for_numpy='arctanh', real_name='arcth')


def arcsh(x):
    return _mono_function(x, 'asinh', name_func_for_numpy='arcsinh', real_name='arcsh')


def arcch(x):
    return _mono_function(x, 'acosh', name_func_for_numpy='arccosh', real_name='arcch')


def exp(x):
    return _mono_function(x, 'exp')


def ln(x):
    return _mono_function(x, 'log', real_name='ln')


def mean(x):
    if isinstance(x, GroupVar):
        return _mono_function(x, 'mean', real_name='mean')
    if isinstance(x, (tuple, list, np.ndarray)):
        return np.mean(np.array(x))
    # Будьте осторожны!
    # Эта функция производит Var неявно
    # Это приводит к неточности в оценке ошибок при одновременном использовани x и mean(x)
    xval = x.val()
    val = np.mean(xval)
    err = np.sqrt(sum(x.err() ** 2) / (len(xval) - 1) / len(xval))
    return Var(val, err)


_all_funcs = {'sqrt': sqrt, 'sin': sin, 'cos': cos, 'tg': tg, 'ctg': ctg, 'arctg': arctg, 'arcctg': arcctg,
              'arcsin': arcsin, 'arccos': arccos, 'sh': sh, 'ch': ch, 'th': th, 'cth': cth, 'arcth': arcth,
              'arcsh': arcch, 'exp': exp, 'ln': ln, 'mean': mean}

def step(x, style: str = 'classic_dermo'):
    if style is 'classic_dermo':
        if len(x) == 2:
            X = x.val()
            Xerr = x.err()
            return Var(X[1] - X[0], np.sqrt(Xerr[1] ** 2 + Xerr[0] ** 2))
        if len(x) == 3:
            X = x.val()
            Xerr = x.err()
            return Var(((X[2]-X[0])/2+X[1]-X[0])/2, np.sqrt(((Xerr[2]/2)**2+(Xerr[1])**2+(Xerr[0]*3/2)**2)/2)/2)
        X = np.array(range(len(x)))
        Y = x.val()
        k = (np.mean(X * Y) - np.mean(X) * np.mean(Y)) / (np.mean(X ** 2) - np.mean(X) ** 2)
        b = np.mean(Y) - k * np.mean(X)
        Sy = sum((Y - b - k * X) ** 2) / (len(X) - 2)
        D = len(X) * sum(X ** 2) - (sum(X)) ** 2
        dk = np.sqrt(Sy * len(X) / D)
        return Var(k, dk)
    elif style is 'at_least_better_dermo':
        ...
    else:
        raise TypeError('Ишь чего захотел!')
