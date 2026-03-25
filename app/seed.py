from app.database import SessionLocal
from app.models import Agent, Channel, Team


def seed_data():
    db = SessionLocal()
    try:
        if db.query(Channel).count() == 0:
            channels = [
                Channel(channel_id=440334, name="Whatsapp ATC"),
                Channel(channel_id=467245, name="Whatsapp ATC"),
                Channel(channel_id=440986, name="Whatsapp Comercial"),
                Channel(channel_id=440224, name="Facebook"),
                Channel(channel_id=440258, name="Instagram"),
                Channel(channel_id=440264, name="TikTok"),
                Channel(channel_id=418328, name="Telegram"),
            ]
            db.add_all(channels)

        if db.query(Agent).count() == 0:
            agents = [
                Agent(agent_id=905321, name="ai_agent", agent_type="ai_agent"),
                Agent(agent_id=967370, name="Alessandra Barrios"),
                Agent(agent_id=965224, name="Daniela Vielma"),
                Agent(agent_id=965216, name="Vicente Benitez"),
                Agent(agent_id=965199, name="Alex Guzman"),
                Agent(agent_id=941623, name="Yusely Azuaje"),
                Agent(agent_id=967369, name="Ana Ruiz"),
                Agent(agent_id=851848, name="Giorgina Gonzalez"),
                Agent(agent_id=965205, name="Emilis Sanchez"),
                Agent(agent_id=965704, name="Alanis Acosta"),
                Agent(agent_id=965207, name="Enyely Hernández"),
                Agent(agent_id=965705, name="Atencion al cliente"),
                Agent(agent_id=1037754, name="Gabriel Noguera"),
                Agent(agent_id=836373, name="JOSE ANGEL MELENDEZ"),
                Agent(agent_id=963022, name="Richard White"),
                Agent(agent_id=965218, name="David Morales"),
                Agent(agent_id=965755, name="Alexander Vasquez"),
                Agent(agent_id=965779, name="Mercadeo LibrePago"),
                Agent(agent_id=972390, name="Adrian Marquez"),
            ]
            db.add_all(agents)

        if db.query(Team).count() == 0:
            teams = [
                Team(team_id=34369, name="ATC"),
                Team(team_id=34367, name="Comercial"),
                Team(team_id=34370, name="Operaciones"),
                Team(team_id=34218, name="Test"),
            ]
            db.add_all(teams)

        db.commit()
        print("Seed data inserted successfully")
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
