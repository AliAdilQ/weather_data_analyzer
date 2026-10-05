"""Database-backed Pandas aggregation with JSON-safe chart outputs."""

import numpy as np
import pandas as pd
from ..models import WeatherRecord, SearchHistory


def analyze(city=None):
    records = WeatherRecord.query
    if city:
        records = records.filter_by(city=city)
    rows = records.order_by(WeatherRecord.recorded_at).all()
    frame = pd.DataFrame(
        [
            {
                "city": r.city,
                "temperature": r.temperature,
                "humidity": r.humidity,
                "wind_speed": r.wind_speed,
                "condition": r.condition,
                "source": r.source,
                "date": r.recorded_at.strftime("%Y-%m-%d"),
            }
            for r in rows
        ]
    )
    stats = dict(
        count=len(rows), temperature=0, humidity=0, wind_speed=0, highest=0, lowest=0
    )
    charts = {}
    by_city = []
    if not frame.empty:
        for metric in ("temperature", "humidity", "wind_speed"):
            stats[metric] = round(float(np.mean(frame[metric])), 1)
            daily = frame.groupby("date")[metric].mean().round(1)
            charts[metric] = {"labels": daily.index.tolist(), "values": daily.tolist()}
        stats.update(
            highest=float(frame.temperature.max()),
            lowest=float(frame.temperature.min()),
        )
        for metric in ("condition", "source"):
            counts = frame[metric].value_counts()
            charts[metric] = {
                "labels": counts.index.tolist(),
                "values": counts.tolist(),
            }
        averages = (
            frame.groupby("city")[["temperature", "humidity", "wind_speed"]]
            .mean()
            .round(1)
        )
        by_city = averages.reset_index().to_dict(orient="records")
        bins, edges = np.histogram(frame.temperature, bins=6)
        charts["distribution"] = {
            "labels": [f"{edges[i]:.0f}–{edges[i + 1]:.0f}°" for i in range(6)],
            "values": bins.tolist(),
        }
    searches = SearchHistory.query.all()
    search_counts = pd.Series([s.city for s in searches], dtype="object").value_counts()
    charts["searches"] = {
        "labels": search_counts.index.tolist(),
        "values": search_counts.tolist(),
    }
    return dict(
        stats=stats,
        charts=charts,
        by_city=by_city,
        total_searches=len(searches),
        successful=sum(s.successful for s in searches),
        failed=sum(not s.successful for s in searches),
        cities=len(set(r.city for r in rows)),
        latest=max((r.recorded_at for r in rows), default=None),
        most_searched=search_counts.index[0]
        if len(search_counts)
        else "No searches yet",
        common_condition=frame.condition.mode().iloc[0]
        if not frame.empty
        else "No observations",
    )
