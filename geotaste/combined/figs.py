from ..imports import *


class CombinedFigureFactory(FigureFactory):
    def __init__(self, filter_data={}, df=None, **kwargs):    
        super().__init__(
            filter_data=get_filter_data(filter_data), 
            df=df, 
            **kwargs
        )

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
    def df_members(self): 
        filter_data=get_filter_data(self.filter_data)
        x=set(filter_data.get(INTENSION_KEY,{}).keys()) - set(MembersDataset.cols)
        if x:
            self.log(f'using CombinedDataset due to {x} !??!?')
            return Combined().filter_df(filter_data)
        else:
            self.log('using MembersDataset')
            return Members().filter_df(filter_data)

    @cached_property
    def df_dwellings(self): 
        odf=MemberDwellingsDataset.add_dwellings(self.df_members).reset_index()
        odf=odf.drop_duplicates(['member','arrond_id']) # @TODO ????
        return odf.set_index('member')

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