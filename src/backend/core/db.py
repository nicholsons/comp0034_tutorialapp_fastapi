from importlib import resources

import pandas as pd
from sqlmodel import Session, create_engine, select, text

import data
from backend.models.models import *  # noqa

# Consider moving the URL to a .env file and using Settings
sqlite_file = resources.files(data).joinpath("paralympics.db")
sqlite_url = f"sqlite:///{sqlite_file}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args, echo=True)


def init_db(session: Session) -> None:
    """Initialize the database by creating tables and adding data if needed.

    Tables have been created with Alembic migrations

        Args:
            session
    """

    #  If you don't want to use alembic migrations,  un-comment the next lines to create the tables
    # from sqlmodel import SQLModel
    # SQLModel.metadata.create_all(engine)

    # Only add data if it does not already exist
    with session:
        games = session.exec(select(Games)).first()
        if not games:
            add_data(engine)


def _load_frames(data_file):
    df_games = pd.read_excel(data_file, sheet_name="games", keep_default_na=True)
    df_teams = pd.read_excel(data_file, sheet_name="team_codes", keep_default_na=True)
    return df_games, df_teams


def _normalize_games_frame(df_games):
    games_int_cols = ['year', 'participants_m', 'participants_f', 'participants', 'events',
                      'sports', 'countries']
    for col in games_int_cols:
        if col in df_games.columns:
            df_games[col] = pd.to_numeric(df_games[col], errors='coerce').astype('Int64')

    for col in ['latitude', 'longitude']:
        if col in df_games.columns:
            df_games[col] = pd.to_numeric(df_games[col], errors='coerce')

    for col in df_games.columns:
        if col.lower() in ('start', 'end') or 'date' in col.lower():
            df_games[col] = pd.to_datetime(df_games[col], errors='coerce').dt.strftime('%d-%m-%Y')


def _add_disabilities(engine, df_games):
    df_disability = (
        df_games['disabilities_included']
        .dropna()
        .astype(str)
        .str.split(',')
        .explode()
        .str.strip()
    )
    df_disability = df_disability[df_disability != ''].unique().tolist()
    with Session(engine) as session:
        for d in df_disability:
            dis = Disability(description=d)
            session.add(dis)
        session.commit()


def _add_countries_and_teams(engine, df_teams):
    for _, row in df_teams.iterrows():
        code = str(row.get('Code')).upper()
        member_type = str(row.get('MemberType', '')).strip().lower()
        team_name = row.get('TeamName').strip()
        region = row.get('Region') if 'Region' in row else None
        notes = row.get('Notes') if 'Notes' in row else None

        with Session(engine) as session:
            country_id = None

            if not pd.isna(team_name) or team_name != '':
                if member_type == 'country':
                    statement = select(Country).filter(Country.country_name == team_name)
                    country = session.exec(statement).first()
                    if not country:
                        country = Country(country_name=team_name)
                        session.add(country)
                        session.commit()
                        session.refresh(country)
                    country_id = country.id

            team = Team(
                code=code,
                name=str(team_name).strip(),
                region=region,
                notes=notes,
                member_type=member_type,
                country_id=country_id
            )
            session.add(team)
            session.commit()


def _add_hosts(engine, df_games):
    replacements = {
        "USA": "United States of America",
        "UK": "Great Britain",
        "China": "People's Republic of China",
        "Korea": "Republic of Korea",
        "Russia": "Russian Federation",
    }

    with Session(engine) as session:
        host_objs = []
        for _, row in df_games.iterrows():
            country_name = row.get('country_name')
            if pd.isna(country_name):
                continue
            country_name = str(country_name).strip()
            lookup_country = replacements.get(country_name, country_name)
            statement = select(Country).filter(Country.country_name == lookup_country)
            country = session.exec(statement).first()

            if not country:
                continue

            h = Host(place_name=row.get('host'), country_id=country.id,
                     latitude=row.get('latitude'), longitude=row.get('longitude'))
            host_objs.append(h)

        if host_objs:
            seen = set()
            unique_hosts = []
            for h in host_objs:
                key = (h.place_name, h.country_id)
                if key not in seen:
                    seen.add(key)
                    unique_hosts.append(h)
            session.add_all(unique_hosts)
            session.commit()


