from dash import Dash, dcc, html, Input, Output, dash_table, callback, State

app = Dash(
    __name__, 
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    title='Geography of Taste',
)
app.layout = html.H1('Testing')
server = app.server

if __name__=='__main__':
    app.run(
        host='0.0.0.0', 
        debug=True,
        port=8052,
        # threaded=True,
        # dev_tools_ui=Fas,
        use_reloader=True,
        use_debugger=True,
        reloader_interval=1,
    )

