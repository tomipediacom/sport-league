-- table user
CREATE TABLE IF NOT EXISTS "user"(
  id bigint,
  name varchar,
  created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamptz,
  deleted_at timestamptz,
  team_name varchar,
  PRIMARY KEY(id, team_name)
);

-- table leaderboard
CREATE TABLE IF NOT EXISTS leaderboard(
  team_name varchar PRIMARY KEY,
  play integer DEFAULT 0,
  win integer DEFAULT 0,
  loss integer DEFAULT 0,
  draw integer DEFAULT 0,
  goals_for integer DEFAULT 0,
  goals_against integer DEFAULT 0,
);

-- leaderboard view
CREATE OR REPLACE VIEW leaderboard_view AS 
SELECT
  team_name,
  play,
  win,
  loss,
  draw,
  (win*3 + draw*1) point,
  goals_for,
  goals_against,
  (goals_for - goals_against) goals_difference
FROM leaderboard
ORDER BY 
  point DESC,
  goals_difference DESC,
  goals_against ASC;

-- table match
CREATE TABLE IF NOT EXISTS match(
  id bigint PRIMARY KEY,
  first_team_name varchar,
  first_team_score integer,
  second_team_name varchar,
  second_team_score integer,
  created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamptz,
  deleted_at timestamptz,
);