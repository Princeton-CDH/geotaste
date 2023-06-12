from app_imports import *


def get_range_slider(series, label='', step=10, value=None, marks={},**kwargs):
    s = pd.to_numeric(series, errors='coerce')
    minval=s.min() // step * step
    maxval=s.max() // step * step + step
    value=value if value is not None else [minval,maxval]
    slider = dcc.RangeSlider(
        min=minval,
        max=maxval,
        step=step,
        value=value,
        marks=None,
        className='slider',
        tooltip={"placement": "bottom", "always_visible": True},
        **kwargs
    )
    return slider



