from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd

app = Flask(__name__)
app.secret_key = "your-secret-key"

NUM_TEAMS = 12

def get_next_pick(current_pick):
    round_num, pick_num = current_pick
    if pick_num < NUM_TEAMS:
        return (round_num, pick_num + 1)
    else:
        return (round_num + 1, 1)

@app.route("/", methods=["GET"])
def draft_board():
    if 'current_pick' not in session:
        session['current_pick'] = (1, 1)  # Start at pick 1.1
    if 'drafted_players' not in session:
        session['drafted_players'] = []
    if 'my_team' not in session:
        session['my_team'] = []

    current_pick = session['current_pick']
    drafted = session['drafted_players']
    my_team_ids = session['my_team']

    df = pd.read_csv("data/2025PreseasonRankings.csv")
    df = df[~df['player_id'].isin(drafted)]

    position_order = ['RB', 'WR', 'QB', 'TE', 'DS', 'K']
    df['position'] = pd.Categorical(df['position'], categories=position_order, ordered=True)
    df = df.sort_values(['position', 'overall_rank'])
    positions = {pos: df[df['position'] == pos] for pos in position_order}

    # Build My Team display structure
    full_df = pd.read_csv("data/2025PreseasonRankings.csv")
    my_team_df = full_df[full_df['player_id'].isin(my_team_ids)]

    team_slots = {
        'QB': [],
        'RB': [],
        'WR': [],
        'TE': [],
        'DS': [],
        'K': [],
        'Bench': []
    }

    position_limits = {
        'QB': 1,
        'RB': 3,
        'WR': 3,
        'TE': 1,
        'DS': 1,
        'K': 1
    }

    for _, player in my_team_df.iterrows():
        pos = player['position']
        if pos in team_slots and len(team_slots[pos]) < position_limits[pos]:
            team_slots[pos].append(player)
        else:
            team_slots['Bench'].append(player)

    current_pick_str = f"{current_pick[0]}.{current_pick[1]}"
    return render_template(
        "draft_board.html",
        positions=positions,
        current_pick=current_pick_str,
        my_team=team_slots
    )

@app.route("/draft/<int:player_id>", methods=["POST"])
def draft_player(player_id):
    drafted = session.get('drafted_players', [])
    if player_id not in drafted:
        drafted.append(player_id)
        session['drafted_players'] = drafted

    current_pick = session.get('current_pick', (1, 1))
    session['current_pick'] = get_next_pick(current_pick)

    return redirect(url_for('draft_board'))

@app.route("/add_to_my_team/<int:player_id>", methods=["POST"])
def add_to_my_team(player_id):
    drafted = session.get('drafted_players', [])
    my_team = session.get('my_team', [])

    if player_id not in drafted:
        drafted.append(player_id)
        session['drafted_players'] = drafted

    if player_id not in my_team:
        my_team.append(player_id)
        session['my_team'] = my_team

    current_pick = session.get('current_pick', (1, 1))
    session['current_pick'] = get_next_pick(current_pick)

    return redirect(url_for('draft_board'))

@app.route("/reset_pick", methods=["POST"])
def reset_pick():
    session['current_pick'] = (1, 1)
    session['drafted_players'] = []
    session['my_team'] = []
    return redirect(url_for('draft_board'))

if __name__ == "__main__":
    app.run(debug=True)
