import tkinter as _tk


class _Printer:
    def __init__(self):
        self.root = None
        self.printable = list()

    def __del__(self):
        if len(self.printable) != 0:
            for i, s in enumerate(self.printable):
                text = _tk.Text(width=25, height=5, wrap=_tk.WORD)
                text.insert(float(i), s)
                text.pack()
            self.root.mainloop()


_p = _Printer()


def printLC(string: str) -> None:
    """
    После выполнения программы выведет всё, что вы хотели напечатать
    """
    if _p.root is None:
        _p.root = _tk.Tk()
    _p.printable.append(string)


def get_started():
    return """--Что такое Var?
Это класс, который характеризует ваши прямые измерения. У него есть поля value и error, которые заполняются при 
инициализации. Это могут быть как массивы данных (серия измерений), так и числа (константы в течение эксперимента). 
--Что будет, если сложить два Var?
Этим действием вы создаёте косвенную переменную - объект класса AbstractVar. Не советуется создавать экземпляры этого 
класса посредством инициализации. У AbstractVar есть полезные методы val() и err().
--Что можно делать с переменными?
В библиотеке есть все элементарные функции с названиями, наиболее распространёнными в русскоязычных учебниках. Есть 
также mean(x).

--Хочу строить график, что делать?
Для нанесения точек с погрешностями воспользуйтесь функцией plot(x,y). Для построения прямой вида kx+b - line(k,b)
Кроме того, есть функция mnk(x,y), которая возвращает (k,b,) (type (k), type(b) is Var, Var) и автоматически добавляет 
прямую на график. Если хотите взглянуть на сам график - вызовите show(). 

--Обычно данные находятся в Exel, а не в python. Можно ли их подружить?
Копируете область в Exel, вставляете как строку в XL_to_table - получаете питоновский список списков. 
--Exel с python дружит, но взаимно ли это?
Да, есть функция table_to_XL. 
--А с TeX дружите?
Да. Функция tex_table принимает на вход кортежи из заголовка (ex: 'C, \\frac{Дж}{К}') и переменной 
(ex: Var([9]*8, [1]*8)) и выдаёт прекрасную Tex таблицу в виде string. В таблице будет отдельные колонки под значение и
 погрешность. Но если погрешность не важна - в кортеж соответствующей переменной добавьте в конце False. 
--Из консоли python неудобно выделять длинное описание таблицы...
Именно для вас у библиотеки есть собственный аналог print - printLC. После выполнения программы вылезет окошко с 
текстом, из которого удобно делать Ctrl+A.
--Есть более подробная документация?
Никто не запрещает Ctrl+B на незнакомые функции. Посмотрите также GroupVar и rus_tex_formula
"""
