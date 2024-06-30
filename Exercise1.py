from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import pandas as pd

engine = create_engine('sqlite:///life_cycle.db', echo=True)
Base = declarative_base()

# LCA: Agrupa un conjunto de LCA Componentes
class LCA(Base):
    __tablename__ = 'LCA'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String)

    components = relationship('LCAComponent', backref='lca')

# LCAComponent: Forma parte de un LCA y es una fase de dicho ciclo. Cuenta con Quantity y Units. 
#      - Está compuesto por Impacts
class LCAComponent(Base):
    __tablename__ = 'LCAComponent'

    id = Column(Integer, primary_key=True, autoincrement=True)
    lca_id = Column(Integer, ForeignKey('LCA.id'), nullable=False)
    phase_type = Column(String)
    quantity = Column(Integer)
    unit = Column(String)

    # Impact usa 2 FK a  LCAComponent, usar primaryjoin
    impacts = relationship('Impact', primaryjoin='LCAComponent.id == Impact.lcac_id', backref='lca_component')


class Source(Base):
    __tablename__ = 'Source'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    lcac_name = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    db_version = Column(String)


# Impact: Interfaz que usa LCAComponent  para "conectar" con otro LCAComponent o con un Source
#      - Está compuesto por Impacts

class Impact(Base):
    __tablename__ = 'Impact'

    id = Column(Integer, primary_key=True, autoincrement=True)
    lcac_id = Column(Integer, ForeignKey('LCAComponent.id'), nullable=False)
    source_id =  Column(Integer, ForeignKey('Source.id'), nullable=True)
    child_lcac_id = Column(Integer, ForeignKey('LCAComponent.id'), nullable=True)

    impact_category = Column(String)
    value = Column(Float)
    source_type = Column(Enum('DB', 'LCA'))

    source = relationship('Source', foreign_keys=[source_id])
    child_lcac = relationship('LCAComponent', foreign_keys=[child_lcac_id])


# Un LCA puede contener muchos LCAComponent
# Un LCAComponent puede tener muchos Impacts
# Un Impact puede tener un child_lcac o bien un source_id, pero los dos a la vez no 

# Reinicializar cada vez qe se ejecuta el script
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

lca1 = LCA(name='LCA Spermercados Día', description='Ejemplo LCA')
session.add(lca1)
session.commit()

#lcac_a1 = LCAComponent(lca_id=lca1.id, phase_type='A1 Extraccion Materia Prima', quantity=0.02, unit='kg')

lcac_a1 = LCAComponent(lca_id=lca1.id, phase_type='A1', quantity=0.02, unit='kg')
lcac_a1_1 = LCAComponent(lca_id=lca1.id, phase_type='A1', quantity=0.01, unit='kg')
lcac_a1_2 = LCAComponent(lca_id=lca1.id, phase_type='A1', quantity=0.01, unit='kg')

lcac_a2 = LCAComponent(lca_id=lca1.id, phase_type='A2', quantity=0.0035, unit='ton kg')
lcac_a3 = LCAComponent(lca_id=lca1.id, phase_type='A3', quantity=0.0066, unit='kWh')

session.add_all([lcac_a1, lcac_a1_1, lcac_a1_2, lcac_a2, lcac_a3])
session.commit()

s_a1_1 = Source(name='Hierro', lcac_name='A1_Source', unit='kg', db_version='1.0')
s_a1_2 = Source(name='Acero', lcac_name='A1_Source', unit='g', db_version='1.0')
s_a2_0 =   Source(name='Gasolina', lcac_name='A2_Source', unit='ton  kg', db_version='1.0')
s_a3_0 =   Source(name='Electricidad', lcac_name='A3_Source', unit='kWh', db_version='1.0')
session.add_all([s_a1_1, s_a1_2, s_a2_0, s_a3_0])
session.commit()


# Add relation Impacts

# LCA -> LCA (Child)
impact_a1_1 = Impact(lcac_id=lcac_a1.id, impact_category='A1', value=0.002, source_type='LCA', child_lcac_id=lcac_a1_1.id)
impact_a1_2 = Impact(lcac_id=lcac_a1.id, impact_category='A1', value=0.001, source_type='LCA', child_lcac_id=lcac_a1_2.id)

# LCA (Child) -> Sorce DB 
impact1_1 = Impact(lcac_id=lcac_a1_1.id, impact_category='A1_1', value=0.02, source_type='DB', source_id=s_a1_1.id)
impact1_2 = Impact(lcac_id=lcac_a1_2.id, impact_category='A1_2', value=0.02, source_type='DB', source_id=s_a1_2.id)

# LCA -> Source
impact2 = Impact(lcac_id=lcac_a2.id, impact_category='A2', value=0.0035, source_type='DB',source_id=s_a2_0.id)
impact3 = Impact(lcac_id=lcac_a3.id, impact_category='A3', value=0.0066, source_type='DB', source_id=s_a3_0.id)

session.add_all([impact_a1_1, impact_a1_2, impact1_1, impact1_2, impact2, impact3])
session.commit()


