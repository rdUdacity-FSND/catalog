from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Category, Item

engine = create_engine('sqlite:///cat_app_data.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Some inital data for our database
# Create dummy user
User1 = User(username="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')  # noqa
userpw = User1.hash_password('TestPass')
User1.hashed_password = userpw
session.add(User1)
session.commit()


# Create some categories
category = Category(name="TestCategory1", user_id=1)
session.add(category)
session.commit()

category = Category(name="TestCategory2", user_id=1)
session.add(category)
session.commit()

category = Category(name="TestCategory3", user_id=1)
session.add(category)
session.commit()

category = Category(name="TestCategory4", user_id=1)
session.add(category)
session.commit()

category = Category(name="TestCategory5", user_id=1)
session.add(category)
session.commit()

category = Category(name="TestCategory6", user_id=1)
session.add(category)
session.commit()

category = Category(name="TestCategory7", user_id=1)
session.add(category)
session.commit()

category = Category(name="Misc.", user_id=1)
session.add(category)
session.commit()

# Create some items
item = Item(title='TestItem1',
            description='Test description one.',
            category_id=1,
            user_id=1)
session.add(item)
session.commit()

item = Item(title='TestItem2',
            description='Test description two.',
            category_id=1,
            user_id=1)
session.add(item)
session.commit()

item = Item(title='TestItem3',
            description='Test description three.',
            category_id=1,
            user_id=1)
session.add(item)
session.commit()

item = Item(title='TestItem4',
            description='Test description four.',
            category_id=2,
            user_id=1)
session.add(item)
session.commit()

item = Item(title='TestItem5',
            description='Test description five.',
            category_id=2,
            user_id=1)
session.add(item)
session.commit()

item = Item(title='TestItem6',
            description='Test description six.',
            category_id=3,
            user_id=1)
session.add(item)
session.commit()

item = Item(title='TestItem7',
            description='Test description seven.',
            category_id=3,
            user_id=1)
session.add(item)
session.commit()

item = Item(title='TestItem8',
            description='Test description eight',
            category_id=3,
            user_id=1)
session.add(item)
session.commit()

item = Item(title='TestItem9',
            description='Test description nine.',
            category_id=4,
            user_id=1)
session.add(item)
session.commit()

item = Item(title='TestItem10',
            description='Test description ten.',
            category_id=4,
            user_id=1)
session.add(item)
session.commit()

item = Item(title='TestItem11',
            description='Test description eleven.',
            category_id=5,
            user_id=1)
session.add(item)
session.commit()

item = Item(title='TestItem12',
            description='Test description twelve.',
            category_id=6,
            user_id=1)
session.add(item)
session.commit()

item = Item(title='TestItem13',
            description='Test description thirteen.',
            category_id=6,
            user_id=1)
session.add(item)
session.commit()

item = Item(title='TestItem14',
            description='Test description fourteen.',
            category_id=7,
            user_id=1)
session.add(item)
session.commit()

item = Item(title='TestItem15',
            description='Test description fifteen.',
            category_id=7,
            user_id=1)
session.add(item)
session.commit()

item = Item(title='TestItem16',
            description='Test description sixteen.',
            category_id=7,
            user_id=1)
session.add(item)
session.commit()


print "All test data added"
