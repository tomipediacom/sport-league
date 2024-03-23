import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime
import pytz
from psycopg2.errors import UniqueViolation

from db import config_db, winner, losser, draw
from sonyflake import SonyFlake

st.secrets["SUPABASE_URI_DB"]

sf = SonyFlake()

st.title("EA Sports League")

jakarta_tz = pytz.timezone('Asia/Jakarta')

db = config_db()

st.divider()
if st.sidebar.header("user"):
    st.header("Add User")
    col_1, col_2 = st.columns(2)
    user_name = col_1.text_input("User Name")
    team_name = col_2.text_input("Team Name")

    if st.button("Add User"):
        id = sf.next_id()
        curr = db.cursor()
        
        query = "SELECT count(*) FROM match;"
        curr.execute(query)
        total_match = curr.fetchone()
        if total_match[0] != 0:
            st.error("match started, can't add user")
        else:
            query = "INSERT INTO \"user\" (id, name, team_name, created_at, updated_at) VALUES({}, '{}', '{}', '{}', '{}')".format(id, user_name, team_name, datetime.now(jakarta_tz), datetime.now(jakarta_tz))
            try:
                curr.execute(query)
            except UniqueViolation:
                st.error("team name already")

            query = "INSERT INTO leaderboard(team_name) VALUES('{}')".format(team_name)
            try:
                curr.execute(query)
            except UniqueViolation:
                st.error("team name already")
            db.commit()

st.divider()
if st.sidebar.header("match"):
    st.header("Add Match")

    curr = db.cursor()
    query = "SELECT team_name FROM \"user\""
    curr.execute(query)
    temp = curr.fetchall()
    data_team = []
    for t in temp:
        data_team.append(t[0])
    
    col_1, col_2 = st.columns(2)
    first_team_name = col_1.selectbox("First Team Name", data_team)
    first_team_score = col_1.number_input("First Team Score", min_value=0, max_value=50, step=1)
    second_team_name = col_2.selectbox("Second Team Name", data_team)
    second_team_score = col_2.number_input("Second Team Score", min_value=0, max_value=50, step=1)

    if st.button("Submit"):
        query = "SELECT EXISTS(SELECT 1 FROM \"user\" WHERE team_name = '{}') team_1, EXISTS(SELECT 1 FROM \"user\" WHERE team_name = '{}') team_2;".format(first_team_name, second_team_name)
        curr.execute(query)
        team_exists = curr.fetchone()
        if (team_exists[0] != True) == True or (team_exists[1] != True) == True:
            st.error("team not found")
        elif first_team_name == second_team_name:
            st.error("both team name can't same")
        else:
            # check is team has match together
            query = "SELECT count(*) FROM match WHERE first_team_name = '{}' AND second_team_name = '{}'".format(first_team_name, second_team_name)
            curr.execute(query)
            checker_1 = curr.fetchone()[0]

            if checker_1 == 1:
                st.error("team has play home and away")
            else:
                query = "INSERT INTO match (id, first_team_name, first_team_score, second_team_name, second_team_score, created_at, updated_at) VALUES({}, '{}', {}, '{}', {}, '{}', '{}')".format(sf.next_id(), str(first_team_name), int(first_team_score), str(second_team_name), int(second_team_score), datetime.now(jakarta_tz), datetime.now(jakarta_tz))
                curr.execute(query)
                db.commit()
                
                if first_team_score > second_team_score:
                    # winner handle
                    winner(curr, first_team_name, first_team_score, second_team_score)

                    # loser handle
                    losser(curr, second_team_name, second_team_score, first_team_score)
                    db.commit()
                elif first_team_score < second_team_score:
                    # winner handle
                    winner(curr, second_team_name, second_team_score, first_team_score)

                    # loser handle
                    losser(curr, first_team_name, first_team_score, second_team_score)
                    db.commit()
                else:
                    # draw
                    draw(curr, first_team_name, first_team_score)

                    draw(curr, second_team_name, second_team_score)
                    db.commit()

st.divider()
if st.sidebar.header("match"):
    st.header("Match")
    curr = db.cursor()
    query = "SELECT first_team_name, second_team_name, first_team_score, second_team_score FROM match"
    curr.execute(query)
    data_match = curr.fetchall()
    
    col_1, col_2, col_3, col_4 = st.columns(4)
    col_list = [col_1, col_2, col_3, col_4]
    total_match = len(data_match)
    for idx, dm in enumerate(data_match):
        if idx+1 <= (total_match/2):
            col_1.caption("match result")
            col_2.caption(idx+1)
            for i in range(2):
                for k in range(2):
                    if i == 0:
                        col_list[i].text(dm[k])
                    if i == 1:
                        col_list[i].text(dm[k+2])
        else:
            col_3.caption("match result")
            col_4.caption(idx+1)
            for i in range(2):
                for k in range(2):
                    if i == 0:
                        col_list[i+2].text(dm[k])
                    if i == 1:
                        col_list[i+2].text(dm[k+2])

st.divider()
if st.sidebar.header("leaderboard"):
    st.header("Leaderboard")
    query = "SELECT team_name, play, win, loss, draw, point, goals_for, goals_against, goals_difference FROM leaderboard_view"
    curr = db.cursor()
    curr.execute(query)
    leaderboard = curr.fetchall()
    leaderboard = pd.DataFrame(leaderboard, columns=["Team", "MP", "W", "L", "D", "Pts", "GF", "GA", "GD"], index=np.arange(1, len(leaderboard)+1))
    db.commit()
    st.table(leaderboard)