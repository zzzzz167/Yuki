from utils import database

from peewee_migrate import Router

database.db.connect()

router = Router(database.db, ignore='basemodel')

router.create(auto=database)
router.run()

database.db.close()
