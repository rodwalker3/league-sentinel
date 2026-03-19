from rules import POSITION_BUCKETS, BANNED_ABILITIES


def get_bucket(position: str):
    return POSITION_BUCKETS.get(position.upper())


def check_team_abilities(players):
    duplicate_map = {}
    duplicate_violations = []
    banned_violations = []

    for player in players:
        name = player["name"]
        pos = player["pos"]
        abilities = player["abilities"]

        bucket = get_bucket(pos)

        for ability in abilities:
            if ability in BANNED_ABILITIES:
                banned_violations.append({
                    "player": name,
                    "pos": pos,
                    "ability": ability
                })

            if bucket:
                key = (bucket, ability)
                duplicate_map.setdefault(key, []).append({
                    "player": name,
                    "pos": pos
                })

    for (bucket, ability), holders in duplicate_map.items():
        if len(holders) > 1:
            duplicate_violations.append({
                "bucket": bucket,
                "ability": ability,
                "players": holders
            })

    return {
        "banned": banned_violations,
        "duplicates": duplicate_violations
    }