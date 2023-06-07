from app_imports import *
from app_figs import *


class CustomCard(dbc.Card):
    def __init__(self, body=[], header=[], footer=[]):
        children = []
        if header: children+=[dbc.CardHeader(header)]
        if body: children+=[dbc.CardBody(body)]
        if footer: children+=[dbc.CardFooter(footer)]
        super().__init__(children)


class MemberNameCard(CustomCard):
    def __init__(self):
        super().__init__(
            body=[self.input_member],
            header=['Select members by name']
        )

    @cached_property
    def input_member(self):
        return dcc.Dropdown(
        options = [dict(value=idx, label=lbl) for idx,lbl in zip(Members().data.index, Members().data.sort_name)],
        value = [],
        multi=True,
        placeholder='Select individual members'
    )



class MemberDOBCard(dbc.Card):
    def __init__(self):
        super().__init__(
            header = ["Filter by date of birth"],
            body = [
                self.button_clear_dob,
            ]
        )

    @cached_property
    def graph_members_dob(self):
        return dcc.Graph(figure=plot_members_dob())

    @cached_property
    def button_clear_dob(self):
        return dbc.Button(
            "Clear", 
            color="link", 
            n_clicks=0
        )

member_gender_card = dbc.Card([
    dbc.CardHeader("Filter by member gender"),
    dbc.CardBody(
        input_gender := dbc.Checklist(
            options=gender_series,
            value=[],
            switch=True,
        )
    )
])

member_filter_card = dbc.Card([
    dbc.CardHeader('Filter for members currently being applied'),
    dbc.CardBody(
        member_filter_pre := html.Pre('[none]')
    )
])

member_map_card = dbc.Card([
    dbc.CardHeader('Map of members’ apartments in Paris'), 
    dbc.CardBody(map_members := dcc.Graph(figure=plot_members_map()))
])

member_tbl_card = dbc.Card([
    dbc.CardHeader('Data on the filtered members'),
    dbc.CardBody(tbl_members := dbc.Container())
])