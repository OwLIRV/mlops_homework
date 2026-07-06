# MLOps Homework Project

## Опис проєкту

У цьому проєкті реалізовано повний базовий MLOps-процес для задачі класифікації тональності українських текстових відгуків.

Проєкт охоплює такі етапи:

* підготовка та розмітка датасету;
* версіонування даних;
* тренування моделі машинного навчання;
* трекінг експериментів;
* збереження моделі у Model Registry;
* розгортання сервісу інференсу;
* моніторинг роботи ML-сервісу;
* збір метрик через Prometheus;
* візуалізація метрик у Grafana;
* базовий аналіз drift за допомогою Evidently.

Модель класифікує короткі українські текстові відгуки за трьома класами:

* `positive`
* `negative`
* `neutral`

---

# HW-1 — Робота з даними в MLOps

## Мета роботи

У межах домашньої роботи 1 було налаштовано процес роботи з даними для MLOps-проєкту.

Було створено датасет коротких українських текстових відгуків, виконано ручну розмітку даних, організовано версіонування датасету та збереження даних у S3-сумісному сховищі.

---

## Що було реалізовано

У проєкті реалізовано:

* створення датасету з українськими текстовими відгуками;
* ручну розмітку даних у Label Studio;
* експорт розміченого датасету;
* збереження кількох версій розмічених даних;
* версіонування датасету за допомогою DVC;
* налаштування S3-сумісного сховища MinIO;
* завантаження даних у віддалене сховище.

---

## Використаний датасет

Для роботи було використано датасет коротких українських текстових відгуків користувачів.

Дані розмічалися за трьома класами:

* `positive`
* `negative`
* `neutral`

У проєкті є дві версії розміченого датасету:

* `data/labeled/reviews_labeled_v1.json`
* `data/labeled/reviews_labeled_v2.json`

---

## Структура проєкту для HW-1

mlops_homework/

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

---

## Інструмент для розмітки даних

Для розмітки даних використано Label Studio.

У Label Studio було створено проєкт:

`Sentiment Dataset Labeling`

До проєкту було імпортовано CSV-файл з текстовими відгуками:

`data/raw/reviews.csv`

Кожен відгук розмічався вручну за одним із трьох класів:

* `positive`
* `negative`
* `neutral`

---

## Інтерфейс розмітки в Label Studio

Для розмітки використовувався такий інтерфейс Label Studio:

<View>
  <Text name="review" value="$text"/>
  <Choices name="sentiment" toName="review" choice="single">
    <Choice value="positive"/>
    <Choice value="negative"/>
    <Choice value="neutral"/>
  </Choices>
</View>

---

## Запуск Label Studio

Label Studio запускається локально командою:

`label-studio start`

Після запуску інтерфейс відкривається у браузері за адресою:

`http://localhost:8080`

---

## Перегляд розмітки

Щоб переглянути розмітку, потрібно:

* відкрити Label Studio;
* перейти до проєкту `Sentiment Dataset Labeling`;
* відкрити список завдань;
* переглянути розмічені приклади;
* за потреби експортувати результати розмітки.

Експортовані результати розмітки збережені у папці:

`data/labeled/`

---

## Версіонування датасету

Для версіонування датасету використано DVC.

Спочатку було ініціалізовано Git та DVC:

`git init`

`dvc init`

Після цього файли датасету були додані до DVC:

`dvc add data/raw/reviews.csv`

`dvc add data/raw/reviews_v2_new.csv`

`dvc add data/labeled/reviews_labeled_v1.json`

`dvc add data/labeled/reviews_labeled_v2.json`

DVC створює спеціальні `.dvc`-файли, які відстежуються через Git. Самі великі файли з даними зберігаються не в Git, а у віддаленому сховищі.

---

## S3-сумісне сховище MinIO

Для зберігання датасету використано S3-сумісне сховище MinIO.

MinIO відкривається локально за адресою:

`http://localhost:9001`

Назва bucket:

`mlops-dataset`

DVC remote було налаштовано командами:

`dvc remote add -d minio s3://mlops-dataset`

`dvc remote modify minio endpointurl http://localhost:9000`

Після цього дані були завантажені у MinIO командою:

`dvc push`

---

## Результат HW-1

У результаті було підготовлено датасет для подальшого використання у MLOps-проєкті.

У проєкті простежується повна лінія роботи з даними:

Оригінальні дані → Розмітка в Label Studio → Експорт розмітки → Версіонування через DVC → Збереження у MinIO

