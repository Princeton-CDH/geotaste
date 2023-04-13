from .imports import *



def get_urlpath_df(name, force=False):
    url=urls.get(name)
    path=paths.get(name)
    if force or not os.path.exists(path):
        df=pd.read_csv(url)
        df.to_csv(path,index=False)
    else:
        df=pd.read_csv(path)
    return df



def printm(x):
    from IPython.display import display, Markdown
    display(Markdown(x))
