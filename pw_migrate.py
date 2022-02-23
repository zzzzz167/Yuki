from utils.database import db

from peewee_migrate import Router

db.db.connect()

router = Router(db.db, ignore='basemodel')

router.create(auto=db)
router.run()

db.db.close()
