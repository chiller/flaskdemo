from userflask import db, User

db.create_all()

admin = User('admin', 'admin@example.com', "dsadasdsa")

db.session.add(admin)

db.session.commit()

