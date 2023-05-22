from app.models import User, Role, Transactions

def test_new_roles():
    """
    GIVEN a Role model,
    WHEN a new role is desired,
    CHECK if name is defined correctly
    """
    role = Role(name='new_role')
    assert role.name == 'new_role'
    
    

def test_new_user():
    """
    GIVEN a User model, 
    WHEN a User is created 
    THEN check email, hash_password, first_name, last_name, role_id and password_hash fields are defined correctly
    """
    user = User(first_name='John', last_name='Doe', email='Johndoe@email.com', role_id=2)
    user.set_password('password')
    assert user.first_name == 'John'
    assert user.last_name == 'Doe'
    assert user.email == 'Johndoe@email.com'
    assert user.role_id == 2
    assert user.password_hash != 'password'
     
    