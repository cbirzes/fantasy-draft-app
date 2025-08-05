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
    current_pick = session['current_pick']

    drafted = session.get('drafted_players', [])
    df = pd.read_csv("data/2025PreseasonRankings.csv")
    df = df[~df['player_id'].isin(drafted)]

    position_order = ['RB', 'WR', 'QB', 'TE', 'DS', 'K']
    df['position'] = pd.Categorical(df['position'], categories=position_order, ordered=True)
    df = df.sort_values(['position', 'overall_rank'])
    positions = {pos: df[df['position'] == pos] for pos in position_order}

    current_pick_str = f"{current_pick[0]}.{current_pick[1]}"
    return render_template("draft_board.html", positions=positions, current_pick=current_pick_str)

@app.route("/draft/<int:player_id>", methods=["POST"])
def draft_player(player_id):
    drafted = session.get('drafted_players', [])
    if player_id not in drafted:
        drafted.append(player_id)
        session['drafted_players'] = drafted

    current_pick = session.get('current_pick', (1, 1))
    session['current_pick'] = get_next_pick(current_pick)

    return redirect(url_for('draft_board'))

# <-- Add this route to fix your error -->
@app.route("/reset_pick", methods=["POST"])
def reset_pick():
    session['current_pick'] = (1, 1)
    session['drafted_players'] = []
    return redirect(url_for('draft_board'))

if __name__ == "__main__":
    app.run(debug=True)