Дані планується використовувати для задачі класифікації тональності тексту.

Приклад:

Вхідний текст:

`Доставка тривала занадто довго`

Очікуваний клас:

`negative`

---

# HW-2 — Тренування моделей та трекінг експериментів

## Мета роботи

У межах домашньої роботи 2 було реалізовано процес тренування моделі машинного навчання для класифікації українських текстових відгуків.

Для навчання використано розмічений датасет, підготовлений у HW-1.

---

## Що було реалізовано

У проєкті реалізовано:

* підготовку даних для тренування;
* тренування моделі класифікації тексту;
* запуск кількох експериментів з різними гіперпараметрами;
* трекінг експериментів у MLflow;
* логування метрик якості моделі;
* збереження classification report;
* побудову confusion matrix;
* збереження моделі локально;
* реєстрацію моделі у MLflow Model Registry.

---

## Використаний датасет

Для тренування використано датасет:

`data/labeled/reviews_labeled_v2.json`

Датасет містить 70 розмічених текстових прикладів з такими класами:

* `positive`
* `negative`
* `neutral`

---

## Обрана модель

Для навчання використано базову модель для класифікації тексту:

`TF-IDF Vectorizer + Logistic Regression`

TF-IDF перетворює текстові відгуки у числові ознаки, після чого Logistic Regression виконує класифікацію за тональністю.

---

## Використані інструменти

У роботі використано такі інструменти:

* Python — для реалізації процесу тренування;
* scikit-learn — для побудови моделі машинного навчання;
* MLflow Tracking — для трекінгу експериментів;
* MLflow Model Registry — для збереження версій моделей;
* matplotlib — для побудови confusion matrix;
* joblib — для локального збереження моделі.

---

## Структура проєкту для HW-2

mlops_homework/

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

---

## Встановлення залежностей

Для запуску проєкту потрібно створити віртуальне середовище:

`python -m venv .venv`

Активувати його:

`.venv\Scripts\activate`

Встановити залежності:

`pip install -r requirements.txt`

---

## Запуск MLflow

Для запуску MLflow Tracking UI використовується команда:

`mlflow ui --host 127.0.0.1 --port 5000`

Після запуску MLflow доступний у браузері за адресою:

`http://localhost:5000`

або:

`http://127.0.0.1:5000`

Експеримент у MLflow має назву:

`sentiment-classification-training`

Локальне посилання на експеримент:

`http://127.0.0.1:5000/#/experiments/1`

MLflow запущено локально, тому посилання працює після запуску MLflow server на комп’ютері.

---

## Запуск тренування моделі

Основний скрипт тренування знаходиться у файлі:

`src/train.py`

Основна команда запуску:

`python src/train.py --data-path data/labeled/reviews_labeled_v2.json --max-features 3000 --ngram-max 2 --c 10.0 --test-size 0.3 --random-state 21`

---

## Запуски експериментів

Було виконано кілька запусків моделі з різними гіперпараметрами:

`python src/train.py --data-path data/labeled/reviews_labeled_v2.json --max-features 500 --ngram-max 1 --c 0.5`

`python src/train.py --data-path data/labeled/reviews_labeled_v2.json --max-features 1000 --ngram-max 1 --c 1.0`

`python src/train.py --data-path data/labeled/reviews_labeled_v2.json --max-features 2000 --ngram-max 2 --c 2.0`

`python src/train.py --data-path data/labeled/reviews_labeled_v2.json --max-features 300 --ngram-max 1 --c 0.1 --test-size 0.3 --random-state 7`

`python src/train.py --data-path data/labeled/reviews_labeled_v2.json --max-features 3000 --ngram-max 2 --c 10.0 --test-size 0.3 --random-state 21`

---

## Логування в MLflow

Під час кожного запуску в MLflow логуються:

* назва моделі;
* шлях до датасету;
* розмір датасету;
* `max_features`;
* `ngram_range`;
* `C`;
* `test_size`;
* `random_state`;
* `accuracy`;
* `f1_weighted`;
* `precision_weighted`;
* `recall_weighted`;
* `classification_report.txt`;
* `confusion_matrix.png`;
* навчена модель.

---

## Результати експериментів

Найкращий запуск мав такі параметри:

* `max_features`: 3000
* `ngram_range`: 1-2
* `C`: 10.0
* `test_size`: 0.3
* `random_state`: 21

Отримані метрики:

