from app_imports import *


@callback(
    [
        Output('members-map', "figure"),
        Output('members-tbl', 'children')
    ],
    [
        Input('member-gender', 'value'),
        Input('is_expat', 'value'),
        Input('member-generation', 'value'),
        
        # Input('dropdown-nation', 'value'),
        # Input('dropdown-gender', 'value'),
    ],
    [
        State('members-map', 'figure'),
    ],
    prevent_initial_call=True
)
def update_map_and_table(gender, is_expat, generation, member_fig):
    dff = get_total_data_members()
    if gender:
        dff = dff[dff.gender.isin(gender)]
    if is_expat:
        dff = dff[dff.is_expat.apply(str).isin(is_expat)]
    if generation:
        print(generation,"?")
        print(dff.columns)
        dff = dff[dff.generation.fillna('').isin(generation)]

    # members = set(dff.member_id)
    # df_tbl = get_total_data_members()
    # df_tbl = df_tbl[df_tbl.member_id.isin(members)]

    fig = go.Figure(data=DashMembersMap(dff).data, layout=go.Figure(member_fig).layout)
    return fig, DashMembersDataTable(dff)

