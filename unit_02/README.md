# Unit_02 Модуль "Машинное обучение и приложения".  
Рекомендательная система постов для конкретного пользователя с определённым id. Рекомендации делаются на основе алгоритмов классического машинного обучения. Система выполнена ввиде веб-сервиса. Содержит один endpoint:  
* `@app.get("/post/recommendations/", response_model=List[PostGet])`  
`def recommended_posts(id: int, time: datetime, limit: int = 10) -> List[PostGet]:`  
Возвращает для пользователя с id, для даты-времени time, limit рекомендованных постов.  
Пример запроса:  
`http://имя_сервера/post/recommendations/?id=200&time=2020-10-20T14:00&limit=5`  

### Описание файлов.  
* ___app_unit_02_github.py___  
Исходный код веб-сервиса.
* ___schema.py___  
Описание таблиц БД через библиотеку pydantic, для задания и проверки формата ответа endpoint веб-сервиса.
* ___catboost_model_6_github___  
Обученная модель CatBoostClassifier, которая предсказывает вероятность лайка поста пользователем.  
* ___karpov-final-unit-02-tables.ipynb___  
Ноутбук в котором осуществлялось выделение признаков и подготовка таблиц для обучения модели.
* ___karpov-final-unit-02-model.ipynb___  
В этом ноутбуке осуществлялось обучение, подбор параметров модели и по обученной модели, определение важности выделенных признаков.  

### Метрика оценки качества модели.
В чекере учебной системы Start ML качество алгоритма рекомендаций проверялось метрикой __Hitrate@5__:

$$\frac{1}{n*T}\sum_{t=1}^{T}\sum_{i=1}^{n}min(1,\sum_{j=1}^{5}[a_{j}(x_{i},t)=1])$$
где:  
n - количество юзеров;  
T - количество периодов проверки;  
$$a_{j}(x_{i},t)$$ j-ая рекомендация i-ому пользователю в момент времени.  
Она принимает значение 1, если среди предложенных 5 рекомендаций хотя бы 1 получила в итоге like от пользователя. Даже если все 5 предложенных постов в итоге будут оценены пользователем, все равно hitrate будет равен 1. Метрика бинарная. В противном случае, если ни один из предложенных постов не был оценен пользователем, hitrate  принимает значение 0.  
При проверке качества модели, в данной работе я использовал метрику Accuracy. Т.к. она интуитивно понятна - это доля правильно предсказанных ответов. Классы в выборке были сильно не сбалансированы, 90% значений с классом 0. Была сделана сбалансированная выборка с небольшим преобладанием класса 0. Выгрузка выборки находится в корне репозитария, в *\data\feed_data.csv*

#### Итоговый hitrate, разработанного алгоритма, в чекере учебной системы LMS, составляет 0.567.  
 

### Описание таблиц.  
В этой части используется БД аналогичная в unit_01, но имеет некоторые отличия: другие названия таблиц и предсказываемое поле target в таблице feed_data.  
#### Таблица user_data. 

Cодержит информацию о всех пользователях соц.сети.  
Аналогична таблице __user__ из unit_01.

#### Таблица post_text_df.  
Содержит информацию о постах и уникальный ID каждой единицы с соответствующим ей текстом и топиком.  Аналогична таблице __post__ в unit_01.  

#### Таблица feed_data.  
| Field name | Overview |
| --------------- | ------------------ |  
| timestamp | Время, когда был произведен просмотр |  
| user_id | id пользователя, который совершил просмотр |  
| post_id | id просмотренного поста |  
| action | Тип действия: просмотр или лайк |  
| target | 1 у просмотров, если почти сразу после просмотра был совершен лайк, иначе 0. У действий like пропущенное значение |