* Accuracy: 0.4762
* F1 weighted: 0.4815
* Precision weighted: 0.5212
* Recall weighted: 0.4762

Оскільки датасет є невеликим і містить 70 розмічених прикладів, метрики можуть бути нестабільними.

Основна мета цього етапу — налаштувати процес тренування моделі, трекінг експериментів та збереження версій моделей.

---

## Model Registry

Навчена модель збережена у MLflow Model Registry під назвою:

`ukrainian-review-sentiment-model`

Після кожного запуску тренування створюється нова версія моделі.

У результаті було створено кілька версій моделі:

* v1
* v2
* v3
* v4
* v5
* v6

Остання та найкраща версія моделі:

`ukrainian-review-sentiment-model v6`

URI моделі для використання в наступному домашньому завданні:

`models:/ukrainian-review-sentiment-model/6`

---

## Результат HW-2

У результаті було реалізовано процес тренування ML-моделі для класифікації українських текстових відгуків.

Також було налаштовано MLflow Tracking для відстеження експериментів та MLflow Model Registry для збереження версій моделі.

---

# HW-3 — Інференс моделі

## Мета роботи

У межах домашньої роботи 3 було реалізовано сервіс інференсу моделі машинного навчання, навченої у HW-2.

Сервіс дозволяє передавати текстові приклади через REST API та отримувати передбачення моделі.

---

## Що було реалізовано

У проєкті реалізовано:

* FastAPI-сервіс для інференсу моделі;
* endpoint `/predict` для отримання передбачень;
* завантаження моделі з MLflow Model Registry;
* роботу з моделлю через URI;
* можливість тестування через Swagger UI;
* можливість тестування через PowerShell;
* повернення передбаченого класу та ймовірностей для кожного тексту.

---

## Призначення моделі

Модель використовується для класифікації українських текстових відгуків за трьома класами:

* `positive`
* `negative`
* `neutral`

---

## Завантаження моделі

Для зберігання та версіонування моделі використано MLflow Model Registry.

Модель не завантажується як окремий файл з репозиторію. Під час запуску FastAPI-сервіс підключається до MLflow Model Registry і завантажує модель за URI:

`models:/ukrainian-review-sentiment-model/6`

---

## Використані інструменти

У роботі використано такі інструменти:

* FastAPI — для створення REST API;
* Uvicorn — для запуску FastAPI-сервісу;
* MLflow Model Registry — для зберігання та завантаження версійованої моделі;
* scikit-learn — для роботи з навченою моделлю;
* pandas — для підготовки даних для інференсу.

---

## Структура проєкту для HW-3

mlops_homework/

├── app/

│   ├── **init**.py

│   └── main.py

│

├── requirements.txt

├── README.md

├── mlflow.db

└── mlartifacts/

---

## Основний файл сервісу

Основна логіка інференсу реалізована у файлі:

`app/main.py`

---

## Підготовка середовища

Перед запуском потрібно активувати Python-середовище:

`.venv\Scripts\activate`

Після цього потрібно встановити залежності:

`python -m pip install -r requirements.txt`

---

## Запуск MLflow Tracking Server

Спочатку потрібно запустити локальний MLflow Tracking Server, який надає доступ до MLflow Model Registry.

У першому терміналі потрібно виконати команду:

`python -m mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlartifacts --host 127.0.0.1 --port 5000`

Після запуску MLflow server буде доступний за адресою:

`http://127.0.0.1:5000`

Цей термінал потрібно залишити відкритим.

---

## Запуск FastAPI-сервісу

В іншому терміналі потрібно активувати Python-середовище:

`.venv\Scripts\activate`

Далі потрібно вказати адресу MLflow Tracking Server:

`$env:MLFLOW_TRACKING_URI="http://127.0.0.1:5000"`

Також потрібно вказати модель з MLflow Model Registry:

`$env:MLFLOW_MODEL_URI="models:/ukrainian-review-sentiment-model/6"`

Після цього потрібно запустити FastAPI-сервіс:

`python -m uvicorn app.main:app --reload`

Після запуску сервіс буде доступний за адресою:

`http://127.0.0.1:8000`

Документація API доступна за адресою:

`http://127.0.0.1:8000/docs`

---

## Перевірка роботи сервісу через Swagger UI

Для перевірки роботи сервісу потрібно відкрити у браузері:

`http://127.0.0.1:8000/docs`

На сторінці документації потрібно знайти endpoint:

`POST /predict`

Далі потрібно натиснути:

