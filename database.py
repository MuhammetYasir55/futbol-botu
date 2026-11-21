
import sqlite3


class Database:

    def __init__(self):
        self.connection = sqlite3.connect("futbol.db")
        self.cursor = self.connection.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                team_id INTEGER DEFAULT NULL,
                points INTEGER DEFAULT 0
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                team_id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT UNIQUE NOT NULL,
                captain_id INTEGER NOT NULL
            )
        """)

        self.connection.commit()

    # Oyuncu kaydet
    def register_player(self, user_id, username):
        self.cursor.execute(
            "SELECT user_id FROM players WHERE user_id = ?",
            (user_id,)
        )

        if self.cursor.fetchone():
            return False

        self.cursor.execute("""
            INSERT INTO players (user_id, username, points)
            VALUES (?, ?, 100)
        """, (user_id, username))

        self.connection.commit()
        return True

    # Oyuncu bilgilerini getir
    def get_player(self, user_id):
        self.cursor.execute("""
            SELECT user_id, username, team_id, points
            FROM players
            WHERE user_id = ?
        """, (user_id,))

        return self.cursor.fetchone()

    # Oyuncunun reytingini getir
    def get_rating(self, points):
        if points >= 1500:
            return "Efsane"
        elif points >= 1000:
            return "Elmas"
        elif points >= 500:
            return "Altin"
        elif points >= 200:
            return "Gumus"
        else:
            return "Bronz"

    # Oyuncuya puan ekle
    def add_points(self, user_id, points):
        self.cursor.execute("""
            UPDATE players
            SET points = points + ?
            WHERE user_id = ?
        """, (points, user_id))

        self.connection.commit()

    # Oyuncuları listele
    def get_players(self):
        self.cursor.execute("""
            SELECT username, team_id, points
            FROM players
            ORDER BY points DESC
        """)

        return self.cursor.fetchall()

    # Takım oluştur
    def create_team(self, team_name, captain_id):
        player = self.get_player(captain_id)

        if player is None:
            return "not_registered"

        if player[2] is not None:
            return "already_in_team"

        self.cursor.execute("""
            SELECT team_id FROM teams
            WHERE team_name = ?
        """, (team_name,))

        if self.cursor.fetchone():
            return "team_exists"

        self.cursor.execute("""
            INSERT INTO teams (team_name, captain_id)
            VALUES (?, ?)
        """, (team_name, captain_id))

        team_id = self.cursor.lastrowid

        self.cursor.execute("""
            UPDATE players
            SET team_id = ?, points = points + 50
            WHERE user_id = ?
        """, (team_id, captain_id))

        self.connection.commit()
        return "success"

    # Takıma katıl
    def join_team(self, team_name, user_id):
        player = self.get_player(user_id)

        if player is None:
            return "not_registered"

        if player[2] is not None:
            return "already_in_team"

        self.cursor.execute("""
            SELECT team_id FROM teams
            WHERE team_name = ?
        """, (team_name,))

        team = self.cursor.fetchone()

        if team is None:
            return "team_not_found"

        self.cursor.execute("""
            UPDATE players
            SET team_id = ?
            WHERE user_id = ?
        """, (team[0], user_id))

        self.connection.commit()
        return "success"

    # Oyuncunun takımını getir
    def get_team(self, user_id):
        self.cursor.execute("""
            SELECT teams.team_id,
                   teams.team_name,
                   teams.captain_id
            FROM players
            JOIN teams ON players.team_id = teams.team_id
            WHERE players.user_id = ?
        """, (user_id,))

        return self.cursor.fetchone()

    # Takım üyelerini getir
    def get_team_members(self, team_id):
        self.cursor.execute("""
            SELECT username, user_id, points
            FROM players
            WHERE team_id = ?
            ORDER BY points DESC
        """, (team_id,))

        return self.cursor.fetchall()

    # Takım toplam puanı
    def get_team_points(self, team_id):
        self.cursor.execute("""
            SELECT SUM(points)
            FROM players
            WHERE team_id = ?
        """, (team_id,))

        result = self.cursor.fetchone()[0]
        return result if result is not None else 0

    # Maç sonucuna göre puan ver
    def finish_match(self, team1_id, team2_id, result):
        if result not in ("team1", "team2", "draw"):
            return False

        self.cursor.execute("""
            SELECT team_id FROM teams
            WHERE team_id IN (?, ?)
        """, (team1_id, team2_id))

        if len(self.cursor.fetchall()) != 2 or team1_id == team2_id:
            return False

        if result == "draw":
            self.cursor.execute("""
                UPDATE players SET points = points + 10
                WHERE team_id IN (?, ?)
            """, (team1_id, team2_id))

        else:
            winner = team1_id if result == "team1" else team2_id

            self.cursor.execute("""
                UPDATE players SET points = points + 30
                WHERE team_id = ?
            """, (winner,))

        self.connection.commit()
        return True


database = Database()
