from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup_catalog import Category, Base, CategoryItem

#engine = create_engine('sqlite:///catalog.db')
engine = create_engine('postgresql://catalog:catalog@localhost/catalog')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# New category Soccer
category1 = Category(name="Soccer")

session.add(category1)
session.commit()

# Items under Soccer
categoryItem1 = CategoryItem(
  name="Shinguards",
  description="Shinguards are use to protect the shins",
  category=category1)

session.add(categoryItem1)
session.commit()


categoryItem2 = CategoryItem(
  name="Two shinguards",
  description="Pair of Shinguards",
  category=category1)

session.add(categoryItem2)
session.commit()


# New Category Snowboarding
category2 = Category(name="Snowboarding")

session.add(category2)
session.commit()

# Items under Snowboarding
catItem1 = CategoryItem(
  name="Goggles",
  description="Goggles for snowboarding",
  category=category2)

session.add(catItem1)
session.commit()

catItem2 = CategoryItem(
  name="Snowboards",
  description="Best for any terrain and conditions. All mountain snowboards ",
  category=category2)

session.add(catItem2)
session.commit()


# New Category Tennis
category3 = Category(name="Tennis")

session.add(category3)
session.commit()

# Items under Tennis
catItem1 = CategoryItem(
  name="Racket",
  description="Best Tennis racket in the world",
  category=category3)

session.add(catItem1)
session.commit()


# New Category Cricket
category4 = Category(name="Cricket")

session.add(category4)
session.commit()

# Items under Tennis
catItem1 = CategoryItem(
  name="Bat",
  description="Bat authorized by the Master himself",
  category=category4)

session.add(catItem1)
session.commit()

catItem2 = CategoryItem(
  name="Balls",
  description="Kookaburra balls",
  category=category4)

session.add(catItem2)
session.commit()

catItem3 = CategoryItem(
  name="Pads and gloves",
  description="Pads and gloves for maximum safety",
  category=category4)

session.add(catItem3)
session.commit()


# New Category Rugby
category5 = Category(name="Hockey")

session.add(category5)
session.commit()

catItem1 = CategoryItem(
  name="Stick",
  description="Field Hockey Stick",
  category=category5)

session.add(catItem1)
session.commit()


print"Added catalog categories and items!"
