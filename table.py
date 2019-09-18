import decimal as _dc
from collections import Counter as _Counter
from string import printable as _printable
from sys import stdin as _stdin

_ArgumentError = TypeError(
    'tex_table function eat args which are (string, AbstractVar) or (string, AbstractVar, bool) or tuple '
    'of such objects.')  # Also it eats GroupVar and tuple of names for each??? <-Надо ли это?


def rus_tex_formula(formula: str) -> str:
    # Будьте аккуратны!
    # Данная чудо-функция неверно обрабатывает формулы, в которых русский используется для написания в
    # различных местах без английских символов между русскими блоками

    # Например:
    # Так_н е работает -> \text{Так}_\text{н е работает}
    # А_{так} работает -> \text{А}_{\text{так}} \text{работает}
    """
    К сожалению TeX не поддерживает русский язык в формулах. Для этого есть \text. Чтобы обращаться с русским так же,
    как и с ангийским в формулах, есть этот преобразватель. Правда работает он через пень колоду (см. комментарий выше)
    """
    ret = ''
    rus_now = False
    for chr in formula:
        if chr in ' ,.!?:;':
            ret += chr
        elif chr in _printable:
            if rus_now is True:
                ret += '}' + chr
                rus_now = False
            else:
                ret += chr
        else:
            if rus_now is True:
                ret += chr
            else:
                ret += '\\text{' + chr
                rus_now = True
    if rus_now is True: ret += '}'
    return ret


def tex_table(*args,
              caption: str = '', numerate: bool = True,
              colors=('C0C0C0', 'EFEFEF', 'C0C0C0',), color_frequency: int = 2,
              accuracy: float = 0.05, lab_fmt: bool = True):
    """
    Проще объяснить на примере
    Есть серии измерений теплоёмкости и температуры.
        T=Var(range(273,280), [1]*7)
        C=Var([9]*7, [0.1]*7)
    T измеряется в К, а С в Дж/К
    :param args: ('T, К', T), ('С, Дж/К', C)
    или (('T, К', T), ('С, Дж/К', C),)
    Сгенерируется таблица со значениями и погрешностями. Будут столбцы: 'T, К', '\Delta T, К', 'С, Дж/К', '\Delta С, Дж/К'
    Но если вам, например, не захотелось отображать погрешность T, то args должно иметь вид:
    ('T, К', T, False), ('С, Дж/К', C)
    :param caption: guess yourself
    :param numerate: Вводит нумерацию строчек
    :param colors: Таблица имеет разные цвета: цвет заголовков, цвет чередования, цвет столбца нумепрации.
    В формате цветов HTML можно менять их.
    :param color_frequency: Частота чередования
    :param accuracy: Точность, с которой отображается ошибка
    :param lab_fmt: Выносит степени 10 в заголовок
    """

    # This func should check: Do this arg should present error in table or not?
    def ch_err(arg):
        return (len(arg) == 2) or arg[2] is True

    if hasattr(args[0], '__getitem__') and not hasattr(args[0][0], 'split'):
        args = args[0]
    try:
        height = args[0][1].__len__()
    except Exception:
        raise _ArgumentError
    table = list()
    if numerate:
        table.append([''] + list(map(str, range(1, height + 1))))
        NCol = 0  # Номер текущей колонки
    else:
        NCol = -1  # Номер текущей колонки

    for arg in args:
        if len(arg[1]) is not height:
            raise TypeError('Wrong length of arguments')
        NCol += 1

        if lab_fmt is True:
            if ch_err(arg):
                # table.append(['$' + rus_tex_formula(arg[0]) + '$'])
                val = tuple(map(lambda x: _dc.Decimal(str(x)), arg[1].val()))
                err = tuple(map(lambda x: _dc.Decimal(str(x)), arg[1].err()))
                most_common_exp = _Counter(_get_eng_exp(v) for v in val).most_common(1)[0][0]
                if most_common_exp != 0:
                    # Наличие ',' значит поставил ли пользователь размерность или это безразмерное число
                    if ',' in arg[0]:
                        table.append(['$' + rus_tex_formula(arg[0]) + '\\cdot 10^{' + str(most_common_exp) + '} $'])
                    else:
                        table.append(['$' + rus_tex_formula(arg[0]) + '\\cdot 10^{' + str(-most_common_exp) + '} $'])
                else:
                    table.append(['$' + rus_tex_formula(arg[0]) + '$'])
                Arr_of_val = list()
                Arr_of_err = list()
                for i in range(height):
                    Rval, Rerr = _lab_decimal_style(val[i], err[i], accuracy=accuracy)
                    Arr_of_val += [str(float(Rval.scaleb(-most_common_exp)))]
                    Arr_of_err += [str(float(Rerr.scaleb(-most_common_exp)))]
                table[NCol] += Arr_of_val
                if most_common_exp != 0:
                    # Наличие ',' значит поставил ли пользователь размерность или это безразмерное число
                    if ',' in arg[0]:
                        table.append(
                            ['$' + '\\Delta ' + rus_tex_formula(arg[0]) + '\\cdot 10^{' + str(most_common_exp) + '} $'])
                    else:
                        table.append(['$' + '\\Delta ' + rus_tex_formula(arg[0]) + '\\cdot 10^{' + str(
                            -most_common_exp) + '} $'])
                else:
                    table.append(['$' + '\\Delta ' + rus_tex_formula(arg[0]) + '$'])
                NCol += 1
                table[NCol] += Arr_of_err

            #     q = tuple(map(str, tuple(zip(*(lab_decimal_style(val[i], err[i], accuracy) for i in range(height))))))
            #
            #     table[NCol] += list(q[0])
            #     table.append(['$' + '\\Delta ' + rus_tex_formula(arg[0]) + '$'])
            #     table[NCol + 1] += list(q[1])
            #     NCol += 1
            else:
                # table.append(['$' + rus_tex_formula(arg[0]) + '$'])
                ...
        else:
            table.append(['$' + rus_tex_formula(arg[0]) + '$'])
            if ch_err(arg):
                table[NCol] += tuple(map(str, arg[1].val()))
                NCol += 1
                table[NCol] += tuple(map(str, arg[1].err()))
            else:
                table[NCol] += list(map(str, arg[1].val()))
    NCol += 1  # Отныне это число колонок без учёта нумерации (самая левая колонка)

    ret = '\\begin{table}[h]' + '\n' + '\\center' + '\n'
    if caption is None or False:
        pass
    else:
        ret += '\\caption{' + caption + '}' + '\n'
    ret += '\\begin{tabular}{' + len(table) * '|c' + '|}' + '\n' + '\\hline' + '\n' + \
           '\\rowcolor[HTML]{' + colors[0] + '}' + '\n'

    for str_num in range(height + 1):
        if str_num % color_frequency == 0 and str_num != 0:
            ret += '\\rowcolor[HTML]{' + colors[1] + '} \n'
        if numerate and str_num != 0:
            ret += '\\cellcolor[HTML]{' + colors[2] + '} '
        for col_num in range(NCol):
            ret += table[col_num][str_num] + ' & '
        ret = ret[:-2] + '\\\\ \\hline' + '\n'
    ret += '\\end{tabular}' + '\n' + '\\end{table}' + '\n'
    return ret


