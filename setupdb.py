from userflask import db
from models import User

db.create_all()

admin = User('admin', 'admin@example.com', "dsadasdsa")

db.session.add(admin)

db.session.commit()

