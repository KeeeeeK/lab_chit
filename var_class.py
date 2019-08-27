import numpy as np
import sympy as sp

# Это словарь с символами-ключами и прямыми переменными-значениями
_DictSymVar = {}
_AloneVar = 0


# Принципиальная разница между косвенной и прямой переменной в том, что их погрешности рассчитываются по-другому
# Конструктор для прямой переменной сделан так, чтобы пользователь не создавал невальидные экземпляры
# Конструктор прямой переменной имеет право создавать символы, а косвенной - нет.

class AbstractVar:
    """
    Не рекомендуется вызывать экземпляры AbstractVar посредством инициализации!!

    AbstractVar хранит в себе:
    story - формула, по которой можно получить данную переменную через переменные прямых измерений.
        Если туда заглянуть, то можно ничего и не понять. Для того, чтобы всё выглядело по-человечески, надо установить
        человеческие имена используемым Var. Сделать это можно, добавив Var(..., ..., name='Name').
    len - размер серии измерений, соответствующих данной переменной.
        Размер 0 соответствует одиночной переменной. Не стоит путать с серией длиной 1.
    """

    def __init__(self, story: sp.symbol.Symbol, len: int):
        self.story = story
        # Это поле тоже необходимо, потому что, формально говоря, при сложении 2-мерных и 3-мерных данных ошибка
        # обнаружится только при вычислениях, а должны выдаваться сразу!
        self.len = len

    @staticmethod
    def _val(args, _func):
        return _func(tuple(_DictSymVar[sym].value for sym in args))

    def val(self):
        """
        guess yourself
        """
        args = tuple(self.story.free_symbols)
        _func = sp.lambdify((args,), self.story, 'numpy')
        return self._val(args, _func)

    @staticmethod
    def _err(args, _partial_diffs):
        args_val = tuple(_DictSymVar[sym].value for sym in args)
        args_err = tuple(_DictSymVar[sym].error for sym in args)
        partial_errors_squared = tuple((func(args_val) * args_err[i]) ** 2 for i, func in enumerate(_partial_diffs))
        return np.sqrt(sum(partial_errors_squared))

    def err(self):
        """
        guess yourself
        """
        args = tuple(self.story.free_symbols)
        _partial_diffs = tuple(sp.lambdify((args,), self.story.diff(sym), 'numpy') for sym in args)
        return self._err(args, _partial_diffs)

    def __len__(self):
        return self.len

    def simplify(self):
        """
        Вычисления вида:
            v = Var(1,1, name='v')
            x=v/v+v-v
            y=x^x^x^(x/(x+x))
        приведут к ужасной истории y, хотя y.val() и y.err() будут посчитаны верно, займут на порядок больше времени,
        чем если перед этим упростить self.story
        Не знаю зачем, но пусть будет.
        """
        self.story = sp.simplify(self.story)

    def __str__(self):
        return '(' + str(self.val()) + ',' + str(self.err()) + ')'

    def _for_binary_operation_check_len(self, other):
        if len(self) == _AloneVar:
            if len(other) == _AloneVar:
                return _AloneVar
            else:
                return len(other)
        else:
            if len(other) == _AloneVar:
                return len(self)
            else:
                if len(self) == len(other):
                    return len(self)
                else:
                    raise TypeError('Wrong length of arguments')

    def _binary_function(self, other, func):
        if isinstance(other, AbstractVar):
            new_story = func(self.story, other.story)
            return AbstractVar(new_story, self._for_binary_operation_check_len(other))
        else:
            new_story = func(self.story, other)
            return AbstractVar(new_story, len(self))

    def __add__(self, other):
        return self._binary_function(other, lambda x, y: x + y)

    def __sub__(self, other):
        return self._binary_function(other, lambda x, y: x - y)

    def __mul__(self, other):
        return self._binary_function(other, lambda x, y: x * y)

    def __rmul__(self, other):
        return self._binary_function(other, lambda x, y: y * x)

    def __truediv__(self, other):
        return self._binary_function(other, lambda x, y: x / y)

    def __pow__(self, power):
        return self._binary_function(power, lambda x, y: x ** y)

    def __eq__(self, other):
        return self.story == other.story

    def __pos__(self):
        return self

    def __neg__(self):
        return AbstractVar(-self.story, self.len)

    def __abs__(self):
        return AbstractVar(self.story.__abs__(), self.len)


