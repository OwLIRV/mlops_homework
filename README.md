Homework 1 — Робота з даними в MLOps

Опис проєкту
У межах домашньої роботи було налаштовано процес роботи з даними для MLOps-проєкту: створено датасет, виконано ручну розмітку, 
організовано версіонування датасету та збереження даних у S3-сумісному сховищі.

Для роботи було використано датасет коротких українських текстових відгуків користувачів. Дані розмічалися за трьома класами:

positive
negative
neutral

Структура проєкту:

mlops_homework/
│
├── data/
│   ├── raw/
│   │   ├── reviews.csv
│   │   └── reviews_v2_new.csv
│   │
│   └── labeled/
│       ├── reviews_labeled_v1.json
│       └── reviews_labeled_v2.json
│
├── configs/
├── reports/
├── .dvc/
├── .gitignore
└── README.md

***Який інструмент використано для розмітки***
Для розмітки даних використано Label Studio.

У Label Studio було створено проєкт:

Sentiment Dataset Labeling

До проєкту було імпортовано CSV-файл з текстовими відгуками:

data/raw/reviews.csv

Кожен відгук розмічався вручну за одним із трьох класів:

positive
negative
neutral

Для розмітки використовувався такий інтерфейс Label Studio:

<View>
  <Text name="review" value="$text"/>
  <Choices name="sentiment" toName="review" choice="single">
    <Choice value="positive"/>
    <Choice value="negative"/>
    <Choice value="neutral"/>
  </Choices>
</View>

***Як запустити\відкрити розмітку***

Label Studio запускається локально командою:

label-studio start

Після запуску інтерфейс відкривається у браузері за адресою:

http://localhost:8080

Щоб переглянути розмітку, потрібно:

Відкрити Label Studio.
Перейти до проєкту Sentiment Dataset Labeling.
Відкрити список завдань.
Переглянути розмічені приклади або експортувати результати розмітки.

Експортовані результати розмітки збережені у папці:

data/labeled/

У проєкті є дві версії розміченого датасету:

data/labeled/reviews_labeled_v1.json
data/labeled/reviews_labeled_v2.json
Як працює версіонування датасету

***Для версіонування датасету використано DVC.***

Спочатку було ініціалізовано Git та DVC:

git init
dvc init

Після цього файли датасету були додані до DVC:

dvc add data/raw/reviews.csv
dvc add data/raw/reviews_v2_new.csv
dvc add data/labeled/reviews_labeled_v1.json
dvc add data/labeled/reviews_labeled_v2.json

DVC створює спеціальні .dvc-файли, які відстежуються через Git. Самі дані зберігаються не в Git, а у віддаленому сховищі.

Для зберігання датасету використано S3-сумісне сховище MinIO.

MinIO відкривається локально за адресою:

http://localhost:9001

Назва bucket:

mlops-dataset

DVC remote було налаштовано командою:

dvc remote add -d minio s3://mlops-dataset
dvc remote modify minio endpointurl http://localhost:9000

Після цього дані були завантажені у MinIO командою:

dvc push

У результаті датасет має дві версії:

v1 — reviews_labeled_v1.json
v2 — reviews_labeled_v2.json

Таким чином, у проєкті простежується лінія даних:
Оригінальні дані → Розмітка в Label Studio → Експорт розмітки → Версіонування через DVC → Збереження у MinIO

***Для яких задач ці дані планується використовувати надалі***

Ці дані планується використовувати для задачі класифікації тональності тексту.
Модель машинного навчання має визначати, чи є короткий текстовий відгук:

positive
negative
neutral

Приклад:

Вхідний текст: "Доставка тривала занадто довго"
Очікуваний клас: negative