def _add_games_and_links(engine, df_games):
    with Session(engine) as session:
        for _, row in df_games.iterrows():
            def san(v):
                return None if pd.isna(v) else v

            g = Games(
                event_type=row.get('type').strip().lower(),
                year=row.get('year'),
                start_date=san(row.get('start')),
                end_date=san(row.get('end')),
                countries=san(row.get('countries')),
                events=san(row.get('events')),
                sports=san(row.get('sports')),
                participants_m=san(row.get('participants_m')),
                participants_f=san(row.get('participants_f')),
                participants=san(row.get('participants')),
                highlights=san(row.get('highlights')),
                url=san(row.get('URL'))
            )
            session.add(g)
            session.commit()
            session.refresh(g)
            games_id = g.id

            country_name = row.get('country')
            if not pd.isna(country_name):
                statement = select(Team).filter(Team.name == country_name)
                team = session.exec(statement).first()
                if team:
                    games_team = GamesTeam(games_id=games_id, team_id=team.code)
                    session.add(games_team)
                    session.commit()

            dis_val = row.get('disabilities_included')
            if not pd.isna(dis_val):
                dis_list = [d.strip() for d in str(dis_val).split(',') if d.strip()]
                games_dis_objs = []
                for dis_desc in dis_list:
                    statement = select(Disability).filter(Disability.description == dis_desc)
                    disability = session.exec(statement).first()
                    if disability:
                        games_dis_objs.append(
                            GamesDisability(games_id=games_id, disability_id=disability.id))
                    else:
                        new_dis = Disability(description=dis_desc)
                        session.add(new_dis)
                        session.commit()
                        session.refresh(new_dis)
                        games_dis_objs.append(
                            GamesDisability(games_id=games_id, disability_id=new_dis.id))
                if games_dis_objs:
                    session.add_all(games_dis_objs)
                    session.commit()

            host_val = row.get('host')
            if not pd.isna(host_val):
                host_names = [h.strip() for h in str(host_val).split(',') if h.strip()]
                games_host_objs = []
                for host_name in host_names:
                    statement = select(Host).filter(Host.place_name == host_name)
                    host = session.exec(statement).first()
                    if not host:
                        country_name = row.get('country')
                        country_id = None
                        if not pd.isna(country_name):
                            country_stmt = select(Country).filter(
                                Country.country_name == country_name)
                            country = session.exec(country_stmt).first()
                            if country:
                                country_id = country.id
                        host = Host(place_name=host_name, country_id=country_id)
                        session.add(host)
                        session.commit()
                        session.refresh(host)
                    games_host_objs.append(GamesHost(games_id=games_id, host_id=host.id))
                if games_host_objs:
                    session.add_all(games_host_objs)
                    session.commit()


def _run_sql_file(engine, filename):
    with Session(engine) as session:
        sql_file = resources.files(data).joinpath(filename)
        with open(sql_file, 'r') as f:
            sql_statements = f.read()
        for statement in sql_statements.split(';'):
            if statement.strip():
                session.exec(text(statement))
        session.commit()


def add_data(engine):
    """Add data to the database from Excel file and SQL files.

        Loads paralympics data from an Excel file, processes it, and populates
        the database tables.

        Args:
            engine:  SQLModel engine object
    """

    data_file = resources.files(data).joinpath("paralympics.xlsx")
    df_games, df_teams = _load_frames(data_file)
    _normalize_games_frame(df_games)
    _add_disabilities(engine, df_games)
    _add_countries_and_teams(engine, df_teams)
    _add_hosts(engine, df_games)
    _add_games_and_links(engine, df_games)
    _run_sql_file(engine, "question.sql")
    _run_sql_file(engine, "response.sql")