class Var(AbstractVar):
    def __init__(self, value, error, name: str = None):
        """
        Если вы создаёте перменную, характеризующую серию измерений:
            value и error должны быть одной длины. Внутри далее они будут приведены к np.array.
        Если хотите создать одиночную переменную:
            value и error должны быть числами.
        name нужен только если вы хотите смотреть поле story в AbstractVar (подробнее там же).
        """
        if hasattr(value, '__iter__') or hasattr(error, '__iter__'):
            # Maybe it's Multi Var
            if hasattr(value, '__iter__') and hasattr(error, '__iter__') and len(value) == len(error):
                # It's Multi Var
                if len(value) == 0:
                    raise TypeError('Good guys never make empty data')
                self.value = np.array(value)
                self.error = np.array(error)
                if name is None:
                    name = 'Var' + str(id(self))
                if name is 'Author':
                    name = 'NougmanovBoulat'
                symbol = sp.symbols(name)
                super().__init__(symbol, len(value))
            else:
                if hasattr(value, '__iter__') and hasattr(error, '__iter__'):
                    raise TypeError('Wrong length of arguments')
                else:
                    raise TypeError('One of arguments is iterable and the other has no this attribute')
        else:
            # It's Alone Var
            self.value = value
            self.error = error
            if name is None:
                name = 'Var' + str(id(self))
            if name is 'Author':
                name = 'NougmanovBoulat'
            symbol = sp.symbols(name)
            super().__init__(sp.symbols(name), _AloneVar)
        _DictSymVar.update({symbol: self})

    def val(self):
        return self.value

    def err(self):
        return self.error


class GroupVar:
    def __init__(self, *args):
        """
        Бывало у вас такое, что снимали несколько серий данных просто при разных температурах, например?
        Формулы для всех серий одинаковые, поэтому в библиотеку нужно забивать все серии по отдельности...
        А вот и не надо!
        Если есть x1, x2, x3, которые идиентичны по своей природе, просто создайте GroupVar(x1, x2, x3) или
        GroupVar((x1, x2, x3,)) и работайте с ним как с обычной переменной.
        val() и err(), будут соответственно возвращать массивы вида (x1.val(), x2.val(), x3.val(),).
        Обратиться к переменным GroupVar можно по отдельности через поле vars.
        """
        if len(args) == 1 and isinstance(args[0], GroupVar):
            self.vars = args[0].vars
        if len(args) == 1 and hasattr(args[0], '__iter__()'):
            self.vars = [i for i in args[0]]
        elif isinstance(args[0], GroupVar):
            self.vars = args[0].vars
        else:
            self.vars = args

    def __getitem__(self, item: int):
        return self.vars[item]

    def __iter__(self):
        return iter(self.vars)

    def _method_for_group(self, method, *args, **kwargs):
        return tuple(getattr(var, method)(*args, **kwargs) for var in self)

    def val(self):
        args = tuple(self.vars[0].story.free_symbols)
        _func = sp.lambdify((args,), self.vars[0].story, 'numpy')
        return self._method_for_group('_val', args, _func)

    def err(self):
        args = tuple(self[0].story.free_symbols)
        _partial_diffs = tuple(sp.lambdify((args,), self[0].story.diff(sym), 'numpy') for sym in args)
        return self._method_for_group('_err', args, _partial_diffs)

    def __len__(self):
        return len(self.vars)

    def __str__(self):
        return str(self._method_for_group('__str__'))

    def _binary_function(self, other, func):
        if isinstance(other, GroupVar):
            return GroupVar(*tuple(func(self[i], other[i]) for i in range(len(self))))
        else:
            return GroupVar(*tuple(func(self[i], other) for i in range(len(self))))

    def __add__(self, other):
        return self._binary_function(other, lambda x, y: x + y)

    def __sub__(self, other):
        return self._binary_function(other, lambda x, y: x - y)

    def __mul__(self, other):
        return self._binary_function(other, lambda x, y: x * y)

    def __rmul__(self, other):
        return self._binary_function(other, lambda x, y: y * x)

    def __truediv__(self, other):
        return self._binary_function(other, lambda x, y: x / y)

    def __pow__(self, power):
        return self._binary_function(power, lambda x, y: x ** y)

    def __eq__(self, other):
        return self[0].story == other[0].story

    def __pos__(self):
        return self

    def __neg__(self):
        return GroupVar(*tuple(-v for v in self))
