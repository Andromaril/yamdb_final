# yamdb_final
![yamdb_workflow](https://github.com/Andromaril/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
<h2>Описание проекта:</h2>
 Проект YaMDb собирает отзывы (Review) пользователей на произведения (Titles). 
 
 Произведения делятся на категории: «Книги», «Фильмы», «Музыка». Список категорий (Category) может быть расширен администратором (например, можно добавить категорию «Изобразительное искусство» или «Ювелирка»).

Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.
 
В каждой категории есть произведения: книги, фильмы или музыка. Например, в категории «Книги» могут быть произведения «Винни-Пух и все-все-все» и «Марсианские хроники», а в категории «Музыка» — песня «Давеча» группы «Насекомые» и вторая сюита Баха.

Произведению может быть присвоен жанр (Genre) из списка предустановленных (например, «Сказка», «Рок» или «Артхаус»). Новые жанры может создавать только администратор.

Благодарные или возмущённые пользователи оставляют к произведениям текстовые отзывы (Review) и ставят произведению оценку в диапазоне от одного до десяти (целое число); из пользовательских оценок формируется усреднённая оценка произведения — рейтинг (целое число). На одно произведение пользователь может оставить только один отзыв
 
<h2>шаблон наполнения env-файла</h2>

```
DB_ENGINE= # указываем, что работаем с postgresql

DB_NAME= # имя базы данных

POSTGRES_USER= # логин для подключения к базе данных

POSTGRES_PASSWORD= # пароль для подключения к БД (установите свой)

DB_HOST= # название сервиса (контейнера)

DB_PORT= # порт для подключения к БД 
```

<h2>Как запустить проект</h2>
Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Andromaril/yamdb_final.git

Запустить docker-compose и собрать контейнеры  командой  
docker-compose up -d --build
```

Теперь в контейнере web нужно выполнить миграции, создать суперпользователя.

<h3>Выполните по очереди команды:</h3>

```
docker-compose exec web python manage.py migrate 

docker-compose exec web python manage.py createsuperuser
```

<h3>Oписание команды для заполнения базы данными.</h3>

```
sudo docker-compose exec web python manage.py loaddata fixtures.json
```

<h3>Для того, чтобы выключить контейнер, используйте команду</h3>

```
docker-compose down
```
