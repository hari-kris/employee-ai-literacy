import csv
import io


def to_csv(results: list[tuple[str, str | float]]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["filename", "ai_literacy_score"])
    writer.writerows(results)
    return buf.getvalue()