`Try it out`

Після цього у поле запиту потрібно вставити тестові приклади:

{
"texts": [
"Мені дуже сподобалось, покупкою задоволена",
"Поганий сервіс і неякісний товар",
"Товар отримано, без особливих вражень"
]
}

Після натискання кнопки `Execute` сервіс повертає відповідь моделі.

---

## Приклад відповіді сервісу

{
"model_uri": "models:/ukrainian-review-sentiment-model/6",
"tracking_uri": "http://127.0.0.1:5000",
"results": [
{
"text": "Мені дуже сподобалось, покупкою задоволена",
"prediction": "positive",
"probabilities": {
"negative": 0.154,
"neutral": 0.134,
"positive": 0.712
}
},
{
"text": "Поганий сервіс і неякісний товар",
"prediction": "negative",
"probabilities": {
"negative": 0.506,
"neutral": 0.326,
"positive": 0.168
}
},
{
"text": "Товар отримано, без особливих вражень",
"prediction": "neutral",
"probabilities": {
"negative": 0.197,
"neutral": 0.588,
"positive": 0.215
}
}
]
}

Значення ймовірностей можуть відрізнятися залежно від версії моделі та вхідних текстів.

---

## Перевірка через PowerShell

Сервіс також можна перевірити через команду:

`Invoke-RestMethod -Uri "http://127.0.0.1:8000/predict" -Method Post -ContentType "application/json" -Body '{"texts":["Мені дуже сподобалось, покупкою задоволена","Поганий сервіс і неякісний товар","Товар отримано, без особливих вражень"]}'`

---

## Результат HW-3

У результаті було розгорнуто REST API для інференсу моделі.

FastAPI-сервіс завантажує модель, навчену у HW-2, з MLflow Model Registry за URI:

`models:/ukrainian-review-sentiment-model/6`

Endpoint `/predict` приймає тестові текстові приклади та повертає передбачення моделі для кожного з них.

---

# HW-4 — Monitoring and Observability у MLOps

## Мета роботи

У межах домашньої роботи 4 було налаштовано систему моніторингу для ML-сервісу інференсу, який був реалізований у HW-3.

Базою для моніторингу є FastAPI-сервіс, який завантажує модель з MLflow Model Registry та виконує передбачення для текстових відгуків українською мовою.

---

## Що було реалізовано

У проєкті реалізовано:

* інструментацію FastAPI-сервісу за допомогою `prometheus-client`;
* endpoint `/metrics` для експорту метрик у форматі Prometheus;
* збір метрик через Prometheus;
* Grafana dashboard для візуалізації метрик;
* тестове навантаження через скрипт `load_test.py`;
* логування передбачень у файл `logs/predictions.csv`;
* генерацію Evidently drift report для базового аналізу дріфту даних.

---

## Архітектура моніторингу

Система моніторингу побудована за такою схемою:

FastAPI inference service → `/metrics` → Prometheus → Grafana Dashboard

FastAPI-сервіс виконує передбачення моделі та збирає метрики.

Prometheus періодично забирає ці метрики з endpoint `/metrics`.

Grafana підключається до Prometheus як datasource і відображає метрики на dashboard.

---

## Основні файли, додані для HW-4

* `app/main.py`
* `docker-compose.monitoring.yml`
* `monitoring/prometheus.yml`
* `monitoring/grafana/provisioning/datasources/prometheus.yml`
* `monitoring/grafana/provisioning/dashboards/dashboard.yml`
* `monitoring/grafana/dashboards/ml_dashboard.json`
* `scripts/load_test.py`
* `scripts/evidently_report.py`
* `logs/predictions.csv`
* `reports/data_drift_report.html`

---

## Prometheus metrics

У FastAPI-сервісі було додано такі метрики:

### `ml_predictions_total`

Показує загальну кількість передбачень моделі.

Метрика має label `predicted_class`, що дозволяє бачити кількість передбачень окремо для класів:

* `negative`
* `positive`
* `neutral`

### `ml_prediction_latency_seconds`

Показує час обробки запиту моделлю.

Ця метрика використовується для розрахунку середнього latency та p95 latency.

### `ml_prediction_batch_size`

Показує кількість текстів в одному запиті до endpoint `/predict`.

### `ml_prediction_errors_total`

Показує кількість помилок під час виконання передбачень.

---

## Запуск MLflow

Спочатку потрібно запустити MLflow Tracking Server:

