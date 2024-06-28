# main.py (actualizado)
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Crear un motor de base de datos SQLite en un archivo
engine = create_engine('sqlite:///database.db', echo=True)

# Definir la base de datos
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)

class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    email_address = Column(String, nullable=False)
    user = relationship("User", back_populates="addresses")

User.addresses = relationship("Address", order_by=Address.id, back_populates="user")

# Crear las tablas en la base de datos
Base.metadata.create_all(engine)

# Crear una sesión
Session = sessionmaker(bind=engine)
session = Session()

# Añadir un nuevo usuario
new_user = User(name='Alice', age=25)
session.add(new_user)
session.commit()

# Añadir una nueva dirección para el usuario
new_address = Address(email_address="alice@example.com", user=new_user)
session.add(new_address)
session.commit()

# Consultar usuarios y sus direcciones
for user in session.query(User).all():
    print(user.name, user.age)
    for address in user.addresses:
        print(address.email_address)
