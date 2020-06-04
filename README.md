# Кэширующий DNS сервер

Сервер, используя сокеты, прослушивает 53 порт. При первом запуске кэш пустой. Сервер получает от клиента рекурсивный запрос и выполняет разрешение запроса. Если информации по запросу в кэше нет, то он использует Яндекс.DNS и находит сначала авторитетный сервер для интересующей нас доменной зоны, потом его IP адрес и делает запрос ANY. Получив ответ, сервер разбирает пакет ответа. Полученная информация сохраняется в кэше сервера. Сервер регулярно просматривает кэш и удаляет просроченные записи. Во время штатного выключения сервер сериализует данные из кэша и сохраняет их на диск. При повторных запусках сервер считывает данные с диска и удаляет просроченные записи. 

#### С примерами запуска можно ознакомиться в файле example.txt
# Примеры выполнения программы: 
#### https://www.notion.so/DNS-0b65c50d4c58484fb404c85cc199c6a9

Выполнила Ильина Анна (группа КН-202)
