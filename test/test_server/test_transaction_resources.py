import datetime
import json
from unittest import TestCase

import mysql.connector
import requests

import transactions.transaction as trn

target = "http://127.0.0.1:5000/"


class TestTransactionResources(TestCase):
    def test_get(self):
        """Ensures get request returns transaction object in the correct format"""

        tests = ["Get an existing transaction", "Transaction doesn't exist"]
        params = ["transaction/1", "transaction/1234523145"]
        expected = [
            (
                '{"transaction_id": 1, '
                '"src_id": 1, '
                '"dest_id": 2, '
                '"src": "Alice _", '
                '"dest": "Bob _", '
                '"amount": 10, '
                '"description": "test", '
                '"due_date": "2023-02-17", '
                '"paid": "false", '
                '"household_id": 1'
                '}',
                200,
            ),
            (
                "Couldn't find transaction in the database; likely due to invalid transaction ID",
                404,
            ),
        ]

        for test, param, expect in zip(tests, params, expected):
            with self.subTest(test):
                got = requests.get(target + param)
                self.assertEqual((got.json(), got.status_code), expect)

    def test_post(self):
        # create a cursor
        conn = mysql.connector.connect(
            host="localhost", user="root", password="HALR0b0t!12", database="x5db"
        )
        db = conn.cursor()

        # make a test transaction
        exp = trn.Transaction.build_from_id(transaction_id=1, cur=db)

        # make transaction from dest -> src instead of src -> dest. Double amount owed
        # these are arbitrary changes to guarantee different transaction
        exp.src_id, exp.dest_id = exp.dest_id, exp.src_id
        exp.amount *= 2

        # add the newly modified transaction to the database
        r = requests.post(
            "http://127.0.0.1:5000/transaction",
            json=exp.json,
            headers={"Content-Type": "application/json"},
        )

        if not (200 <= r.status_code < 300):
            self.fail(f"Error {r.status_code}")

        with self.subTest("add to db"):
            got = trn.Transaction.build_from_req(request=json.loads(r.json()))
            self.assertTrue(got.equal(exp))

        with self.subTest("attempt to add with incorrect json"):
            got = requests.post(
                "http://127.0.0.1:5000/transaction", json='{"Should": "Fail"}'
            )
            self.assertEqual(got.status_code, 400)
            self.assertEqual(got.json(), "Incorrect JSON Format for Transaction object")

    def test_patch(self):
        """Checks that we toggle paid and unpaid properly. Done by reading off a transaction and storing it,
        then sending the patch request, then reading off the same transaction. The 'before' and 'after'
        transactions are compared. Test passes if paid is different and every other field is the same
        """

        # FIXME: Database updates with the patch command, but after request still provides the un-updated value for
        #  paid. Very confusing

        # create a cursor
        conn = mysql.connector.connect(
            host="localhost", user="root", password="HALR0b0t!12", database="x5db"
        )

        db = conn.cursor()

        # store transaction 2
        before = trn.Transaction.build_from_id(transaction_id=2, cur=db)

        requests.patch(target + "transaction/2")

        # get new status of paid directly from db
        db.execute("""SELECT paid FROM transaction WHERE id = %s""", [before.t_id])
        paid_status = db.fetchall()[0]
        conn.commit()

        # build after object to compare before object with; overwrite paid status with one calculated above
        after = trn.Transaction.build_from_id(transaction_id=2, cur=db)
        after.paid = paid_status

        with self.subTest("paid has changed"):
            self.assertNotEqual(before.paid, after.paid)

        with self.subTest("other fields unchanged"):
            self.assertEqual(
                [v for v in before.__dict__][:-1], [v for v in after.__dict__][:-1]
            )

        with self.subTest("transaction not found"):
            r = requests.patch(target + "transaction/2000000000")
            self.assertEqual(r.status_code, 404)

    def test_delete(self):
        """Add a transaction. Delete the transaction."""
        now = datetime.datetime.now()
        temp_transaction = trn.Transaction(
            0,
            1,
            2,
            "",
            "",
            1,
            "test delete",
            datetime.datetime.fromisoformat(now.isoformat()),
            False,
            1
        )
        r = requests.post(
            "http://127.0.0.1:5000/transaction",
            json=temp_transaction.json,
            headers={"Content-Type": "application/json"},
        )
        new_id = json.loads(r.json())["transaction_id"]

        with self.subTest("delete transaction that exists"):
            r = requests.delete(f"http://127.0.0.1:5000/transaction/{new_id[0]}")
            self.assertEqual(r.status_code, 200)

            r = requests.delete("http://127.0.0.1:5000/transaction/2000000")
            self.assertEqual(r.status_code, 402)