def _get_eng_exp(x):
    return divmod(int(x.logb()), 3)[0] * 3


def _lab_decimal_style(val, err, accuracy=0.05):
    if err!=0:
        Rerr = err.quantize(_dc.Decimal('1').scaleb(_dc.Decimal(str(_dc.Decimal(accuracy) * err)).logb()),
                            rounding=_dc.ROUND_HALF_UP)
        Rval = val.quantize(Rerr,
                            rounding=_dc.ROUND_HALF_UP)
        return Rval, Rerr
    else:
        if val!=0:
            Rval = val.quantize(_dc.Decimal('1').scaleb(_dc.Decimal(str(_dc.Decimal(accuracy) * val)).logb()),
                                rounding=_dc.ROUND_HALF_UP)
            return Rval, _dc.Decimal(0)
        else:
            return _dc.Decimal(0), _dc.Decimal(0)

def XL_to_table(text: str = None):
    """
    Вводишь копию ячеек из XL - получаешь питоновские списки списков.
    В случае отсутствия параметров, принимает то же самое, но не в качестве аргумента, а из stdin
    """
    if text is None:
        text = _stdin
        arr = text.readline().strip()
        table = list(list() for i in range(len(arr)))
        while arr != '':
            arr = list(map(float, (arr.split('\t'))))
            for i in range(len(arr)):
                table[i].append(arr[i])
            arr = text.readline().rstrip()
            return table

    table = tuple(map(lambda x: tuple(map(float, x.split())), text.split('\n')))
    table = tuple(zip(*table[:-1]))
    return table


def table_to_XL(table, t=True):
    """
    Хочешь перевести питоновские списки списков в Exel? Тебе сюда.
    Выводит строку, которую можно вставить в Exel. (И получить ячейки)
    Если надо выодить данные в строку, в не в столбец - t=False.
    """
    ret = ''
    if t:
        table = tuple(zip(*table))
    if len(table) == 1 and not hasattr(table[0], '__iter__'):
        for cell in table:
            ret += str(cell) + '\n'
        return ret[:-1]
    for col in table:
        for cell in col:
            ret += str(cell) + '\t'
        ret += '\n'
    return ret[:-1]
