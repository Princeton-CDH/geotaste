from app_imports import *



# @callback(
#     [
#         Output('members-map', "figure"),
#         Output('members-table', 'children')
#     ],
#     [
#         Input('map_kind', 'value'),
#         # Input('dropdown-nation', 'value'),
#         # Input('dropdown-gender', 'value'),
#     ]
# )
# def update_map_and_table(map_kind):
#     dff = get_filtered_data_members(map_kind)
#     members = set(dff.member_id)
#     df_tbl = get_total_data_members()
#     df_tbl = df_tbl[df_tbl.member_id.isin(members)]

#     return DashMembersMap(dff), DashMembersDataTable(df_tbl)

    