`python -m mlflow server --host 127.0.0.1 --port 5000`

MLflow UI буде доступний за адресою:

`http://127.0.0.1:5000`

---

## Запуск FastAPI inference service

В окремому терміналі потрібно запустити FastAPI-сервіс:

`uvicorn app.main:app --host 0.0.0.0 --port 8000`

Документація API доступна за адресою:

`http://127.0.0.1:8000/docs`

Endpoint для метрик:

`http://127.0.0.1:8000/metrics`

---

## Запуск Prometheus та Grafana

Для запуску Prometheus і Grafana використовується Docker Compose:

`docker compose -f docker-compose.monitoring.yml up -d`

Prometheus доступний за адресою:

`http://localhost:9090`

Grafana доступна за адресою:

`http://localhost:3000`

Дані для входу в Grafana:

* Login: `admin`
* Password: `admin`

---

## Перевірка Prometheus

Після запуску Prometheus потрібно відкрити:

`http://localhost:9090/targets`

У списку targets має бути сервіс:

`fastapi-ml-service`

Статус має бути:

`UP`

Це означає, що Prometheus успішно збирає метрики з FastAPI-сервісу.

---

## Перевірка метрик у Prometheus

Для перевірки кількості передбачень використовувався запит:

`ml_predictions_total`

Після запуску тестового навантаження Prometheus показав такі значення:

* `negative` = 70
* `positive` = 34
* `neutral` = 16

Загальна кількість передбачень:

70 + 34 + 16 = 120

Це відповідає кількості запитів, які були створені скриптом `load_test.py`.

Ці значення показують не кількість рядків у навчальному датасеті, а кількість передбачень, які модель зробила під час тестового навантаження.

---

## Grafana Dashboard

У Grafana було створено dashboard:

`MLOps / ML Inference Monitoring`

На dashboard відображаються такі графіки:

* Predictions per minute;
* Average prediction latency;
* P95 prediction latency;
* Predictions by class.

Цей dashboard дозволяє бачити, як працює ML-сервіс під навантаженням: скільки передбачень виконується за хвилину та який середній час обробки запиту.

---

## Генерація тестового навантаження

Для перевірки моніторингу використовується скрипт:

`python scripts/load_test.py`

Скрипт відправляє 120 запитів до endpoint:

`http://127.0.0.1:8000/predict`

Після запуску скрипта метрики оновлюються у Prometheus, а Grafana dashboard показує зміну кількості передбачень та latency.

---

## Evidently Drift Report

Для базового аналізу дріфту даних було додано скрипт:

`scripts/evidently_report.py`

FastAPI-сервіс зберігає інформацію про передбачення у файл:

`logs/predictions.csv`

У логах зберігаються такі дані:

* timestamp;
* text;
* text_length;
* word_count;
* prediction;
* latency_seconds.

На основі цих логів Evidently порівнює старішу частину даних з новішою частиною даних.

Для аналізу використовуються такі ознаки:

* `text_length` — довжина тексту;
* `word_count` — кількість слів;
* `prediction` — передбачений клас;
* `latency_seconds` — час обробки запиту.

Таким чином можна перевірити базовий data drift та prediction drift.

---

## Генерація Evidently-звіту

Для генерації Evidently-звіту потрібно виконати:

`python scripts/evidently_report.py`

Після цього створюється HTML-звіт:

`reports/data_drift_report.html`

Відкрити звіт можна командою:

`start reports\data_drift_report.html`

---

## Результат HW-4

У результаті було налаштовано систему моніторингу для FastAPI ML-сервісу.

Було реалізовано збір метрик через Prometheus, створено Grafana dashboard для візуалізації роботи сервісу та додано Evidently-звіт для базового аналізу drift.

Система дозволяє контролювати:

* кількість передбачень;
* розподіл передбачень за класами;
* середній latency;
* p95 latency;
* розмір batch;
* помилки під час інференсу;
* базові ознаки data drift та prediction drift.

---

# Загальний результат проєкту

У межах усіх домашніх робіт було реалізовано повний базовий MLOps pipeline:

* HW-1 — підготовка, розмітка та версіонування даних;
* HW-2 — тренування моделі та трекінг експериментів;
* HW-3 — розгортання REST API для інференсу;
* HW-4 — моніторинг, observability та drift report.

Проєкт демонструє повний шлях роботи з ML-моделлю:

Дані → Розмітка → Версіонування → Тренування → Model Registry → Inference API → Monitoring → Drift Analysis
