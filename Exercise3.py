from sqlalchemy import create_engine,  update
from sqlalchemy.orm import sessionmaker
from Exercise1 import Base, LCA, LCAComponent, Impact, Source


engine = create_engine('sqlite:///life_cycle.db', echo=True)

Session = sessionmaker(bind=engine)
session = Session()


# A function to retrieve the last LcaComponents of a chain of LcaComponents for a particular phase (example, a1).
# Justificación: Filtrar por los Inmpact que relacionan el Componente con Source, que serán los "nodos hoja"
# # Anotación: 
# El orden del join y el filtro no afecta al rendimiento en SQL Alchemy, la base de datos hace la consulta más optima
# # https://stackoverflow.com/questions/43668752/in-sqlalchemy-is-a-filter-applied-before-or-after-a-join 

def get_last_components(list_lcac: list, phase_name: str) -> list:

    lcac_ids = [lcac.id for lcac in list_lcac]

    return session.query(LCAComponent)\
        .join(Impact, LCAComponent.id == Impact.lcac_id)\
        .filter(LCAComponent.phase_type==phase_name)\
        .filter(Impact.source_type=='DB')\
        .filter(LCAComponent.id.in_(lcac_ids))


select_phase = get_last_components(session.query(LCAComponent).all(), 'A1')
for row in select_phase:
    print(row.id, row.phase_type, row.quantity, row.unit)


# A function to update the impacts of a particular LcaComponent with a fixed value
# Update en bulk en lugar de usar bucle for
def update_lcac_impacts(lcac: LCAComponent, value:float) -> bool:  

    try: 
        stmt = (
            update(Impact).where(
                Impact.lcac_id == lcac.id
            ).values(
                value=value
            )
        )
        session.execute(stmt)
        session.commit()
    
    except Exception as e:
        print(f'[ERROR] Could not complete update: {e}')
        return False

    return True

parent = session.query(LCAComponent).filter(LCAComponent.id==1).first()
update_lcac_impacts(parent, 0.0231)

# Exercise 3

#Formula del impacto = (Quantity (units) * Impact_Value (%) * 100)

# Impacto padre = Hijo1(Quantity * Impact_value) + Hijo2(Quantity * Impact_value)
# Partimos de la base que el sumatorio del value de los impacts de los hijos no será superior a 1 (100%)
# Al ser una estructura de N niveles, se  debe recorrer de manera recursiva

# En lugar de hacer  una query por cada nivel/ iteración, obtener todos los valores en un  df para ir calculando los datos y trabajar sobre esta
    
def recursive_impact(parent_id):
    
    child_impacts = session.query(Impact)\
    .filter(Impact.lcac_id==parent_id)
    
    total_impact = 0
    for child_im in child_impacts:
    
        # Nodo "Hoja" (Caso base)
        if child_im.child_lcac_id is None:
            
            impact = child_im.value
            
            quantity = session.query(LCAComponent).filter(
                LCAComponent.id==child_im.lcac_id
            ).first().quantity
            
            print('---> Hoja ', impact, quantity)
            
            total_impact += impact * quantity
        
        # Nodo Rama (Caso recursivo)
        else:
            print('Rama: ', child_im.child_lcac_id)
            total_impact += recursive_impact(child_im.child_lcac_id)

    
    return total_impact / child_impacts.count()

def calculate_impact(parent_id):
    return recursive_impact(parent_id)

print(calculate_impact(parent.lca_id))
