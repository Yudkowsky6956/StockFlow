import json
import plotly.graph_objects as go
import pandas as pd

from .vars import *


def compress_zero_sequences(df_err: pd.DataFrame) -> pd.DataFrame:
    """
    Сжимает последовательности дней с amount == 0,
    оставляя только первую и последнюю точку последовательности.
    """
    amounts = df_err["amount"].values
    dates = df_err["date"].values

    keep_indices = set()

    i = 0
    n = len(amounts)
    while i < n:
        if amounts[i] == 0:
            start = i
            while i + 1 < n and amounts[i + 1] == 0:
                i += 1
            end = i

            # добавляем только начало и конец последовательности нулей
            keep_indices.add(start)
            if end != start:
                keep_indices.add(end)
        else:
            keep_indices.add(i)
        i += 1

    # Оставляем только нужные строки
    mask = [idx in keep_indices for idx in range(n)]
    return df_err[mask]


def view_by_day(top_n_errors=100):
    """
    Временной график топ N ошибок по дням с интерактивным скроллингом и вертикальной легендой под графиком.
    """
    # Загружаем данные
    with open(OUTPUT_BY_DAY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Считаем суммарное количество каждой ошибки
    total_counter = {}
    for day, errors in data.items():
        for err in errors:
            total_counter[err["text"]] = total_counter.get(err["text"], 0) + err["amount"]

    # Берём топ N ошибок
    top_errors = sorted(total_counter.items(), key=lambda x: x[1], reverse=True)[:top_n_errors]
    top_n_errors = len(top_errors)
    top_texts = set(text for text, _ in top_errors)

    # Формируем DataFrame с датами
    rows = []
    for day, errors in data.items():
        for err in errors:
            if err["text"] in top_texts:
                rows.append({
                    "date": pd.to_datetime(day, format="%d.%m.%Y"),
                    "error": err["text"],
                    "amount": err["amount"]
                })

    df = pd.DataFrame(rows)
    if df.empty:
        print("Нет данных для отображения")
        return

    fig = go.Figure()

    # Добавляем линии для каждой ошибки
    total_per_day = df.groupby("date")["amount"].sum().reset_index()
    total_per_day.rename(columns={"amount": "total_errors"}, inplace=True)
    fig.add_trace(
        go.Scatter(
            x=total_per_day["date"],
            y=total_per_day["total_errors"],
            mode="lines+markers",
            name="Общее количество ошибок",
            line=dict(color="black", width=2),
            marker=dict(size=6)
        )
    )

    # Получаем полный список всех дат
    all_dates = pd.date_range(start=df['date'].min(), end=df['date'].max())

    for err_text in top_texts:
        # Фильтруем данные по конкретной ошибке
        df_err = df[df["error"] == err_text].copy()
        df_err["date"] = pd.to_datetime(df_err["date"], dayfirst=True)
        df_err.set_index("date", inplace=True)

        # Переиндексация по всем датам
        df_err = df_err.reindex(all_dates, fill_value=0)
        df_err = df_err.reset_index().rename(columns={"index": "date"})

        # Сжимаем последовательности нулей
        df_err = compress_zero_sequences(df_err)

        # Добавляем на график
        fig.add_trace(go.Scatter(
            x=df_err["date"],
            y=df_err["amount"],
            mode="lines+markers",
            name=err_text,
            hovertemplate="%{y} ошибок<br>%{x|%d.%m.%Y}<extra></extra>"
        ))

    fig.update_layout(
        title=f"Динамика {top_n_errors} ошибок по дням",
        xaxis_title="Дата",
        yaxis_title="Количество ошибок",
        xaxis=dict(
            type="date"  # оставляем только тип оси
        ),
        autosize=True,
        height=2000,
        legend=dict(
            orientation="v",  # вертикальный список
            yanchor="top",
            y=-0.1,  # немного ниже графика
            xanchor="left",
            x=0,
            traceorder="normal"
        ),
    )

    fig.show()