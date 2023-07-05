from ..imports import *

class CombinedFigureFactory(FigureFactory):
    def __init__(self, filter_data={}, df=None, **kwargs):
        if filter_data and not EXTENSION_KEY in filter_data:
            filter_data = Members().filter(**filter_data)
        super().__init__(filter_data=filter_data, df=df, **kwargs)

    ## figs
    @cached_property
    def dob_fig(self): return MemberDOBFigure(self.filter_data)
    @cached_property
    def membership_fig(self): return MembershipYearFigure(self.filter_data)
    @cached_property
    def gender_fig(self): return MemberGenderFigure(self.filter_data)
    @cached_property
    def nationality_fig(self): return MemberNationalityFigure(self.filter_data)
    

    ## datasets (filtered)
    @cached_property
    def df_members(self): return Members().filter_df(self.filter_data)
    @cached_property
    def df_dwellings(self): return MemberDwellings().filter_df(self.filter_data)

    ## calcs
    @cached_property
    def arrond_counts(self): 
        # return get_arrond_counts_series(self.valid_arronds)
        return self.valid_arronds.value_counts()
    @cached_property
    def arrond_percs(self):
        s=self.arrond_counts
        return (s/s.sum()) * 100
    @cached_property
    def arronds(self):return self.df_dwellings.arrond_id
    @cached_property
    def valid_arronds(self): return self.arronds.loc[lambda v: v.str.isdigit() & (v!='99')]



# ff1=CombinedFigureFactory(filter_data={'nationalities':['Hungary']})
# ff2=CombinedFigureFactory(filter_data={'nationalities':['France']})
# ff1.arrond_counts
# ff1.arrond_percs