# hhkeys (бот @hhkeys_bot для парсинга Keywords с сайта hh.ru)
Телеграм бот для парсинга hh.ru по ключевым навыкам.

1. Принимает ключевое слово для поиска, количество страниц для поиска, 
количество ключевых навыков для вывода результата.

2. Парсит страницы с использованием aiohttp библиотеки.

3. Обрабатывает собранные навыки с использованием библиотек pandas и numpy.

4. Выводит результат в виде .png картинки с графиком matplotlib.axes.Axes.pie,
на котором указаны топ-N ключевых навыков и число их повторений, согласно собранным вакансиям.
