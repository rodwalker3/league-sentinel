import os
import discord
from dotenv import load_dotenv
from discord import app_commands

from neon import get_roster
from config import check_team_abilities
from teams import TEAMS

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


def build_report(results: dict) -> str:
    banned = results["banned"]
    duplicates = results["duplicates"]

    if not banned and not duplicates:
        return "✅ No banned abilities or duplicate abilities found."

    lines = []

    if banned:
        lines.append("🚫 **Banned Abilities**")
        for item in banned:
            lines.append(
                f"- **{item['ability']}** on {item['player']} ({item['pos']})"
            )
        lines.append("")

    if duplicates:
        lines.append("🚨 **Duplicate Abilities**")
        for item in duplicates:
            player_names = ", ".join(
                f"{p['player']} ({p['pos']})" for p in item["players"]
            )
            lines.append(
                f"- **{item['ability']}** in **{item['bucket']}**: {player_names}"
            )
        lines.append("")

    return "\n".join(lines)


@tree.command(name="checkteam", description="Check a team for banned and duplicate abilities")
@app_commands.describe(team="Type the team name exactly as listed in teams.py")
async def checkteam(interaction: discord.Interaction, team: str):
    await interaction.response.defer(thinking=True)

    matched_team = None
    for team_name in TEAMS:
        if team_name.lower() == team.lower():
            matched_team = team_name
            break

    if matched_team is None:
        valid_teams = ", ".join(TEAMS.keys())
        await interaction.followup.send(
            f"❌ Team not found.\nValid teams: {valid_teams}"
        )
        return

    try:
        roster = await get_roster(TEAMS[matched_team])
        results = check_team_abilities(roster)
        report = build_report(results)
        await interaction.followup.send(report)
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}")


@tree.command(name="scanleague", description="Scan every team in the league")
async def scanleague(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    league_results = []

    for team_name, url in TEAMS.items():
        try:
            roster = await get_roster(url)
            team_results = check_team_abilities(roster)

            if team_results["banned"] or team_results["duplicates"]:
                lines = [f"🚨 **{team_name}**"]

                for item in team_results["banned"]:
                    lines.append(
                        f"- BANNED | {item['ability']}: {item['player']} ({item['pos']})"
                    )

                for item in team_results["duplicates"]:
                    player_names = ", ".join(
                        f"{p['player']} ({p['pos']})" for p in item["players"]
                    )
                    lines.append(
                        f"- DUPLICATE | {item['bucket']} | {item['ability']}: {player_names}"
                    )

                league_results.append("\n".join(lines))

        except Exception as e:
            league_results.append(f"❌ **{team_name}**: {e}")

    if not league_results:
        await interaction.followup.send(
            "✅ League clean. No banned or duplicate abilities found."
        )
        return

    message = "\n\n".join(league_results)

    if len(message) > 1900:
        chunks = [message[i:i + 1900] for i in range(0, len(message), 1900)]
        for chunk in chunks:
            await interaction.followup.send(chunk)
    else:
        await interaction.followup.send(message)


@client.event
async def on_ready():
    await tree.sync()
    print(f"League Sentinel online as {client.user}")


client.run(TOKEN)