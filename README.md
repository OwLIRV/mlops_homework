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

***HW-2 — Тренування моделей та трекінг експериментів***

Було реалізовано процес тренування моделі машинного навчання для класифікації текстових відгуків. Для навчання використано розмічений датасет, підготовлений у HW-1.

Використаний датасет

Для тренування використано датасет:

data/labeled/reviews_labeled_v2.json

Датасет містить 70 розмічених текстових прикладів з такими класами:

positive
negative
neutral
Обрана модель

Для навчання використано базову модель для класифікації тексту:

TF-IDF Vectorizer + Logistic Regression

TF-IDF перетворює текстові відгуки у числові ознаки, після чого Logistic Regression виконує класифікацію за тональністю.

Використані інструменти

У роботі використано такі інструменти:

Python — для реалізації процесу тренування;
scikit-learn — для побудови моделі машинного навчання;
MLflow Tracking — для трекінгу експериментів;
MLflow Model Registry — для збереження версій моделей;
matplotlib — для побудови confusion matrix;
joblib — для локального збереження моделі.

Структура проєкту

mlops_homework/
│
├── data/
│   └── labeled/
│       └── reviews_labeled_v2.json
│
├── src/
│   └── train.py
│
├── models/
│   └── sentiment_model.joblib
│
├── reports/
│   ├── classification_report.txt
│   └── confusion_matrix.png
│
├── requirements.txt
├── README.md
└── .gitignore

**Встановлення залежностей**

Для запуску проєкту потрібно створити віртуальне середовище:

python -m venv .venv

Активувати його:

.venv\Scripts\activate

Встановити залежності:

pip install -r requirements.txt

**Запуск MLflow**

Для запуску MLflow Tracking UI використовується команда:

mlflow ui --host 127.0.0.1 --port 5000

Після запуску MLflow доступний у браузері за адресою:

http://localhost:5000

або:

http://127.0.0.1:5000

Експеримент у MLflow має назву:

sentiment-classification-training

***Локальне посилання на експеримент:***

http://127.0.0.1:5000/#/experiments/1

MLflow запущено локально, тому посилання працює після запуску MLflow server на комп’ютері.

**Запуск тренування моделі**

Основний скрипт тренування знаходиться у файлі:

src/train.py

python src/train.py --data-path data/labeled/reviews_labeled_v2.json --max-features 3000 --ngram-max 2 --c 10.0 --test-size 0.3 --random-state 21

Було виконано кілька запусків моделі з різними гіперпараметрами:
python src/train.py --data-path data/labeled/reviews_labeled_v2.json --max-features 500 --ngram-max 1 --c 0.5
python src/train.py --data-path data/labeled/reviews_labeled_v2.json --max-features 1000 --ngram-max 1 --c 1.0
python src/train.py --data-path data/labeled/reviews_labeled_v2.json --max-features 2000 --ngram-max 2 --c 2.0
python src/train.py --data-path data/labeled/reviews_labeled_v2.json --max-features 300 --ngram-max 1 --c 0.1 --test-size 0.3 --random-state 7
python src/train.py --data-path data/labeled/reviews_labeled_v2.json --max-features 3000 --ngram-max 2 --c 10.0 --test-size 0.3 --random-state 21

Під час кожного запуску в MLflow логуються:

назва моделі;
шлях до датасету;
розмір датасету;
max_features;
ngram_range;
C;
test_size;
random_state;
accuracy;
f1_weighted;
precision_weighted;
recall_weighted;
classification_report.txt;
confusion_matrix.png;
навчена модель.
Результати експериментів

Найкращий запуск мав такі параметри:

max_features: 3000
ngram_range: 1-2
C: 10.0
test_size: 0.3
random_state: 21

Отримані метрики:
Accuracy: 0.4762
F1 weighted: 0.4815
Precision weighted: 0.5212
Recall weighted: 0.4762

Оскільки датасет є невеликим і містить 70 розмічених прикладів, метрики можуть бути нестабільними. Основна мета цього етапу — налаштувати процес тренування моделі, трекінг експериментів та збереження версій моделей.

**Model Registry**

Навчена модель збережена у MLflow Model Registry під назвою:

ukrainian-review-sentiment-model

Після кожного запуску тренування створюється нова версія моделі. У результаті було створено кілька версій моделі: v1, v2, v3, v4, v5, v6

Остання та найкраща версія моделі: ukrainian-review-sentiment-model v6

URI моделі для використання в наступному домашньому завданні: models:/ukrainian-review-sentiment-model/6