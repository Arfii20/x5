from __future__ import annotations

from dataclasses import dataclass
import datetime
import json
from mysql.connector import cursor


class TransactionConstructionError(Exception):
    """Triggered when a transaction failed to build from the database"""


@dataclass
class Transaction:
    """Specifies a singular transaction"""

    t_id: int
    src_id: int
    dest_id: int
    amount: int
    due: datetime.date
    paid: bool
    description: str = ""
    src_name: str = ""
    dest_name: str = ""

    @property
    def json(self) -> str:
        """Returns a JSON representation of transaction object of the format

         {   "src": <str:src full name>,
            "dest": <str:dest full name>,
            "amount": <int:amount>,
            "description": <str:description>
            "due_date": <str:date string in format yyyy-mm-dd>
            "paid": <str:boolean>
        }

        """

        return json.dumps(
            {
                "src": self.src_name,
                "dest": self.dest_name,
                "amount": self.amount,
                "description": self.description,
                "due_date": self.due.isoformat(),
                "paid": "true" if self.paid else "false",
            }
        )

    @staticmethod
    def build_from_id(*, transaction_id: int, cur: cursor.MySQLCursor) -> Transaction:
        """Builds a transaction from an id in the db and a cursor to said database"""

        cur.execute(
            "SELECT transaction.id, u1.id, u2.id, amount, due_date, paid, description,"
            "CONCAT_WS(' ', u1.first_name, u1.surname), CONCAT_WS(' ', u2.first_name, u2.surname) "
            "FROM transaction, pairs, user u1, user u2 "
            "WHERE transaction.id = %s AND pairs.id = transaction.pair_id"
            " AND u1.id = pairs.src AND u2.id = pairs.dest",
            [transaction_id],
        )

        # only one row will match an ID
        # throw an exception if no transaction returned
        # complain if None is returned

        if (row := cur.fetchone()) is None:
            raise TransactionConstructionError(
                "Couldn't find transaction in the database; "
                "likely due to invalid transaction ID"
            )
        else:
            args: list = [element for element in row]

        # args is in the form
        # [transaction_id: int, src_id: int, dest_id: int, amount: int, due_date: str, paid: int,
        # description: str, src_name: str, dest_name: str]

        # need to convert paid from int -> bool
        # do in place so can pass tuple directly into Transaction() instantiation

        args[5] = bool(args[5])

        return Transaction(*args)
