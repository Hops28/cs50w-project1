import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def main():
    f = open("books.csv")
    reader = csv.reader(f)
    i = 1
    for isbn, title, author, year in reader:

        if title == "title":
            print("No")
        else:
            # if ':' in title:
            #    title.replace(":", " =")

            db.execute("""INSERT INTO "Book" ("ISBN", "Title", "Author", "YearB") VALUES (:isbn, :title, :author, :yearb)""", {"isbn" : isbn, "title" : title, "author" : author, "yearb" : year})

            print(f"Added Book {i} - {isbn} - {title} - {author} - {year}")
            i = i + 1
            db.commit()


if __name__ == "__main__":
    main()
