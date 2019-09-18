import matplotlib.patches as _mp
import matplotlib.pyplot as plt
from lab_chit.var_class import *
from lab_chit.mono_funcs import mean

_lines = []


def plot(x: AbstractVar, y: AbstractVar, use_brand_new_fig=False, capsize=3, s=1, c=None, marker=None) -> None:
    """
    :param capsize: Размер шляпок на крестах ошибок
    :param s: Размер точек на графике
    :param c: Цвет точек
    :param marker: Форма точек (треугольнички, крестики...)
    Более о допустимых значениях параметров в документации matplotlib
    """
    if (use_brand_new_fig is False) and (plt.gcf() is None) or use_brand_new_fig is True:
        plt.figure()
    axes = plt.gca()
    axes.scatter(x.val(), y.val(), s=s, c=c, marker=marker)
    axes.errorbar(x.val(), y.val(), x.err(), y.err(), capsize=capsize, capthick=1, fmt='none', c=c)


# Сейчас вы увидите очень русскую функцию. Она выполнена в русском стиле и имеет русское название


# style_dermo = 'classic_dermo'
# style_better_dermo = 'at_least_better_dermo'


def mnk(x: AbstractVar, y: AbstractVar, style: str = 'classic_dermo', add_to_fig: bool = True, c=None, ls=None, not_all=(None, None,)):
    """
    Эта функция создаёт объекты типа Var неявно! Будьте осторожны.
    С x и y всё понятно.
    :param style: К сожалению на данный момент в библиотеке существует лишь classic dermo. Почему такое название?
    Потому что это просто классика, никак не оправданная с точки зрения статистики. Даже если предположить, что все
    ошибки действительно распределены нормально, вообще-то есть ошибки по x, поэтому модель линейной регрессии может
    даже приблизительно не работать. И даже если ошибки по x малы, вообще-то ошибки по y могут различаться между собой!
    Поэтому это даже не принцип наибольшего правдоподобия. (Видел формулу, где y входит с разными весами, но не нашёл к
    ней погрешности. Если найдёте, напишите, пожалуйста об этом https://vk.com/boulatn - добавим at least better dermo.)
    :param add_to_fig: Ну мало ли - параметры прямой хотите, а рисовать фигуру не хотите
    Параметры c (color) и ls (linestyle) для параметров рисования прямой. Допустимые значения есть в библиотеке
    matplotlib.
    """
    if style is 'classic_dermo':
        # y == kx + b
        if not_all[0] is None:
            if not_all[1] is None:
                X = x.val()
                Y = y.val()
            else:
                X = x.val()[:not_all[1]]
                Y = y.val()[:not_all[1]]
        else:
            if not_all[1] is None:
                X = x.val()[not_all[0]:]
                Y = y.val()[not_all[0]:]
            else:
                X = x.val()[not_all[0]:not_all[1]]
                Y = y.val()[not_all[0]:not_all[1]]
        k = (np.mean(X * Y) - np.mean(X) * np.mean(Y)) / (np.mean(X ** 2) - np.mean(X) ** 2)
        b = np.mean(Y) - k * np.mean(X)
        Sy = sum((Y - b - k * X) ** 2) / (len(X) - 2)
        D = len(X) * sum(X ** 2) - (sum(X)) ** 2
        dk = np.sqrt(Sy * len(X) / D)
        db = np.sqrt(Sy * sum(X ** 2) / D)
        if add_to_fig:
            line(k, b, c, ls)
        return Var(k, dk), Var(b, db)
    elif style is 'at_least_better_dermo':
        ...
    else:
        raise TypeError('Ишь чего захотел!')

def mnk_through0(x:AbstractVar, y:AbstractVar,add_to_fig: bool = True, c=None, ls=None):
    k = mean(y/x)
    if add_to_fig:
        line(k.value, 0, c, ls)
        return k


def line(k, b, c=None, ls=None, use_brand_new_fig=False):
    """
    Строит прямую вида kx+b
    Параметры c (color) и ls (linestyle) для параметров рисования прямой. Допустимые значения есть в библиотеке
    matplotlib.
    """
    if (use_brand_new_fig is False) and (plt.gcf() is None) or use_brand_new_fig is True:
        plt.figure()
    _lines.append((k, b, c, ls,))

def get_lines():
    """
    Список всех линий, которые будут нанесены на график.
    """
    return _lines


def show(fix_ax=True, hline_in0=True, vline_in0=True, xlabel='', ylabel='', title='', tex_style=True,
         label_near_arrow=True):
    """
    :param fix_ax: Фиксирует оси так, чтобы были видны все точки, но не обязательно все линии.
    :param hline_in0: Рисует прямую x=0
    :param vline_in0: Рисует прямую y=0
    :param xlabel: guess yourself
    :param ylabel: guess yourself
    :param title: guess yourself
    :param tex_style: С этим параметром ваши подписи к графику будут в формате tex. ($...$ не нужны).
    :param label_near_arrow: Делает так, чтобы подписи к осям были не по серединкам, а рядом с соответсвующими стрелками
    """
    ax = plt.gca()
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    if label_near_arrow:
        ylabel_prop = dict(rotation=0, y=1)
        ax.xaxis.set_label_coords(1.06, -0.02)
    else:
        ylabel_prop = {}
    if title.rstrip() is not '' and tex_style:
        plt.title('$' + title + '$')
    else:
        plt.title(title)

    if xlabel.rstrip() is not '' and tex_style:
        ax.set_xlabel('$' + xlabel + '$')
    else:
        ax.set_xlabel(xlabel)
    if ylabel.rstrip() is not '' and tex_style:
        ax.set_ylabel('$' + ylabel + '$', ylabel_prop)
    else:
        ax.set_ylabel(ylabel, ylabel_prop)
    ax.grid(axis='both', which='major', linestyle='--', linewidth=1)
    ax.grid(axis='both', which='minor', linestyle='--', linewidth=0.5)
    ax.minorticks_on()
    if fix_ax:
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
    if hline_in0 is True:
        ax.hlines(0, xmin, xmax, linewidth=0.5)
    if vline_in0 is True:
        ax.vlines(0, ymin, ymax, linewidth=0.5)
    global _lines
    for k, b, c, ls in _lines:
        points = []
        if ymin <= k * xmin + b <= ymax:
            points.append((xmin, k * xmin + b,))
        if ymin <= k * xmax + b <= ymax:
            points.append((xmax, k * xmax + b,))
        if len(points) < 2 and xmin * k < ymax - b < xmax * k:
            points.append(((ymax - b) / k, ymax,))
        if len(points) < 2 and xmin * k < ymin - b < xmax * k:
            points.append(((ymin - b) / k, ymin,))
        plt.plot((points[0][0], points[1][0],), (points[0][1], points[1][1],), c=c, ls=ls)
    _lines = []

    ax.annotate('', xy=(1.05, 0), xycoords='axes fraction', xytext=(-0.03, 0),
                arrowprops=dict(arrowstyle=_mp.ArrowStyle.CurveB(head_length=1), color='black'))
    ax.annotate('', xy=(0, 1.06), xycoords='axes fraction', xytext=(0, -0.03),
                arrowprops=dict(arrowstyle=_mp.ArrowStyle.CurveB(head_length=1), color='black'))
    plt.show()
