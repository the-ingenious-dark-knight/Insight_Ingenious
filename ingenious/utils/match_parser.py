import json


class MatchDataParser:
    def __init__(self, payload):
        with open(payload,'r') as file:
            self.data = json.load(file) #if isinstance(payload, str) else payload
        self.fixture = self.data.get("fixture", {})
        self.players = self.data.get("players", [])

    def get_team_info(self, team_key):
        team = self.fixture.get(team_key, {})
        return {
            "id": team.get("id"),
            "name": team.get("name", "Unknown Team"),
            "short_name": team.get("shortName", "Unknown"),
            "logo_url": team.get("logoUrl", "")
        }

    def get_player_name(self, player_id):
        player = next((p for p in self.players if p.get("id") == player_id), {})
        return player.get("displayName", "Unknown Player")

    def get_match_summary(self):
        home_team = self.get_team_info("homeTeam")
        away_team = self.get_team_info("awayTeam")
        result = self.fixture.get("resultText", "Result not available")
        venue = self.fixture.get("venue", {}).get("name", "Unknown Venue")
        competition = self.fixture.get("competition", {}).get("name", "Unknown Competition")

        return (
            f"Match: {competition} at {venue}\n"
            f"Teams: {home_team['name']} vs {away_team['name']}\n"
            f"Result: {result}"
        )

    def get_innings_summary(self):
        innings_data = self.fixture.get("innings", [])
        summaries = []

        for inning in innings_data:
            batting_team_id = inning.get("battingTeamId")
            batting_team = next(
                (team_key for team_key in ["homeTeam", "awayTeam"]
                 if self.fixture.get(team_key, {}).get("id") == batting_team_id),
                "Unknown Team"
            )
            team_name = self.fixture.get(batting_team, {}).get("name", "Unknown Team")
            runs_scored = inning.get("runsScored", 0)
            wickets = inning.get("numberOfWicketsFallen", 0)
            overs = inning.get("oversBowled", "0.0")
            extras = inning.get("totalExtras", 0)
            overs_float = float(overs.split('.')[0]) + float(overs.split('.')[1])/6 if '.' in overs else float(overs)
            run_rate = round(runs_scored / overs_float if overs_float else 0, 2)

            summaries.append(
                f"{team_name} Innings:\n"
                f"Score: {runs_scored}/{wickets} in {overs} overs\n"
                f"Run Rate: {run_rate}\n"
                f"Extras: {extras}"
            )

        return "\n\n".join(summaries)

    def get_batting_highlights(self):
        highlights = []
        for inning in self.fixture.get("innings", []):
            batsmen = inning.get("batsmen", [])
            top_scorers = sorted(batsmen, key=lambda x: x.get("runsScored", 0), reverse=True)[:3]
            for batsman in top_scorers:
                runs = batsman.get("runsScored", 0)
                balls = batsman.get("ballsFaced", 0)
                strike_rate = batsman.get("strikeRate", 0)
                player_id = batsman.get("playerId")
                player_name = self.get_player_name(player_id)
                milestones = []
                if runs >= 50 and runs < 100:
                    milestones.append("half-century")
                elif runs >= 100:
                    milestones.append("century")
                highlight_text = (
                    f"{player_name} scored {runs} runs off {balls} balls "
                    f"(SR: {strike_rate})"
                )
                if milestones:
                    highlight_text += f" achieving a {' and '.join(milestones)}"
                highlights.append(highlight_text)
        return highlights

    def get_bowling_highlights(self):
        highlights = []
        for inning in self.fixture.get("innings", []):
            bowlers = inning.get("bowlers", [])
            top_bowlers = sorted(
                bowlers,
                key=lambda x: (x.get("wicketsTaken", 0), -float(x.get("economy", 99))),
                reverse=True
            )[:3]
            for bowler in top_bowlers:
                wickets = bowler.get("wicketsTaken", 0)
                overs = bowler.get("oversBowled", "0")
                runs_conceded = bowler.get("runsConceded", 0)
                economy = bowler.get("economy", 0)
                player_id = bowler.get("playerId")
                player_name = self.get_player_name(player_id)
                milestones = []
                if wickets >= 5:
                    milestones.append("five-wicket haul")
                highlight_text = (
                    f"{player_name} took {wickets} wickets for {runs_conceded} runs "
                    f"in {overs} overs (Econ: {economy})"
                )
                if milestones:
                    highlight_text += f" achieving a {' and '.join(milestones)}"
                highlights.append(highlight_text)
        return highlights

    def get_key_partnerships(self):
        partnerships = []
        for inning in self.fixture.get("innings", []):
            batsmen = inning.get("batsmen", [])
            # Sort batsmen by runs scored
            sorted_batsmen = sorted(batsmen, key=lambda x: x.get("runsScored", 0), reverse=True)
            
            # Look at top run scorers and find their partnerships
            for i in range(len(sorted_batsmen) - 1):
                batsman1 = sorted_batsmen[i]
                batsman2 = sorted_batsmen[i + 1]
                runs1 = batsman1.get("runsScored", 0)
                runs2 = batsman2.get("runsScored", 0)
                
                # If both batsmen scored well (combined 50+ runs)
                if runs1 + runs2 >= 50:
                    player1 = self.get_player_name(batsman1.get("playerId"))
                    player2 = self.get_player_name(batsman2.get("playerId"))
                    partnerships.append(
                        f"Significant partnership between {player1} ({runs1}) and "
                        f"{player2} ({runs2}), total: {runs1 + runs2} runs"
                    )
        return partnerships

    def get_momentum_shifts(self):
        momentum_shifts = []
        for inning in self.fixture.get("innings", []):
            batting_team_id = inning.get("battingTeamId")
            batting_team = next(
                (team_key for team_key in ["homeTeam", "awayTeam"]
                 if self.fixture.get(team_key, {}).get("id") == batting_team_id),
                "Unknown Team"
            )
            team_name = self.fixture.get(batting_team, {}).get("name", "Unknown Team")
            
            # Look for clusters of wickets
            bowlers = inning.get("bowlers", [])
            for bowler in bowlers:
                wickets = bowler.get("wicketsTaken", 0)
                overs = bowler.get("oversBowled", "0")
                if wickets >= 2:
                    player_name = self.get_player_name(bowler.get("playerId"))
                    momentum_shifts.append(
                        f"Momentum Shift: {player_name} took {wickets} wickets in "
                        f"{overs} overs against {team_name}"
                    )
            
            # Look for high scoring batsmen
            batsmen = inning.get("batsmen", [])
            for batsman in batsmen:
                runs = batsman.get("runsScored", 0)
                strike_rate = batsman.get("strikeRate", 0)
                if runs >= 30 and strike_rate >= 150:
                    player_name = self.get_player_name(batsman.get("playerId"))
                    momentum_shifts.append(
                        f"Momentum Shift: {player_name} scored {runs} runs at a "
                        f"strike rate of {strike_rate}"
                    )
        
        return momentum_shifts

    def create_detailed_summary(self):
        match_narrative = self.get_match_summary()
        innings_details = self.get_innings_summary()
        batting_highlights = self.get_batting_highlights()
        bowling_highlights = self.get_bowling_highlights()
        partnerships = self.get_key_partnerships()
        momentum_shifts = self.get_momentum_shifts()

        sections = [
            ("Match Summary", match_narrative),
            ("Innings Details", innings_details),
            ("Batting Highlights", "\n".join(batting_highlights)),
            ("Bowling Highlights", "\n".join(bowling_highlights)),
            ("Key Partnerships", "\n".join(partnerships)),
            ("Momentum Shifts", "\n".join(momentum_shifts))
        ]

        return "\n\n".join(
            f"{title}:\n{content}" for title, content in sections if content.strip()
        )
