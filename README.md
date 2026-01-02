# hello-world

цей репозитор призначений для тесту github

## Термінальна гра «Змійка»

Файл `snake_game.py` містить самодостатню гру для терміналу. Щоб скопіювати її на
інший комп'ютер і пограти:

1. Створіть нову теку (наприклад, `snake/`) і додайте в неї файл `snake_game.py`
   із цього репозиторію. Можна скопіювати текст вручну, завантажити файл або
   перенести через `scp`/USB.
2. Переконайтеся, що встановлено Python 3. На Windows додайте бібліотеку
   `windows-curses` командою `pip install windows-curses`.
3. Відкрийте термінал у створеній теці та виконайте `python snake_game.py`.
4. Керуйте стрілками або клавішами WASD; вийти можна, натиснувши `q`.

## Скрипт для прогнозів у тенісі

У репозиторії додано скрипт `tennis_prediction.py`, який допомагає
орієнтовно оцінити шанси перемоги для тенісистів. Скрипт очікує базові
статистичні показники (ранг, відсоток виграних очок на подачі/на прийомі,
успішність на поточному покритті та форму) і повертає ймовірності перемоги для
кожного тенісиста. Підтримуються два режими роботи: ручний розрахунок для однієї
пари гравців та пакетна обробка CSV-файлу з кількома матчами.

### Встановлення

Для встановлення залежностей виконайте:

```bash
pip install -r requirements.txt
```

Або встановіть пакет у режимі розробки:

```bash
pip install -e .
```

Після встановлення ви зможете використовувати команду `tennis-prediction` замість
`python tennis_prediction.py`.

### Приклад використання

```bash
python tennis_prediction.py \
  --player_one-name "Iga Swiatek" --player_one-ranking 1 \
  --player_one-serve 0.62 --player_one-return 0.46 \
  --player_one-surface 0.80 --player_one-form 0.90 \
  --player_two-name "Elena Rybakina" --player_two-ranking 4 \
  --player_two-serve 0.58 --player_two-return 0.41 \
  --player_two-surface 0.74 --player_two-form 0.85
```

У результаті будуть показані відсоткові ймовірності виграшу кожної спортсменки.

### Пакетний режим

CSV-файл має містити назви колонок `player_one_name`, `player_one_ranking`,
`player_one_serve`, `player_one_return`, `player_one_surface`, `player_one_form`
та відповідні колонки для `player_two`. Приклад використання:

```bash
python tennis_prediction.py --matches-file matches.csv --output predictions.csv
```

Скрипт виведе результати у консоль і, за потреби, збереже їх у файл
`predictions.csv`.

## Гібридна модель (Gradient Boosting + Neural Network)

Файл `hybrid_pipeline.py` містить приклад офлайн-пайплайну для побудови гібридної
моделі, яка поєднує градієнтний бустинг та багатошаровий перцептрон у режимі
stacking. Пайплайн охоплює:

* попередню обробку числових та категоріальних фіч;
* отримання out-of-fold прогнозів бустингу для тренування нейромережі;
* оцінювання моделі за метриками ROC AUC, LogLoss, Brier Score та Accuracy;
* серіалізацію артефактів для подальшого експорту в ONNX/Core ML.

### Приклад використання в Python

```python
from hybrid_pipeline import HybridPipelineConfig, HybridWinProbabilityPipeline

matches = [
    {
        "p1_rank": 0.2,
        "p2_rank": 0.6,
        "p1_form": 0.8,
        "p2_form": 0.5,
        "surface_index": 0.7,
        "winner": 1.0,
    },
    # ... додаткові матчі
]

config = HybridPipelineConfig(
    target_column="winner",
    numeric_features=["p1_rank", "p2_rank", "p1_form", "p2_form", "surface_index"],
    n_splits=4,
    boosting_estimators=80,
    boosting_learning_rate=0.1,
    hidden_size=32,
    nn_learning_rate=0.03,
    nn_epochs=150,
)

pipeline = HybridWinProbabilityPipeline(config)
pipeline.fit(matches)

print(pipeline.evaluate(matches))
pipeline.save("hybrid_model.json")
```

Отриманий JSON-артефакт містить повний пайплайн (препроцесинг + моделі) і може бути
конвертований у формат Core ML за допомогою `coremltools`, щоб виконувати
інференс на iOS-пристрої.

### Тестування

Для перевірки логіки можна запустити автоматичні тести:

```bash
pytest
```

Тести охоплюють ручний та пакетний режими, а також базові розрахунки ймовірностей
і дозволяють переконатися, що скрипт працює очікуваним чином після внесення змін.

## Парсинг букмекерських фідів

Розміщений у репозиторії файл `betting_data.py` перетворює сирий текст із
букмекерського фіду (саме такий блок даних було передано в запиті) у структури
типу `MatchOdds`. Додатково функція `build_training_rows` будує словники з
обчисленими ознаками – нормалізованими ймовірностями, маржею та проксі-міткою
"фаворит" – які можна одразу використовувати для навчання моделей, зокрема
гібридного пайплайна з файлу `hybrid_pipeline.py`.

### Приклад використання

```python
from betting_data import build_training_rows, parse_betting_text

with open("raw_feed.txt", "r", encoding="utf8") as handle:
    feed = handle.read()

matches = parse_betting_text(feed)
training_rows = build_training_rows(matches)

for row in training_rows[:3]:
    print(row)
```

Для прикладу з опису вище буде розпізнано 3 матчі, а кожен словник міститиме
`odds_margin`, `implied_prob_one`, `implied_prob_two` та інші поля, необхідні
для машинного навчання.

## Android-додаток

У директорії `android-app/` міститься приклад нативного Android-застосунку на
Kotlin/Jetpack Compose, який використовує ту саму формулу, що й Python-скрипт, для
розрахунку ймовірностей перемоги. Інтерфейс дозволяє вводити показники для двох
тенісистів та одразу бачити результати.

### Вимоги

* Android Studio Giraffe (або новіша версія) з установленим Android SDK 34.
* JDK 17, що постачається разом із Android Studio.

### Запуск із Android Studio

1. Відкрийте Android Studio та оберіть **Open an Existing Project**.
2. Вкажіть шлях до каталогу `android-app` у цьому репозиторії.
3. Дочекайтеся, поки Gradle синхронізує залежності.
4. Запустіть застосунок на емуляторі або під’єднаному пристрої Android 8.0+
   (API 26 або вище).

### Налаштування введення

У застосунку передбачені підказки та валідація для значень, які мають бути в
межах `[0, 1]`. Якщо введено некоректні дані, поле буде підсвічене, а кнопка
розрахунку стане недоступною.

### Повторне використання формули

Файл `app/src/main/java/com/example/tennispredictor/model/TennisPrediction.kt`
містить Kotlin-версію функцій підрахунку якості та ймовірностей. Їх можна
використати повторно в інших частинах Android-проєкту або в модульних тестах.
