import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def config_db():
    uri = os.environ.get("SUPABASE_URI_DB")
    conn = psycopg2.connect(uri)
    return conn

def winner(curr, winner_team_name, winner_team_score, losser_team_score):
    query = "UPDATE leaderboard SET play = play + 1, win = win + 1, goals_for = goals_for + {}, goals_against = goals_against + {} WHERE team_name = '{}'".format(winner_team_score, losser_team_score, winner_team_name)
    curr.execute(query)

def losser(curr, losser_team_name, losser_team_score, winner_team_score):
    query = "UPDATE leaderboard SET play = play + 1, loss = loss + 1, goals_for = goals_for + {}, goals_against = goals_against + {} WHERE team_name = '{}'".format(losser_team_score, winner_team_score, losser_team_name)
    curr.execute(query)

def draw(curr, team_name, score):
    query = "UPDATE leaderboard SET play = play + 1, draw = draw + 1, goals_for = goals_for + {}, goals_against = goals_against + {} WHERE team_name = '{}'".format(score, score, team_name)
    curr.execute(query)

