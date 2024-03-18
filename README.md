# Karpov_courses. Курс StartML.
___
## Финальный проект. Построение рекомендательной системы для социальной сети Karpov Courses.
Представим, что у нас есть социальная сеть для студентов Karpov Courses, которая обладает следующим функционалом:
можно отправлять друг другу письма, создавать сообщества, аналогичные группам в известных сетях, и в этих сообществах публиковать посты.
Из приятного – при регистрации студенты должны заполнять данные по своему профилю, которые хранятся в поднятой на наших мощностях postgres database.
Так же наша платформа обладает лентой, которую пользователи могут листать и просматривать случайные записи случайных сообществ.
Если пост нравится, можно поддержать автора и поставить like.
Все действия пользователей сохраняются, каждая их активность, связанная с просмотром постов, тоже записывается к нам в базу.
Платформа Karpov Courses заинтересована в благосостоянии студентов, поэтому разработчики решили усовершенствовать текущую ленту.
А что, если показывать пользователям не случайные посты, а рекомендовать их точечно каждому пользователю из всего имеющегося множества написанных постов?
Как это сделать и учесть индивидуальные характеристики профиля пользователя, его прошлую активность и содержимое самих постов?


В этом как раз в этом и состоит цель проекта – разработать такую рекомендательную систему для студентов, которая будет выдавать каждому пользователю только те посты, которые ему интересны.


С точки зрения разработки, на протяжении четырёх шагов реализовались сервисы, которые для каждого юзера в любой момент времени возвращали рекомендованные посты.


## Использованы библиотеки:
* fastapi
* uvicorn
* sqlalchemy
* psycopg2
* pandas
* numpy
* matplotlib
* seaborn
* pytorch
* catboost
## Шаги для достижения цели:
* Шаг 1 (unit_01).
В этой части разрабатывался сервис, который возвращает топ ```limit``` постов по количеству лайков.
* Шаг 2 (unit_02).
В этой части курса был разработан сервис по рекомендации постов на основе алгоритмов классического машинного обучения.
* Шаг 3 (unit_03).
В этом блоке при построении сервиса по рекомендации использовались нейронная сеть.
При помощи нейронной сети были выполнены эмбеддинги постов, затем для рекомендации применились алгоритмы классического машинного обучения.
* Шаг 4 (unit_04).
Задачей этой части курса было построения сервиса для проведения A/B эксперимента по рекомендациям постов моделью из unit_02 и моделью из unit_03.
По user_id каждый пользователь переходил, либо в контрольную, либо в тестовую группу.
В контрольной для рекомендаций постов применялась модель из unit_02, в тестовой - модель из unit_03.
