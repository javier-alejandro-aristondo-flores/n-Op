import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from paths import FIGURES, RESULTS
OUT = str(RESULTS)

t=pd.read_csv(f"{OUT}/observables.csv").merge(pd.read_csv(f"{OUT}/step1_copies.csv"),on=["family","point"])
u=t[~t.is_copy]
r=pd.read_csv(f"{OUT}/step3_residual_vs_strain.csv")
d=pd.read_csv(f"{OUT}/step4_residual_vs_strain_pbe.csv")
c=pd.read_csv(f"{OUT}/step5_coefficients.csv"); c=c[~c.is_copy]

fig,ax=plt.subplots(2,2,figsize=(13,9))
# (a) the headline: scalar residual vs strain, with the threshold
x=[np.mean([float(v) for v in b.split("-")]) for b in r["bin"]]
for k,style in [("M0","--"),("M1","--"),("M2","-o"),("M3b",":"),("M4","-s")]:
    ax[0,0].semilogy(x,r[k],style,label=k,lw=2 if k in("M2","M4") else 1)
ax[0,0].axhline(20,color="k",ls="-.",lw=1.5); ax[0,0].text(0.02,22,"threshold  σ = 20 meV",fontsize=9)
ax[0,0].axhline(0.0105,color="r",ls=":",lw=1.5); ax[0,0].text(0.02,0.012,"measured noise floor 0.011 meV",fontsize=9,color="r")
ax[0,0].set_xlabel("strain magnitude ‖E‖"); ax[0,0].set_ylabel("residual MAE (meV)")
ax[0,0].set_title("(a) PBE indirect gap — model ladder, grouped CV"); ax[0,0].legend(ncol=3,fontsize=9)

# (b) DOS ladder
x2=[np.mean([float(v) for v in b.split("-")]) for b in d["bin"]]
for k in ["L0","L0mean","L1","L2","L3"]:
    ax[0,1].plot(x2,d[k],"-o",label=k)
ax[0,1].axhline(15,color="k",ls="-.",lw=1); ax[0,1].text(0.02,15.6,"row-3 clause: 15%",fontsize=9)
ax[0,1].set_xlabel("strain magnitude ‖E‖"); ax[0,1].set_ylabel("residual (% of curve integral)")
ax[0,1].set_title("(b) PBE density of states — σ=0.3 eV, grouped CV"); ax[0,1].legend(ncol=3,fontsize=9)

# (c) the gap itself
for fam,g in u.groupby("family"):
    ax[1,0].scatter(g.strain_norm,g.pbe_indirect_gap,s=6,label=fam.split("-",1)[1][:22])
ax[1,0].set_xlabel("strain magnitude ‖E‖"); ax[1,0].set_ylabel("PBE indirect gap (eV)")
ax[1,0].set_title("(c) the target: gap spans 0.44 – 4.81 eV"); ax[1,0].legend(fontsize=7,ncol=2)

# (d) correction drift
ax[1,1].scatter(c.strain_norm,c.gap_difference,s=6,c="tab:purple")
A=np.polyfit(c.strain_norm,c.gap_difference,1)
xs=np.linspace(0,c.strain_norm.max(),10)
ax[1,1].plot(xs,np.polyval(A,xs),"k-",lw=2,label=f"{A[0]*10:.1f} meV per 1% strain")
ax[1,1].axhline(c.gap_difference.iloc[int(np.argmin(c.strain_norm))],color="r",ls="--",label="equilibrium-geometry value")
ax[1,1].set_xlabel("strain magnitude ‖E‖"); ax[1,1].set_ylabel("HSE06 − PBE gap correction (eV)")
ax[1,1].set_title("(d) the hybrid correction drifts (noise floor 0.002 meV)"); ax[1,1].legend(fontsize=9)
plt.tight_layout(); plt.savefig(f"{FIGURES}/plot_gate4_summary.png",dpi=130)
print("wrote plot_gate4_summary.png")
