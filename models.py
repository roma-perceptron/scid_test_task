from sqlalchemy import Column, Integer, String, UUID, DATE, TIME, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# class FirstTable(Base):
#     __tablename__ = 'first_table'
#
#     id = Column(Integer, primary_key=True)
#     first_name = Column(String(32))
#     last_name = Column(String(32))
#     port = Column(Integer)
#
#
# class SecondTable(Base):
#     __tablename__ = 'second_table'
#
#     id = Column(Integer, primary_key=True)
#     public_id = Column(String(256))
#     date_of_birth = Column(DATE)
#     amount = Column(Integer)


# class Countries(Base):
#     __tablename__ = 'countries'
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String(32))
#     capital = Column(String(32))
#     president = Column(String(32))
#     territory = Column(Integer)
#     army = Column(Integer)

# ниже код моделей таблица для SQLAlchemy - перепиши для создания этих таблица на чистом SQL через mysql-connector-python

class Festival(Base):
    __tablename__ = 'festivals'
    #
    festival_id = Column(Integer, primary_key=True)
    name = Column(String(32))
    place = Column(String(32))
    date = Column(DATE)


class Band(Base):
    __tablename__ = 'bands'
    #
    band_id = Column(Integer, primary_key=True)
    name = Column(String(32))
    genre = Column(String(32))


class Schedule(Base):
    __tablename__ = 'schedules'
    #
    schedule_id = Column(Integer, primary_key=True, autoincrement=True)
    festival_id = Column(Integer, ForeignKey('festivals.festival_id'), primary_key=True, nullable=False)
    band_id = Column(Integer, ForeignKey('bands.band_id'), primary_key=True, nullable=False)
    time = Column(TIME, nullable=False)
    #
    band = relationship('Band')
    festival = relationship('Festival')





