from app_imports import *


def get_app(theme_d={}):
    # Setup app
    app = Dash(
        __name__, 
        meta_tags=[{"name": "viewport", "content": "width=device-width"}],
        # external_stylesheets=[dbc.themes.BOOTSTRAP],
        external_stylesheets=[
            # include google fonts
            "https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;900&display=swap"
        ],
        title=TITLE,
    )
    app.layout = get_app_layout()
    return app

def run_app(app):
    app.run(
        host='0.0.0.0', 
        debug=True,
        port=8052,
        # threaded=True,
        # dev_tools_ui=Fas,
        use_reloader=True,
        use_debugger=True,
        reloader_interval=1,
        reloader_type='watchdog'
    )


app = get_app()
server = app.server

if __name__ == "__main__":
    run_app(app)
    

    


