
            
    # def diffdb(self):
    #     from sqlitedict import SqliteDict
    #     return SqliteDict(os.path.join(PATH_DATA, 'diffdb.sqlitedict'))

    # def diffkeys(self):
    #     return tuple(sorted(list(json.dumps(d, sort_keys=True) for d in self.filter_data.get(INTENSION_KEY,({},{})))))

    # def measure_diff(self, force=False):
    #     name_L,name_R = self.diffkeys()
    #     # if name_L == name_R: return {}
    #     key = json.dumps([name_L, name_R])
        
    #     with self.diffdb() as cache:    
    #         if force or not key in cache:
    #             from scipy.stats import kstest, mannwhitneyu, pearsonr
    #             statd={}
    #             lvals = self.df_arronds.count_L.fillna(0)
    #             rvals = self.df_arronds.count_R.fillna(0)

    #             for statname,statf in [('kstest',kstest), ('mannwhitneyu',mannwhitneyu), ('pearsonr',pearsonr)]:
    #                 stat = statf(lvals,rvals)
    #                 statd[statname]=stat.statistic
    #                 statd[statname+'_p']=stat.pvalue
    #             cache[key]=statd
    #             cache.commit()
    #         return cache[key]


    # def get_diffs(self):
    #     ld=[]
    #     with self.diffdb() as cache: 
    #         for key,val in cache.items():
    #             k1,k2=json.loads(key)
    #             ld.append(
    #                 dict(
    #                 group1=k1, 
    #                 group2=k2, 
    #                 group1_desc=format_intension(json.loads(k1)), 
    #                 group2_desc=format_intension(json.loads(k2)), 
    #                 **{kx:(float(kv) if is_numeric_dtype(kv) else kv) for kx,kv in dict(val).items()}))
    #     df=pd.DataFrame(ld)#.set_index(['group1','group2'])
    #     if len(df): df['is_self']=[((k1,k2) == self.diffkeys()) for k1,k2 in zip(df.group1, df.group2)]
    #     return df
        
        

    # def rank_diff(self):
    #     self.measure_diff()
    #     df = self.get_diffs()
    #     if not len(df): return df
    #     pcols=[c for c in df if c.endswith('_p')]
    #     df['median_p'] = df[pcols].median(axis=1)
    #     df['rank_diff'] = df['median_p'].rank(ascending=True, method='first').apply(force_int)
    #     return df



