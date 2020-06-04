
import pickle
import numpy as np
import pandas as pd
from scipy import optimize
from Functions import pxminf, pxf3

# species infomation dict
species_dict = {'Aru':['Aru_29', 31, 48], 'Bpa':['Bpa_38', 56, 144],
                'Pgr':['Pgr_22', 61, 122], 'Pst':['Pst_19', 63, 142],
                'Qru':['Qru_42', 51, 88]}

# read MCMC input
df = pd.read_csv('../Data/UMB_daily_average_Gil_2015.csv')
df['ps'] = df[['ps15', 'ps30', 'ps60']].mean(1)
#df = df.iloc[54:86, ] # with ps < -0.1

# MCMC model
def muf(X, T, I, D, ps, Jmax, Vcmax,\
        ca=400, Kc=460, q=0.3, R=8.314, z1=0.9, z2=0.9999, a=1.6, L=1):
    alpha_log10, c, g1, kxmax, p50 = X
    gs_closure = []
    for i in range(len(T)):
        Ti, Ii, Di, psi = T.iloc[i], I.iloc[i], D.iloc[i], ps.iloc[i]
        # px
        pxmin = pxminf(psi, p50)
        pxmax = optimize.minimize_scalar(pxf3, bounds=(pxmin, psi),\
                                         method='bounded',\
                                         args=(Ti, Ii, Di, psi, Kc, Vcmax, ca,\
                                               q, Jmax, z1, z2, R, g1, c,\
                                               kxmax, p50, a, L))
        px1 = pxf3(pxmin, Ti, Ii, Di, psi, Kc, Vcmax, ca, q, Jmax, z1, z2, R,\
                   g1, c, kxmax, p50, a, L)
        px2 = pxf3(pxmax.x, Ti, Ii, Di, psi, Kc, Vcmax, ca, q, Jmax, z1, z2,\
                   R, g1, c, kxmax, p50, a, L)
        if px1*px2 < 0:
            px = optimize.brentq(pxf3, pxmin, pxmax.x, args=(Ti, Ii, Di, psi,\
                                                             Kc, Vcmax, ca, q,\
                                                             Jmax, z1, z2, R,\
                                                             g1, c, kxmax,\
                                                             p50, a, L))
            b=(0.3*p50-1)*(np.log(10))**(-1/c)
            gs_closure.append(np.exp(-(px/b)**c))
        else:
            gs_closure.append('nan')
    return gs_closure

# quantiles
def qtf(traces, T, I, D, ps, Jmax, Vcmax, n_samples=1000):
    # draw MCMC parameter samples
    tracesdf = pd.DataFrame(data=traces)
    samples = tracesdf.iloc[np.random.choice(tracesdf.index, n_samples)]
    # run
    df_vn = []
    for i in range(len(samples)):
        vn = muf(samples.iloc[i], T, I, D, ps, Jmax, Vcmax)
        df_vn.append(vn)
    df_vn = pd.DataFrame(df_vn)
    df_vn_qt = df_vn.quantile([.05, .5, 0.95]).T
    return df_vn_qt

# main function
def f1(species):
    # species info
    species_code, Vcmax, Jmax = species_dict.get(species)
    # read data
    df_sp = df[['date', 'T', 'I', 'D', 'ps', species_code]]
    df_sp.loc[df_sp[species_code]==0, species_code] = np.nan
    df_sp = df_sp.dropna()
    T = df_sp['T']
    I = df_sp['I']
    D = df_sp['D']
    ps = df_sp['ps']
    # read trace
    ts = pickle.load(open('../Data/UMB_trace/{}_dry.pickle'.format(species),\
                          'rb'))
    # run    
    vn = qtf(ts, T, I, D, ps, Jmax, Vcmax)
    vn['date'] = list(df_sp['date'])
    vn['ps'] = list(ps)
    vn.rename(columns={0.05: 'qt=0.05', 0.5: 'qt=0.5', 0.95: 'qt=0.95'},\
              inplace=True)
    return vn

# run
species_list = ['Aru', 'Bpa', 'Pgr', 'Pst']
for sp in species_list:
    vn = f1(sp)
    vn.to_csv('../Results/ensemble_gs_UMB_{}.csv'.format(sp), index=False)
    print('{} is done'.format(sp))