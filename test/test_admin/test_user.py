import datetime
from unittest import TestCase
import mysql.connector

from admin.user import User, UserError

def setUpModule():
    """Check that first 7 rows of user db are as expected"""

    # connect to db
    conn = mysql.connector.connect(
        host="localhost", user="root", password="I_love_stew!12", database="x5db"
    )

    db = conn.cursor()

    db.execute("""SELECT * FROM user;""")

    # make sure that first 7 rows in db are as expected
    expected_user_table = [
        (1, "Alice", "_", "alice", "alice@alice.com", None, 1, None),
        (2, "Bob", "_", "bob", "bob@bob.com", None, 1, None),
        (3, "Test", "Ledger", "l", "l@l.com", datetime.date(1, 2, 2), 2, None),
        (4, "Test2", "Ledger", "l", "l@2.com", datetime.date(1, 1, 1), 2, None),
        (5, "Andrew", "Lees", "alees", "a@a.com", datetime.date(2023, 3, 13), 3, None),
        (6, "Bandicoot", "Crash", "bc", "b@c.com", datetime.date(2023, 3, 13), 3, None),
        (7, "Kez", "Carey", "kc", "k@c.com", datetime.date(2023, 3, 13), 3, None),
    ]

    received = db.fetchall()

    for exp, got in zip(expected_user_table, received):
        if exp != got:
            # if there is a discrepancy delete row and insert the correct row
            db.execute("UPDATE user "
                       "SET "
                       "first_name = %s, "
                       "surname = %s, "
                       "password = %s, "
                       "email = %s, "
                       "date_of_birth = %s, "
                       "household_id = %s, "
                       "color = %s "
                       "WHERE id=%s", [*exp[1:], exp[0]])

    # commit any changes
    conn.commit()

class TestUser(TestCase):

    def test_insert_to_database(self):
        # connect to db
        conn = mysql.connector.connect(
            host="localhost", user="root", password="I_love_stew!12", database="x5db"
        )

        db = conn.cursor()

        john = User(0, 'John', "Heereboys", "j@heere.com", b"test", datetime.date(1, 1, 1), None, None)
        john.insert_to_database(db, conn)

        del db
        cur2 = conn.cursor()

        # ensure that insert worked
        cur2.execute("""SELECT * FROM user WHERE email = %s""", ["j@heere.com"])

        got = cur2.fetchall()[0]

        with self.subTest("Insert"):
            self.assertEqual(got[1:], ('John', "Heereboys", "test", "j@heere.com", datetime.date(1, 1, 1), None, None))

        # cleanup
        cur2.execute("""DELETE FROM user WHERE id = %s""", [got[0]])
        conn.commit()

        # try to insert where an email adress already exists
        fail = User(0, 'John', "Heereboys", "l@l.com", b"test", datetime.date(1, 1, 1), None, None)

        with self.subTest("email exists"), self.assertRaises(UserError):
            fail.insert_to_database(cur2, conn)



    def test_join_household(self):

        # connect to db
        conn = mysql.connector.connect(
            host="localhost", user="root", password="I_love_stew!12", database="x5db"
        )

        db = conn.cursor()

        # create a user with no household and insert into db
        john = User(0, 'John', "Heereboys", "j@heere.com", b"test", datetime.date(1, 1, 1), None, None)
        john.insert_to_database(db, conn)

        john.join_household(2, db, conn)

        del db
        cur = conn.cursor()
        cur.execute("""SELECT household_id FROM user WHERE email = 'j@heere.com'""")

        self.assertEqual(cur.fetchone()[0], 2)

        cur.execute("""DELETE FROM user WHERE email = 'j@heere.com'""")
        conn.commit()



    def test_leave_household(self):
        ...

    def test_delete(self):
        ...

    def test_build_from_email(self):
        ...

    def test_build_from_id(self):
        ...

    def test_json(self):
        ...
