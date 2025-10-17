# hello-world

цей репозитор призначений для тесту github

## Скрипт для прогнозів у тенісі

У репозиторії додано скрипт `tennis_prediction.py`, який допомагає
орієнтовно оцінити шанси перемоги для тенісистів. Скрипт очікує базові
статистичні показники (ранг, відсоток виграних очок на подачі/на прийомі,
успішність на поточному покритті та форму) і повертає ймовірності перемоги для
кожного тенісиста. Підтримуються два режими роботи: ручний розрахунок для однієї
пари гравців та пакетна обробка CSV-файлу з кількома матчами.

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

Скрипт виведе результати у консоль і, за потреби, збереже їх у файл `predictions.csv`.
