import os


def _get_color(score: float) -> str:
    if score < 0.1:
        return "#FF0000"
    if score < 0.3:
        return "#FF4D4D"
    if score < 0.6:
        return "#DFB317"
    return "#44CC11"


def generate_peso(repo, site_dir: str) -> None:
    logger.info(f"Generating PESO badge for {repo['name']}")

    nchecks = len(repo["checks"])
    score = repo["score"]

    label = "PESO Scorecard"
    label_w = len(label) * 7 + 10
    label_pos_x = label_w // 2

    message = f"{score}/{nchecks}"
    message_w = len(message) * 7 + 10
    message_pos_x = label_w + (message_w // 2)

    color = _get_color(score / nchecks)
    total_w = label_w + message_w

    with open(f"{site_dir}/badges/{repo['name']}.svg", "w") as fd:
        fd.write(f"""\
<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="20" role="img" aria-label="{label}: {message}">
  <rect width="{total_w}" height="20" fill="#555"/>
  <rect x="{label_w}" width="{message_w}" height="20" fill="{color}"/>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,sans-serif" font-size="11">
    <text x="{label_pos_x}" y="14">{label}</text>
    <text x="{message_pos_x}" y="14">{message}</text>
  </g>
</svg>
        """)
