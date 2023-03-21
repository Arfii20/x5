"""Endpoints for transactions"""
import flask_restful  # type: ignore

import server.transactions.ledger_resource
import server.transactions.transaction_resources as tr
import server.shared_calendar.shared_calendar as calendar
import server.shared_list.shared_list as lists
import server.shared_list.user_profile as profile



def attach(api: flask_restful.Api):
    """Attaches all endpoints to the flask app"""
    # calendar
    api.add_resource(calendar.GetSharedCalendar, "/get_shared_calendar/<int:household_id>")
    api.add_resource(calendar.SharedCalendar, "/shared_calendar/<int:household_id>")
    api.add_resource(calendar.CalendarEvent, "/calendar_event/<int:calendar_event_id>")
    api.add_resource(calendar.UserAttributes, "/user_attributes/<int:household_id>")

    # list
    api.add_resource(lists.SharedList, "/shared_list/<int:household_id>")
    api.add_resource(lists.ListDetails, "/list_details/<int:list_id>")
    api.add_resource(lists.ListEvents, "/list_events/<int:list_id>")
    api.add_resource(lists.ListEventDetails, "/list_event_details/<int:list_event_id>")

    # transactions
    api.add_resource(tr.TransactionResource, "/transaction/<int:t_id>", "/transaction")
    api.add_resource(server.transactions.ledger_resource.LedgerResource, "/ledger/<int:user_id>")

    # profile
    api.add_resource(profile.UserProfile, "/user_profile/<int:user_id>")
