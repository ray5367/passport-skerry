"""Free State of Skerry — an invented passport spread.

Writes one image, /output/entry.png (1024x1024 PNG, <= 1 MiB): an open
passport spread for a country that does not exist. Left page: the data
page (portrait, personal details, machine-readable zone with correct ICAO
check digits). Right page: a Kestrelia visitor visa, eight arrival /
departure stamps from three neighbouring countries, a Port Anselm tide
table, and the harbour-dues stamp. Every date is consistent: the passport
was issued 03 MAR 2023 and no stamp predates it; the visa was issued
before the trip it covers.

Pure standard library: the PNG is encoded by hand (zlib) and every glyph
is rasterised from the embedded DejaVu bitmap tables in FONT, so the
program runs in a sandbox with no network and no third-party packages.
Deterministic: the same bytes on every run.
"""

import base64
import math
import os
import random
import struct
import zlib

FONT = (
{'SB30': {' ': (0, 0, 0, 0, 10, ''), 'A': (29, 26, -3, 5, 23, 'c-muNpa#hO|NnmtF3GDv$w$oC<sANlfIoK0m0-!8Smh*sfhGT`V3Vx*{|YSIgGG+{(SOfRAj!8Jn3DeguQJR8YmLX0-0?q;!3ZpQ5<^b;-#0-9hBIJUBXr5`{|kU*8d!1;njHI^|CT_C=QBw1s{pEG-2Y2pdKOq~KC0yL|Jh*L7%X`MMb6+qDsV!UoP{R221$<Z%YPRrQ|t#w^0yRnET4n3=YX}=Bgb+CoUQc_B>98|#<%}}A1VH~fwcxhI5rSBKrLMWchnq$lH>va9qh)!'), 'B': (29, 26, -2, 5, 25, 'c-muNpa9JHj|BdHy1%1B0f!_Q{Ay!F(tHLabc2C`Ln-DWSh^L9BoJ_(2kRBYD#?%m*6NL2(hn>di(N7wENP8ZlK&QneVz%6YgJP3fS6}x(OnAz*B1sbGvJc^d9hcE0b3v_Mx6jL|4nDZ>L8}sVC^fhdxh%_Sk@V<B*SX3<Rt8pQ^AsJu}dxoOU}V6$@UB^nT1ud6D;>Z6ho3tHh4E!?sq88Wb*%l1J*S3{q42Q4OR@40s!H|Bku'), 'C': (28, 26, -2, 5, 24, 'c-muNpb)V7_8fcg>DTLvOY+oEWmt+H|3`oumC^_)xnm%qyP3)yd{#660GS8iQqo{e+qfV+kDo|#Y!^UMkGWy|JS4eXuqByrW0>#3<(OZ9r2dK_tZ#tJS%bA*LvpnZT&@l*w+^eX=YZvAV3pelmg~hTw+W9NJ~Q#T#R|g@2*CUt>~~Rw$d3R2jZwlZ11=@;^Zx_Xuzth^<4^woKOZfQws1mtQGfqm=0I2=e;g!vCqs#Y+j8E&|Iam0(nK**n%Jj^o|gQ2k3anU`|X*jwv;AI0EP0nKL'), 'D': (30, 26, -2, 5, 26,
'c-muNpa{(P4+sA~J~%NYniq#G1bmt#jH3MvNbm*&1D|%`BM|ec6E;~O;Mxvi|FFR>%fR&z#Ca=*U6vsgY<WKpS)tz`-gh4CvJ98On!Rzzt_I6?;E<gLmR*EHwi7J74To$uSavI3lNaK3RXYyZD_~hq?6Sg;(BQ@wl70AM;SKg!;Km(;JX(<0f98ZI<xCdFp6Wh5IyDtF)sYPVYf2VG'), 'E': (27, 26, -2, 5, 23, 'c-muNAQQ~^j|l__N&&$c5cdY0`-R$4$N)(y=l>LHNx=YVQdD;aK`)apwdQ{aB~sWD0AVRI008Hh+l2'), 'F': (25, 26, -2, 5, 21, 'c-muNAOp<!j{#obmjHq@Al?HQPlkFDNB~J<%Krk&C18Mf2`XAnz=L#_K#tk~q9jNJ00EZ8k^'), 'G': (30, 26, -2, 5, 26, 'c-muNpaNj^>p6P=<L~$PcTWr#Mwcsl@*e^I9!lgvl2kqo5`0{!#m6ombsWTQKuF3x0}1TphVU3WP-NM!fOT@i1vVqg7J)6xK$xY0B+K#&>=IEVcN|5?+JLoQL-s-)Lbe_(yADS<%mK^J#38#8EZd7ib`xG%h{-dcyd}`kbU<;{S{$+vA6-Tmh9b)h4vpV}*ku_Cz}y5Jvh0^Z+*@qeWf^3jg80i>vCA?jo&*V8Ns?#hlCmyFmt|lrd5n~D{(oHL#)O)(e0z>Q`1I$~)00aoELf<Ji~$yB-a!'), 'H': (32, 26, -2, 5, 28, 'c-muNpcu^f4+kq47#tA1|HR1y!5I+m28>q%mNY=JVpzzd0g~m1d-#wmPlfbHJ^%oHzcqd'), 'I': (18, 26, -2, 5, 14, 'c-muNAPUU*4+kr7i2%VF5cdYM#!(THM2HM$`~U#iACeg'), 'J': (21, 32, -5, 5, 14,
'c-muNAPvm;j{rP)1%V(3EaHG_!l)qK1np4;i@<_LsDce(K^Z8|<o|IHH4h~Af&ni0g_nVW@is_s5<>9*5=nthkl1S(Bta;6WCpi^(X9FKgCAcXZc687AQ=Dv{TsFf'), 'K': (31, 26, -2, 5, 26, 'c-muNpb*UX4+krNTpK9+198$oa0bM`0pnHw`&)owKC(31qW_<~8E{F99RB}Mj{%po=H34%B^Yo?yS)Fuijx7Cbo%fAEsP8}q?!8u|F6UrGGOTkn}NiAX<X6}a7_e<^z(;c`7?Yt>{fpbmOsde!{w%*!SdT!ad^!2Cs=+Z6OLes_y?AsgDX&TA@1+R6(!9O`8r$?IujzFheMiaEm-<r0`|njz`h^G#VXCfcMe&a0ssI%kq~V'), 'L': (25, 26, -2, 5, 21, 'c-muNAOp<!4+krVlK_G<AkiCGOdFM;pG4390x~6#q80`SNRS8s{(+~8'), 'M': (37, 26, -2, 5, 33, 'c-muNpd#4w9}4P`1an}5XV4VAV1uh+yosg=2);lB;@|>4P$kGVe)<0sBy<+Z2|uwYS_l@ih4OX&zut;Pk?C)c*jgxm_W!0eSQJUD0EzvP2XlqL{gl9}$Q&%#1Lju$U%-G>5yNqi;CpT$kM-$)100INz@pheUiANc3^)`qKLm;1WMp7C_1_nlB8F11uor{X|67bW6$yaDeHX*3|5*$;6){W!i+lWj$Bjpk>OYY9r~e%ccoZ>g0!#ds!K=s#EU}CMuOfyEAPG|fiV}e0M;HhwLIP-tpvm_El8Tc5|FNfW{EDaq0EBr^4*'), 'N': (31, 26, -2, 5, 27,
'c-muNpb%{M4+c}<0yz+Y{}#y7|MRg+1Hlsz@2?NS#3lc8kjw{5|Nm@&SNi`GDZJAE&vN6C-V2f6$b?<mcpF5%54*Gh?<I(Q26kx%`4?d6-|pC@8O*<f<v;3Rmu3k22bO;zj$N9e24ek5PVCYQiy-o=8L>;V9fHVrV3%ePz5|hefnAzG{XH~%u}d>J|H3QHkb+;Dp&L~inwWmT_)Ht{N;7buMKhdS007?b^fd'), 'O': (30, 26, -2, 5, 26, 'c-muNpaS5IoObr{*YD3R&P@=)kZXDS9}d1u6h@KMz6KIqV<*64I_n>h^~efIQVp!J7Q%@KvA>(cCAn^c1dhVED?q%L;xKL{*tP%|*96R+4CS%D1Mz-x!_9gQ=8Hl&4q&zC5YE^H7Knmy8o-=Y2-$wHz-$O-E|@b7AzK3$*nw<N4??yOEN~WwY!R~TJiI11Vt3UX2*(k-kD?(Qw)beE@eIWOC5B=TJS2@#-NADo#65x%3$G>NMrnNj3DiJ1aUk{&<Onvn1rl0q!^dqr6BPST>`)R1Z^wH?%K17)1U+T(M9)0;^xKc;m*yu4Q6m*I003{U{>K'), 'P': (27, 26, -2, 5, 23, 'c-muNAQQ~^j|9Fv*qF|PT?zzV1|exY0}{Exz${<!9mM(<k0AvF?*G8X%3_gX*a9}Q7MoN7SZW(KsaUYoNo-O@xOHs@OI2Z!@&dc?voyLClU(Hw5bJL=n!gaC5x{^=>f57@X*>)J*g^vX400*t1du?q6d3>j$lmA('), 'Q': (30, 31, -2, 5, 26,
'c-muNpaS5IoObr{*YD3R&Px=+kZXDS9}d1w7D18Jz6KIqV<*64I_n>h^~4rQQVp!J7Q%@Kv42>>CAn^c1dhVED?q&0k}z&1*tP%|*96R+2IaB71Mz-x!_9gQ;{OtZa2&vD&mo+#2`mr|;WU6bs}QpNV1YRh&Ri6GfS?8}umjnk9)xTmSl}!U*&<|z%)@T-9tfuqyQ^kFIF8tT6c6FBy+;d;XW)<)h4N}qL(&+`oeSgg-UD%upv1yUF}P7$A3y>%5KbJ3{mmIEg7t2KgjU<|aU0JB#r`u}l*GZ)gp_hV_VZ(;tdPkkAAbA)|IOrZE?g<|$p8N<y=6IZ$eR3y7%qWbItQ;TL(&&~vJB$2N8bLCpgeN{0Nm{vMg'), 'R': (30, 26, -2, 5, 25, 'c-muNpa{(Pj|9HIIMk_+Qx*)CaHD8H0}{Kzz`*CU8!Ww_37aef1LJ0}bR2eB24k@7dK|LM|3K{Xcx8{_kTn6D+>OIkTR_Zr(%58q9e06P_e?PT3k8qX#<DTsl)YWX%78`o2BT!nU$AGH7_f#ULpxY|CJtH7ry$mAUhJ|AnPAQJIAqx#fS4bJafDSeSaS~!S(e-2BqEJnmLUeLc?Oo0vjWIvx(4OQV3TDCLy;vL005D<93K'), 'S': (26, 26, -2, 5, 22, 'c-muNAREY3?R@;@*X!G-H?~G-vm(TqTYmjV0yPMk#X#;VM<Hfz&D2XMGJ!zeQYf2c5wgq<piC%?!~O_K<}FYr56){rlKBUec_fF;$sa%t`msDr1Vd&I)V2Sv&r4B8kqJij%*A9TB&j}RssG22P4zyBBE^hsqGr*C=WwYIbeAZ^t^NU)S%Sp_l6yfiXJFh7|GnT+B0qsL*AOz(5xTAcWey-@zAC`jjIV$)?FgCw7bT(WWT3=PH6)q;?^`Vdn0d{o`~k9a7?5QU;8{4rQZCb^{vBuUzWMdz_1XEMoaCo71^_L_%!&'), 'T': (27, 26, -2, 5,
22, 'c-muNAP=ngj}5R8l!^fBUIP|_nDm7bDbE5m45_RFMr4;FOQC^LDcVU*Kt%l;;-yFg066!xZ2'), 'U': (30, 26, -2, 5, 26, 'c-muNpa}f<4+kC~z6_MpK!hv<g8`UVgD@`S{}u#iRF-&IO|Wb;LLm148U#lQEIR=qkoA8qg2VO;B)btI(DT0qDT+^nWS=s^`3L{|A;~s?jdp}_75;n`K$4aC29muj1mUso`acCF^~8WRKgw0-Vwa1(^#2+UYU1*Hjz~ZM*9fDhJ=Wk^r(b;g^Wpy126YB%0005l$GH'), 'V': (29, 26, -3, 5, 23, 'c-muNARp-bhXWCa$Qdwa3qeT+2Ij|Lo(96S)c>pC>^iXI1cc<d|Bi6B<ZqDVdoCE?^8a-tN38~HO@eV3{m(;^bOcMDhVq2Jf8j^=&o!{D34~Mje-?^o^T3jG!EDC6{|!+j`M-c9zY2iZp8t=dh0|=XR<JuZ|BpkHGz3dt1G41)zTrR*;uBz52L^_=|6Lg29|x9P$-wsVpE8Cd`x}ttFY(C#+p$DlH&|=c;s1VEB$fVwB;Wpj$c!!4cR(Vw3Tu+^`wy`dt0dDykmPb4si_(yX@^5n{OAAwR~V=Q0O7K>1^'), 'W': (40, 26, -3, 5, 34,
'c-pm+O(+Cm7=YjPv!QLZDUqKzY$>%xk#dk&Ia0JD<)Db#av&wLhb`rxE#xLiq!guATYGRItr7=P3K1nr#AfW8*SzmH?9A*O`A+ZiJ<sgd&Nl#my&Ca%74pWUGQFhpxFhy$rri;Z?xYSN<Bi}UMNko|S@kqGE+>xOU{xz%kl{vEbJ&*Xx>-#N2#K>Q87#LSwnXQMk-6a6E{V>^RE68x{~TsjPNN4Sae`wOe(cqDUhc+dT*3ZbrV^sFuUu_c%qF5tY0q;05R+FSC+_KAHor5u0H6U6pp?6?vOR*s`fh^N06+jo0Zs^F4uE}h>N^*AA%H6^1Mo3*L7seSyyZ(WpV=-vSD=Esb?8ICv72GlIgV3A*95QDAXXc@I`I>SSVI(GYM1UT#xC`dOjN#SQ!nlq=aWCfMR8pV;;AP=P03x0FwKIN7}T#-w=&<^SOv9mw`%tNZ<1M4AuCGcG3$EBbo|hk0+QXV%ZY0ZJr#uiTi?DTMR5'), 'X': (28, 26, -2, 5, 23, 'c-muNAQ#;E4+ks^3@uQm3_&>thI%mXu^@yO`2T|}!c^wtV96C=j`*wpQOH)Rd;v>FgV>w?FGqDxDp>A=9Eb%o8xA&sB@Zwueg5Z!?h&z<V9AOj|9dfg=>v89C3Y-9FcTtYiY<7!Z-M2yv4)*BSnjU_Hn~QKp%3{nr7ZsZxB`}3f@$6D|HZ11;0Z^UoArMmBSSh^?wvHMl<)udvhd*9!-y6v;J_Ds0hTO44Ngb|F?fUJzH1|-(*8ez1^zU!<ass-uLK&B0YLT|MEY<bBu5?q0E!{s7y'), 'Y': (27, 26, -3, 5, 21,
'c-muNAP>0whXV@`e+rnnfq)bPgYpj$=bIwToQ?n6;AS>~6>fs^JpVu9f=hAU2g~_@IqbLp2O~MfA1rm31H`WWzZ1ooTfuS-K$hIspK2&l5SM&cVqjQ{<OT?625Z~G;P(F^7n&5*B_TKd2Vn$C09fkR{~cHYY#Ue(%?%Ks@(Uz&1Zz0I7_w3~5XoQ%@lvD#00Yvu!v'), 'Z': (26, 26, -2, 5, 22, 'c-muNAPWTi#{g>x%WQz_H~R&aiN%oNy9<_B%77uW3@mYv55p~qV2R(B7!qn<z%n%$671)|5(k+uWF~?o-pOJ}_&~f8j3FWQ8Z0pzLxO1^SmHVthD<eB;-?{ogw=1bOc92Jzyq+v4n_=_RbYvi;usQX5C?l<NN9ZpOH6?A4gOz%FgPxOB`&gK$V>rCeA8sWka>a`+XQ7u1^_|o&<F'), 'a': (23, 19, -2, 12, 19, 'c-muNAQf=AbsoI_=FgX>M<zHR2~YTs00+d7h39E=N_d?Ei63J^2yXz>;vYcbjtF6A2xBiuxD;**ciM*ApZ-EkZ-<H6y+E?_e+N`l<`alFU4@xp1+s7xh_fHWLJ{5y;#6P=gY7Q>v34K}&jWGh0~vg8kcIs~oFCylnmbWk!ng|Rv~^pc;Q|q7$~yJ==i^l#5G&!r!~+2KW1;r'), 'b': (25, 27, -2, 4, 21, 'c-muNARPq!hX4tpB^Ve)2D60C>Zd>7ooW<Cm#F;*@y{oJG>Jcj0=#LzK@3M!iMb%=R1oVv3yOp<i0K7p2B1i&gP3Yy<|GseDG*Z_%-n+M4?ZySFmXC?+Tnw6l|QCGrh!=ZQ2p_z0OoTC)HufoD|lkCU;q5q`%_J#3}gZTg3aAb'), 'c': (22, 19, -2, 12, 18,
'c-muNAQ_lVJpJm|$GfMNWE-=<#3Z->M}Q2dpwt5pZ>t5Di2pr==pK;ZF=h}`;yp~%8muuE!kGXQZ3m00LpXsj(e+?aUNl$j2aB?yi9*!!p@~Aw)qrpo{XY$1Sb;_3!EDBR|68DncY{PvfZdz?|F<H{Z}&mM8x7fov%dXrg_|s~86FDLnUHKW>^=7K$B%nU>_`u8048R3cm'), 'd': (25, 27, -2, 4, 21, 'c-muNpaewxhX4VhB^VeK29<<(^XYd#pDZ^+mk9a{@xb3&R0-$5K;Dmd9-+#=C=x99LA)*yb0vy|KbYqLVuqtgOaSv_KukjviA`W07l^5hBC#LLW5x6bP8~Sy@B{N4F<r$B_D3(KKOjE;naCrE=5q#y;4dg)_5Z&IJak*my#MuVwWR{O1StRjvwGbw'), 'e': (23, 19, -2, 12, 19, 'c-muNAOqOXxbWuJ+Y9|V$bxbQ|3kswiOg_O`DZ|Z*Y@nz&w=z3xG-340g#aiVnjkk?ZDdgfGl+o;|f%`11u~6WO0C5h7jTPU=AyY`3J<xg9z{cj|!$hgg2rIuYm~nfH_>~K6C*KYeP655H|q<<5`e!7nsd{`2Q)Ga;^6uZ?~zkin<^9|HBM!jLt>4eXre-jA!zhcjf(`Z}+!k^O6((0D*s%Qv'), 'f': (19, 27, -2, 4, 13, 'c-muNAOQ%LAAJ4m&BZ0bTrd&S=l`Lg1uDY(0?7H3%%^o4E|d$BUk_wB!i83XgsM>t-wzVXMG-mz63W3VB=R2tLU0NZXVy>>`T_T14jv&Q001aomn;'), 'g': (25, 25, -2, 12, 21,
'c-muNAP<N)pMLlA$#OG={}A8-6%YCh;s32gm2mzGWdDfg5vu$P78Zc2XSomJb%B^GQ6&7qJO>an97SRRm?r~b8lp&S0`s^)Ol1^_{a_v|h^auF4xD!Qfq9OYu3`rJqZiX35TE}{<Pk*kIRiuR7nHCPKnmTKGw**rTWzTXmf*$=eglyB7dY4Fe?62H2a?!<BynF5%wReOlJG*3_<u22nnlog7u?-&2{?G0iDV^{e&*uS_rLspcX??XF9X>C0P(Nj4g'), 'h': (26, 27, -2, 4, 22, 'c-muNAP0#2hkzUsWPsqvpqF9I+W+d;yZtd3G7aaT9-ECW^Jj}1r^5>n%L`5B1t*YI4Pq@rlbH)*1%X(X&}7O%EDsRt5jIzYWu6QLnIF*b`X8bLWBpekAVV?$01(vP^8'), 'i': (15, 26, -2, 5, 11, 'c-muNAP9_)e7WEZ=W)OM|NsA285q~-KM452xIC|cyl=8_)uzY3UUXw13j6?@^gjnXmx1BP;O9c!{Qv(7Y+O7504S+&S^'), 'j': (18, 32, -5, 5, 11, 'c-muNARf41{BlSaSwQjo|Ns9VvmuFu{RaU}BoXBwK!NA%$lAOveLZT(KpOZD0V()I7#PlsV3Erpkthh;`d<wL1JhfOh!I4@=Kn1Xo&u1-X$F`G6x>jNiikAqd-C)9!_CQT#K#K&66cR?'), 'k': (26, 27, -2, 4, 21, 'c-muNAPfBX4+c4;$S^P*845BQ5D$DIMTSB8%-?dXrdd4y=#AB$xF5GQvAKY`=l_3yY;LRG4kX^FV3GOr4@BM+!jySwzX(JfV8xKhWneo5qUU3CoA4bFqY9gU)ZYUc|3a~asM9YX>$^E>I{5!Tg<%Pd=|ez<WB>r2Hq?#'), 'l': (15, 27, -2, 4, 11, 'c-muNAOL>+2ZJ2!Tn2_Cqg-5EXjuLKzXBT<4*&rF&V(@'), 'm': (36, 19, -2, 12,
32, 'c-muNpc?q`9}IF>^Nzm#@noGVP$**C^IvcGgkz{_JP)D&mvZlbvL+*$bOa>uXSWVd_-`QN_t~4aJhrbuV)kfiUUC9i`$4RKnm|@Rh&2OE%~TL;E{Jso#L5M+4x_0l1+gZ8SZhJ71Q6>InwlICs|Und0%FC0SXYL-8fbj||L>6jV>MX7SpNlxRznp4076v|9R'), 'n': (26, 19, -2, 12, 22, 'c-muNAPfBX4+c4`S^Ho8dbd9YL#E*zg#JGpN!JmOz@IH@oDMHQEH5;f7o0#=HHftgO=d2L6$D~kLX#;6u{=PmM`$uRaG57VK?WLb|Nn>Rz*zqk2*{8O0Lm`4T>'), 'o': (24, 19, -2, 12, 20, 'c-muNAPcCs?tk|E$MZv-I>@3zOaH^cS~0k=$TcAUcN!mW!Ve(ht|Ux+6G+_z5UT^k+6xsn1?zVLF>S$2M~HYUm?H~fO8$pyWnfqb=5T?S>|o{&i1<D*hZV$R0y9tHSKop#Ukc3ZgNPf0InE%aJ(y_+b?ADyBf3GXo$z3|0`V_T;!hysCL$mN7XO2X&q`tBkW*_t@chS*7l%8v$cqmK07LSf5d'), 'p': (25, 25, -2, 12, 21, 'c-muNARPq!hX4ti)lYxEJJl$PE>ZgrLVxmy>k$D9{3#URP5TXEIHF3-1u>_BSoc{_Bz!?kFEBFzMM53KR0A_7p-4!9n8IM@78D5y5R(tgJWQMpoObviT;-4Hk7*#*Jyd`EDS-Lh0oCU?!%D(_{qtY%Pc?}$pi5xJ2-PHDG5G&~1CbJ>0sy#=*UA'), 'q': (25, 25, -2, 12, 21,
'c-muNAP<N)pMLlA$#OG={}A8-6%YCh;s32gm2mzGWdDfg5vu$P78Zc2XSomJb%B^GQ6&7qJO>an97SRRm?r~b8lp&S0`s^)Ol1^_{a_v|h^auF4xD!Qfq9OYu3`rJqZiX35TE}{<Pk*kIRiuR7nHCPKnmTKGw**rTWzU;E&&6ym+1KaA1!JLNe~AB)R5Pt'), 'r': (21, 19, -2, 12, 16, 'c-muNARegvhkzW0h#k-W{Qob5ESS3tLd!rE9|3W0ea#f&OZ<Z>_&*fHT!Sij8O<)R-~?=f#n=RM21fA5e;9BeAV?$t05}(K!~'), 's': (21, 19, -2, 12, 17, 'c-muNAPLCT?R)(7_sh#WyF<lcV(GvB!@(V>nCV|2XO|T}mwMe-xZp&P3L!8v1TMG^Bxnp~GQNQcP6G*ko*E#HY`4W<s3ngV`m?}A<3GbKzv}=O6)ipV9V+@w70C=%!^}Nk(N+k5#(zr)V-84gAxv;16PQtkqVoT4cL`R>__si@pIUH1IQSF-wS&v9bj`WP-+zC+zCKrwwBTg`0I(o~Yy'), 't': (18, 24, -2, 7, 14, 'c-muNAP#W+2LTPLi+KD;fEpYkw6mQ!5q1m_hCd(?9R`NB|Er)P4?!aK3=Hf4cR)oJgG6TXdj0(G2o=%&2KCoYxItQTZhZaw@l-iGk?{ZkD2acp'), 'u': (26, 19, -2, 12, 22, 'c-muNAO{5ehX4r%h875G3PBkL1`(JH1H*zrEVB?*MhGk;4PvfEm0<<TXo8rRP-PfyfcODGhQ>cMnOYG4j2653<v(aL9LJ$yw`M7XK7o)bJ@e()^R3|!S0l@i1^_G)t%d'), 'v': (24, 19, -3, 12, 17,
'c-muNAQkldhk_I!XAPL8gHN1+VIGLR6{`K}e=V3vh9L2ODqyzr|2+sRj)Elm!ORW+0}$d7An^~}K$iTU2h0d@)@LAz3?QrXe;Kk{>p|jI7#KL-d>2L*m-q#eaAZjOKNr<=%Ru7m7|#7SL>0FLiT{cGe*`@=&VVGo{|`qOPXGtNGgfqQj@KaZI?P~g0}B6=U?3L&0I&RZi~'), 'w': (32, 19, -3, 12, 26, 'c-muNpcJ_Lhk^+}j`ZLE|095O3RoluL%tYDZ$g!4U`PV7A2WfNXMwC=LLgT6|4f(-eBVF{oPaDfu(mWHi|NTvVYm}kfJEm584Y0h13;GZ{|yKydV@qiaWXL6{10^B|G&}<4D<g7Bjj0Lf)qqBnEXGo7sM)N;QaWW9m$UqL84n3`u=Amf>>u6BL2@p4g(XA=x>RqKZW?dgP7`D{@bDi(shvN`v2=07*>H;Q-42TM3Jw81QF0pejxha{}$9hmj4G52Dyp#4OpcHS}Ys@34+};4a7Q)9!tp}Q9BUJ3dG7om*)q%8|tRJK(B}~PzeA4ByPvW'), 'x': (23, 19, -2, 12, 18, 'c-muNAPwC44+Se27J%sje8LP&TS1&}20*69=O<!tV+8Ml#P10*@Lc<8fn>b?H<0)?rd9tlQLK#t8+!cz0yO7L28*BLL=$Gc0TSNMh$ig*7p%MiRaE}XJFuJoc_WLmpZ@2~ybmP)UI|Hf7D%_~W03d-gsllcCj%+-pCIwYP(et5<S<--h0T8nJi?>^0M_D>V*'), 'y': (24, 25, -3, 12, 17,
'c-muNAQhzihk_|U&IT|`1D`kpLj{Qak^{oI_FV*K65o4}L>idw@_!b>iWZRg4Mq@i<9{uLxae1qgg=m_@OKBYn<j$94+9z9|J{+rWq*MrEEu@nU1db^#5|Dr8iv&Wsi>Y){|glVt8(czCz`KUgEXA_-;5p_hG38Wl*9<89U$?An89ZU5;w#Wu1Eg=-;XW4y&*ov03v_xFrkXH|1|}Y{r_{(RCfH|BE_5Y_cafOI2c5to2=D+{^N(kUJR4~04>^yas'), 'z': (21, 19, -2, 12, 17, 'c-muNAOTeTM*$pI1i!LE1zo^&CRi|v0a?)ECrE4p1G1p_6Oh;;7G&F44uHg-ilaE84<z=}5=ATmY)K}Hn9diF*a8$W{#ziivmD4`j2l5>Z{$Jj9Z(-J)PltRx-uXOdi(_mRxqFlKEW0sAFv4$2>`CDgdG'), '0': (25, 26, -2, 5, 21, 'c-muNAQxElUwHNF#pyO3RAHgj|DoXTbPgnO(ThN#Lptnc*MRgMPK3k;ApeIrkYNPU)DIW;25}FAnNL8b!R^@sl9&r-?g23;LB;w0fOu_S_F@q86;#3j?3^+%dkUB>50S_Nb8^7!E->2{BGClqq=DHjV0HpTVj`H60%kXY*#(#q5Z(C%jLOGlxg##;^5gO#!&XF)>;^HXz$AP@yhC8-BTyjf!Gm`*DA>h-3_av91Ol-uK>k53Hsi}cdOtT(6pE~aN9`<5)L6Hgc<IfrmuEV3$xcoT08-B5g#'), '1': (25, 26, -2, 5, 21, 'c-muNARCCy`S<_-|0C$aEcqY)|HmTXeD(kDFIXge{{P>pbpne-#4TS225b`ItPI#Cz+hB@RuWJCBY`KxNRR>m5A2ho'), '2': (25, 26, -2, 5, 21,
'c-muNAO{G#)oeU_|KsoXH`nHfBTJn5j{x6WSx_V{c<^vq?F370XGW5E%nzcOcY$R}kt7lz3@fn2U4+CxsFlp$z%sm;?t2K9kie992@?OvgdxuV7bGzsQ$qw;gFJ>f(^;VSH)l)@EkN<7W|-m?K=F+t7{VO0|Nnm-g{fToJTR0nJ-}4<<Nvp82>Z%^9k{p{F!au7FknbHJ^%lwm6ZWg;_rV{0GIerJqgkP0PhyJ2m'), '3': (25, 26, -2, 5, 21, 'c-muNAP2DMB~Cqf_4$t<uTRhRV@8t5`Huu{nxRO%PZi_TsQ&_z`KE^~;S6SYfc0!glGp}i-2+MdWJE}mL0Lz^S~xJ>_XH&V7*jk9tf2x;ltZiO2S|K26RP+Pu<B>?tk8{tNc=fh$&W6>u3Gd4B=^z^({ja^AenbEm@=7Q^LjBQWWf@bFeO;Q5^rGK7vI^SEHSXe1GvP0J18p>EU^(GaTcOQ=nh!I10nJMn3n*Hbi#eGcn<@T1OhxyMz}@9y>iv*yYK&eeSUOiASVO4003prvn&'), '4': (25, 26, -2, 5, 21, 'c-muNpaAeZ{0{_AFeN7b$1Y*^7rO-OrT>4iN>u%SxB;7l>i7SiOR!1o|G$(0n?&;eH=@`i#NYjoWxyt}^8Zc-Y!W{IzbIgn;Cb}FkO7;-r2nUwu}PT!{jJA<O=8D?bg%>>aRiqH94x^RA5@cgf@HZ0Q4&N004a&Qp#'), '5': (25, 26, -2, 5, 21, 'c-muNAPe;TM*?qXC1HWfaxx@zX59Mz<<Yh>F*Jz{f1y_YtY<-y_)(|CCR_R)B(<IyA(4OD9!!UVHPvCU>@rB=s{p1%KUhlyrbI4Sq6JeT87wgkQz8#6(F)^s{C9=2CV(Yk5fW8U)-|vnMGz8?1;LD1u!e31gv9^55%O#bH9tY(d)SdB;NW*R2f{5J_La*|-hT5N7`hcw3}gcU!;`av'), '6': (25, 26, -2, 5,
21, 'c-muNARFk`9(eHO>%HT%;#H7^rB?j=4+jbeagB#S{(cW3PR;H=$PzsFfZ}VJ!0Z%ciOE3m-;xkE<1K`Qz&D`8J}eH(1lib&MPfNfqENE!;^*%VR(K*w+yY5#`~-FEW?s0&Z?M1{cXst7AjWPcs5loyWjc^4_ZP%Ufl7!&B&0#?vmn+*m}|k}UlH#3Ck&Bb0teG0xL5!GH-c&b1=Rn$U}hg!!VW6223?0PR3Zh<j$hoc!2Jl~O2J*V7w*GcxIg}YST1l0#$^zns~tuUPR7P>uz3Ah#)uNaQWbk1fBW%lPn87O$q4|TMA>%'), '7': (25, 26, -2, 5, 21, 'c-pPbEepZ`6ougnLqrgSi62ac|4bH^Og7V!2#Sb;3<Qfm%(7rG42E-TT3(wXoTQ#~d7pC4zS)t_h5v)#4X@L@imR(&19KD5Ey&yI^Cc`)cXMtX1v6Nw-pVL?3L;pm-b^X`3Z}4Cy>X%R6ii^Jdi_i_P%wsA^;*K+R}jKpb?3xms9*#K`)yCc416p'), '8': (25, 26, -2, 5, 21, 'c-muNAQKq2?|=IB&!_v_D-@80`Pcr3gWtU@aB-FsAd#cm+&1??jCpX07_d?UAS({c(t}AX0P+4Z16g`tiDH<<CJ^r%h@}LUXoX2kfa}l&OC-Z2^nQc5x<FPGi1AtgVf%L=|DYz9#VsKH$`Z*V3jOz?-ndjNi0nhxb?>1P&*vK;gjwc;geJ>!8twzqe=6V-ogne^AQm@RV+2%O<Ohh?1!ivnF>ga9g29I8g4xr+Y$b?9E|`-FX7_>Fwh)OVBpuViY(t2IF__Z>W^V&Azw<yXIS2L`h{f{}B|`Mxfw+q`xD5}27&nFB9??9Eh}!=vMUcb9s^`G7uYW#2+)=MdZhB$>02r+9^#'), '9': (25, 26, -2, 5, 21,
'c-muNAQLFH9(wWf^ZiXZd?><fy?_5h!JA|xamF<up>=YcQQv`dJwhTGB>sUL$m#&G+~5+oLEQBqmJNt?117EvHoOzW6azCIp%PwTUKxnVj8FpvQD9ynnEemL+y|8iK-X~}Dq(<b$2+J5(;KiiKul|}#CMppT2TG*|0PU<=NgE+R+b~;J6Pft+=tSqpds~mCy3mQ2o&b1P0xOQJW<X&2_(^mCHOahBs{T5JOGM6VTSP>{_ldaEI=Ac84wcxoWKmOlR)v4%t#XdKb0%7i3VQ)ieHvyK$d`k-?R9UqgFR#@tH?IKHuL}uFOC_002-}*=7'), '.': (14, 10, -2, 21, 10, 'c-muNAOO6sznj4c<7oW+|NsAF7_Sn@`Tqtx4^<_D?~V7fxd>SW00VXzjs'), ',': (14, 14, -2, 22, 10, 'c-muNAOM#9|Np-U&RYrOmB4xXfxJLC?;(&U3*+blIcMNfvw^%g7{~VC|NqCBpd7>Z|NlQ%fJs^Z`hQ;wVR!m!5e6av038w}y8'), '-': (16, 14, -2, 17, 12, 'c-muNAP5rvL%|jD_yY<6`dTEh'), '/': (15, 29, -2, 5, 11, 'c-oE8K?*@}6vg3x7$8G$@HSweEI?8=K*|PQloc>g7ND210a7+V$_DfX$^s;1Ofn<`{Ft3Pe0TQMsdMT&7wdYkH{8Nd%D<r`25>gnB}}CB18QO&?kRB!3n_7dmRN>YP8`9;)EuBI72xZOeb||71Ov(YKv8VN$z)eBmNNhORj~oLq&S1QnSX_*Sb=9&3}J0*j?jts3ikuj@KC='), ':': (15, 19, -2, 12, 11, 'c-muNAPD4lecG=A=P{l8|NsAWHW*j)KM0t^xY}T@6^zS#1<1S04%e)*@AF|T2J!$FXWT$@h6N5T(|I88CR{Ot;_lA})rhbX0Dsgo0s'), '(': (18, 31, -2, 4, 14,
'c-muNAPtDtccSpws=xkUfGnVS{r~@yN=O2(AOHV9#*HLk{N?}uPjW~CJWu}r|KEXZNEcAxzY3B7|2Lq(ZDb`GASEl2MK*v$8j(ewf<!WrZ2}4W4?_}>1&jD0iD-aDJn^c*GzZfzEbhT{GyivVe=+o;`<;OoWOh4>BJ*!(VaUMX{S_^o85j)iqs0XS16S)0)c67dsg^DxV;=yP_IBL'), ')': (18, 31, -2, 4, 14, 'c-muNAPQtpR74Z0`2S}zKZ=OR#{d6cIG_kIt@!`{R}zX4_r3rB{|2H6CI0{a|C<uB2*+2T&}I}xTYw_}^^rxIKq8ZnMWR3=w~$4gKqCJHkVN!BBLB^hL^Qx6?noj^V3A<FYB0@#*d>V9J(z9=`^x~`?_1Hs=er7W7~Tb16pj|of3uMUgn@DK&J#7h{>>Fd3DKNs8Vn=?0LTP)69'), "'": (13, 26, -2, 5, 9, 'c-muNzz0<R|NkFC2hMN;03>P~sQ'), '<': (29, 22, -2, 9, 25, 'c-muNpem59IEh1sFLB?$|6j1luy`)}_8$naNE-FO_zwm@S7BIm6(aLzPm%zpMPP6|PXbkw%kpm!nM;)l7<OF&%iL+v#^y$l<mVI|UW4eoTC0jp(s9XGh@EGOWw1!|#P9hFmi~7rOB9Q|blGKy_TM`b__4?v_C1Hl|5%C5c4pjR3kJM6V+9(_m8TeJ2mp9)cTN'), '>': (29, 22, -2, 9, 25, 'c-muNpa^VkR>v)Q<^TVaIU=|v|NsBBDU<`7WdE1{VDMqK9V4bJSNMjX5cvl!*sK>w+WiM2kKKCl++z^wUz>ul*{)D=5iI=$htqvt;F6RsJc&c6NXCJ`5IZ*npvv&YZT}5%&WS8x6dBIYb>AT}_nK7E%<KCMk$FGMmJw&zvf~K&Q#fN~ON%-K9RUFBr*}F'), '&': (31, 26, -2, 5, 27,
'c-muNpbFrKTXo~(pHEj-mRhi4$~r&(4+j|-vgW^l!dE>71YIv+limxI{UZxvNxZ|9X8Z}1z6)W`$CPIN3zYsPjnmzyK~7qWQ#u;#<Z4{fjAy{|+1O>x4nw`13F7fUIUZ2iYM{%$yakE;OTm<`1hJF!UV*5;abTg6|FdBxtNsQG-(X_Ud<K?}1c@#Dp9Pa{1BrHl)I9>R{)8|vu)X=O0F&MYceCPs5c78cL(cz0aAzL{iIstwvbR9&pM{_QJHVyaf`ryX*b-MEj-G<>bOzW)9SBGC0$4g3A<gpuByb1n7Rh&D|K}m(O<sdU-q&hzaOsslfQCsULSAt*A|?G@qInw1?13xLtl$3N)1OcGHk1G(UE~J3G?@SZ->dz5'), '*': (20, 26, -2, 5, 16, 'c-muNAPtoN|F4EFmiqs{C=%Cn4IcwT@c;iT3=9T4*}+1Lr~cp4WpMoeiGd;E+y82?nEd7c|G&oS|9{9n^Z);Uiy?X$gU<c`zyAN@)Bpdj&_NjKef<Cb|9=*#Birh63@G+{fht18=hXlIJN`ep{Qu8ls7krB|Ns9;*Zco~YvKR@f9Hb5n9lsaYsBCHa!cBe|8)?B=4<&G7=plVHrmC3+i$QiP-hrs008~ORjU'), '+': (29, 23, -2, 8, 25, 'c-muNpazin|Np<kaF)FCA02$5hU7>IKC%D+B|>es'), '!': (17, 26, -2, 5, 13, 'c-muNAPR{72LT5pk#`^gNhE=jK>jCWJ&S<?r;!C}fdWgA1;T&=wa5YnK!Gr10j_`l{~MsV<jMbkTqpwj{y#!>>x}=qQ3cBX&qfs}`9Fhz06`$J`QuS7WPyV~r$0b)nIt&GT<{1m90KwmB6~(^>!)Kn#JT_g1Dr{L'), '?': (22, 26, -2, 5, 18,
'c-muNAPvZc_U^m-^7p4Z>yo(Pf;|5b;IR{u==W?9Ud#O;;UDG*(P9wIdJ80c6fXLM9n2^NiT)FXiJpfrg1|-_qq!vlEUJwrS_2aN%84q-at9<j7fopgNbrsrvJjKQZjj(sNfd<^|Np-}-i2<z#s3RfLWmSmtbk+c+nc@^qP;*@{n9}feF}1H1975#K*8U-=%So6-rWjdAPWEhCW>?}'), '=': (29, 18, -2, 13, 25, 'c-muNpa@*~j}E?2Ly|^dXt|co004w!a7z'), ';': (15, 24, -2, 12, 11, 'c-muNAPD4lecG=A=P{l8|NsAWHW*j)KM0t^xY}T@6^zS#1<1S04%e)*@AF|T2C4uDpvg}VTo)ks8iE@I<ZeW8Yk=Hp1os4xs{`km{rmraFPz7I_W%E1`Y;~b7NF8hgyf0;e+!TtA$7u)Naq3ooS!})'), '"': (20, 26, -2, 5, 16, 'c-muNARegv|NlRPfnm%4|0f2e*eD<$007szH+c'), '%': (33, 26, -2, 5, 28,
'c-pOzJuE|E6oyaTNJWa&Ml@*$2Br>LiGh$16PAXkRSb=xi-yF?RE91(6N5wuAzEQzK|+GW&(froN@+>ac4+H$?)_TsZP%XRJ}2ir-}$>ll`x$%7|*^Pj{OBZNH(i<X$!(ObRu9*!KE%R%i2QYB7bK@U>}!N>IN^sheY}`5K;mT<gDrfZT$3{dBZd@>!a{$M(kxFz&vHznLb1eWeGv%8Pi78na7BB$zqFJrG<2bozg25hRi5Ky76r)y_2%0QLJhDg1hXH>O*bgTB4Ta`&9bTXZ~+8d6dY;1LHaxM&3sDgvd|!l+`kX;iH-e@Z8ZF0$%G%6TFBvkdq(J$<qSUCAu{S2a%tZQKA9Hx>m2czyV{Al|CXn<3yX_LfXREWu>2}i*c;co09OzToo+_8Ecw^P25$>oM2^M3^}FNhw#&_IQlTJ*)FdcQ~%Z45c~z#{w@ynsX5dVV#cCxT6xH1o_rRnjQs-0;OW%'), 'É': (27, 31, -2, 0, 23, 'c-muNpcv@?`u~3e2R0ej^Z)<PWyY$h;s5_GT*mz?A>Q&C|1p68K`9_O1LEF*bH7kq3K<|t<@}#QEh!ivO^WKyAn0ZCrPllpp+pK>0w63!1^@v53g~$'), 'é': (23, 28, -2, 3, 19, 'c-muNAQu$=|Np-ULsahb|Nk>F6>t9ke=QS+Xz2g{``Ix>`Jeqi&xdKm^#6Co8E69RXIyym>+OYp9Tblo{0{|xCo;oD<(~lsUfZ)<KL^rF;KE?F1wck7h!F`DwF7I{1G3aXj4M##4zREQki`LJ8A62DgE_1q<{uC%4<fw(KPs345#ER<yapoN1Lkm{`_Kg}tPSCKK->fbjAuc@U0^o*;s2*#%C+8uyxpeCD(ZgZ{|_^`F*+CF_PusTGM>q2-j(-%zTMxF%}Y-B0{{oisJ{'), 'æ': (33, 19, -2, 12, 29,
'c-muNpa$S_>pXb<&9CQ&OZb31?P+(uf4Dx&7D>T`|1j{xilO`$l)aV*S;0IlPT9yC|Np<6`Tze{e|FvLKo!SW5ehbfX@RF;tvx`dCy3F2P~Z$<OaUwK0kSy%0vYeQVJbKiS6~0|2j&n1kkAVdD-0@c_4Ge7&;W_u0kI}Q<fT7?I8#(v8Cw3Mf*lYAO(6Cj5DQ(w1&D&JAa*4}fgXB5?gokGgILqS3j86$I{*I%L0Hp3qBDRDrYm3t>%gLntNuUZfG9Bk2NeAp!Yd03MUaX)dh7z$oBsa~f!R^=7wV`#)A`zd!(8|!5#b7>S=YY&etoP>3CLDxJ^Jd`k0*P|#Tcjr0Ct%3UH'), 'ø': (24, 23, -2, 10, 20, 'c-muNpcyEwL$LKa4?h3?{n7da4u;5oFNL6@k{kZRz@xIC@ARO;au0w4f3o-mQhxy%zsz8U90n<z3SxDGSb0!k7q9{DKo;9_5bLWXM0_GxT#<o6^a#X`Qi%9wFh`I<_rc#9Fmn?`d@q>8<NN809|xFu0wTT)%&GtT$bf+l%-jnR&xV+KQi6d&7R;In5f}Lk;%wjqGM&NVJ`6}2CWBZLz{WE|#Wj9_{VT+q@*5Nq3Q%FuyT2=L!2@Ws6jYe=`2QpZw&?YbzW;b}w8sD*#OzCIXcw0Z0KM0;Xa'), 'å': (23, 30, -2, 1, 19, 'c-muNAO{4T`u=8-47zCUe-L;khbk)e{r_}9qx=7tq6!E7|H8_^ko5l*s&Ft^I2m0SY>2@<bVC^Oz*at&Lw8ExsUL3_%P>$KaJh9Jy#D6Tm#0T2I3Nj6_>TYw#E^yOX>&?=odby<V?qdT0Mp_hK;n)FVP^<qFG#o)ZVGqWhTEV1LQQXniQ2tDvh#ljR8-~@h&Nq@nPCO8a1)5LAH+ft-U{MWU<iZlF95N2APdg}apnUVd~cA2{Xm=_;XIl<QCz~f3hK0VTcF_r5ogLe_4()HRUQy4;ljiN02VRIMg'), 'Ä':
(29, 32, -3, -1, 23, 'c-muNpcsTaei6sOz`6SKeklw&&hP*K{}yB@{r~^}0!+ytKuIBnGOUse;ZI&AGca(i{c=#6fw~|UXkiU5$*VxgN6gse9R7oVKX%ELV9A|W<s^QACI6{lldSpw3M|`$MUMH=f6q@K$+sMslK%g%GRy>PjmMPS@js8j2rPLLLr(eMH$eu5GhkUGbjfaTWTb&5=b*{4zxi(oq<B7qB)<xvO2+-a1g2+!wdSKr9{-;Wrj5apH&EmZ{-XjXWXV}*l53FU_`dvifilH@fFyrQA;<DLIC~CQYdvx-N5I)y|3H#YSYUkn|M!vNe;Zh9Foa_RaRb!S1#m~rAt*^M004`9;Ry'), 'Ö': (30, 32, -2, -1, 26, 'c-muNpay7uf6bJELFL4!`7D@{w*UYCzret-5lE$A%Gv>iFEKD|!Y<3u_Th#l1B2?R&kI=@s0z3vr=5NL_4~7na}$Ix<XYbThl4K@g;6B6uYp9@*a`5M&iV&rJ+eZQR0C_Qg>d3Q?C<7qNv_)<fuk_)3J~w5IE-5fwk-h0H34%cLwT(4K)j#aaI>C+`Jxbx16b`jgfljQ1)?CF1~6w8Lbe|)FdM>|3+7Bi$ku=bb|4$ngODu*3!KFvTZAk-53k9M*j+UT!g0jzqi6_+?LAs(JOlB6iJ{m74@qNGcktW?agU(H!fQ#mQCc5B0yPj$9Ekk`If4ytfrM7u@NpZ@1jYUnJCwx1+wmTea=uOxK~Gsc(KF9I{r2PerTIxhR7u7Fyw({X'), 'Ü': (30, 32, -2, -1, 26,
'c-muNpa$Ss|9Q6v1B2K7H@R43YybcMKY@Yi-T(jpR54}ifU=VqnBD^^EV8^Czw8%hVDNeHrhtJ;;KzSB@Br~;pqvIGWEmI?z`PoSaUuV=AULD4#LH@eWt$NKvH#Z~I8tEQ2?&9#|8o%>wqGFGjR=9B|1C&Sd>SPClo8H9_}>pnwgGIkBaEx?=c@pcti(5v>}4SckA2twDJZEY2CVr}t~wXHT<oR)*LYA9m)~<l`uV>`7(MN=2G2VE;@h7O_qR5vQzbD206uTx0{'), 'ä': (23, 28, -2, 3, 19, 'c-muNAQ|v){<1@efx-XLt8`@H*8l(icQLSj`Tzf~9GY+k1M6p?uq>(}+XXQVp+Deq>pXb<&7Ut%k4$ht5}xoM0S<^E3(wQ$l<+zS5<kX-5Z(Z$#Xo?=9TCFL5XN4Ra4Fmr?z9cJKmCQ8-VPJBdx2ypFw7u8<`alFU4@xp1+s7xh_fHWLJ{5y;#6P=gY7Q>v34K}&jWGh0~vg8kcIs~oFCylnmbWk!ng|Rv~^pc;Q|q7$~yJ==i^l#5G&!r!~+1Qki0P'), 'ö': (24, 28, -2, 3, 20, 'c-muNAO|o`_;^u|fkEfo$0>}+;=cd?|3AdQa1cm^po<@XhzFyYb3q4a&iPNM<_s86Z{7dw`;X^`I(3jmg_iz@gSBFCVUcS<{_iwC-h>}O#$8F6_$H9L2_RMnh_x3gYzo%z1Y+8PnT`<gRxn2v#FYFG*UG@K4$R>KG1<Y)9T4$-U=AyY$pmJe!mqvsVZIcY*#{9f26LQ2OnWfX4(ibLa7T25SUcgta0TLDp2VL(#!W;(2rT{w51*C7$RVfJdf@qwA1@AfXptEq09V4dO8'), 'ü': (26, 28, -2, 3, 22,
'c-muNARGAHf1Sm^z_#S`5d~BU=8ymX|CM3L{Qv*|8Z?;?KpAPU%xZMg9=uKmn|4&5VGx0U{}3R-z|aC=O(7`5z#syXVPIG=h-DU{$_RmFq(RKJs4}cz8BGxL5~>Wt4G=#7$k6zQCQ}RIpV4ABzx)SHhT}Li?A9!W&?gX5rDwkUdcHLr;%a0W(f|N87RS8'), 'ß': (27, 27, -2, 4, 23, 'c-muNpajTP?tJ|9_uC7zozWy1>wf-+fxQwaQr#f2h3cFtlY#UVZX_9<zd(^QVCEqps|87_6{M*Z%&Y~nUb7&iHiD$`fDD1m6CkD~LJDNc{~QK}xDO!4r(3}YsUr|6e-O1=55<8{sS7~zBqIYBDJ~E>g#nusFNnOsg-wd#HHbPYflX>MIG|p7Vv!Ph2$uUdfek~7LFFbSgpUbhNHGYmgUFp>!;oTNh<OW^OTZ$<Ab$tMS%OW9!4<^Wjw+S#e<Fxu4&qEem->|@&Te`Z$o{Slk@x{|6;KKW-g+>gO0n8CAGr7Z$J1R!0u&@o05seLaR'), '·': (14, 17, -2, 14, 10, 'c-muNAOO6sznj4c<Ea1q|Ns9a7_Sn@`TqvSs{--f!g!j$fV`=2Q+#i{pUuTE-~a&5ZW)p'), '–': (19, 14, -2, 17, 15, 'c-muNAQGhfM}QOxg$5-60P~tI^#'), '—': (34, 14, -2, 17, 30, 'c-muNpbAL&j}xTOQ^hDi0s#BlYPk')}, 'SB18': {' ': (0, 0, 0, 0, 6, ''), 'A': (20, 17, -3, 2, 14, 'c-muNAPt26|F45Cw(tM{X=p+k|NsC0#EU96arf{4|1(j9xZazu`v3nDidf2N2791x8)UJwaSRMs{{LTwBxLrAoq-|q|Noz22(bnKp`a2jB=l7dL{0zy{{a(BtY|-&vIZ*jg$gm=N`f%%{{O!n!cqZB9|19bfQ{54K8ye=SVC('), 'B':
(19, 17, -2, 2, 15, 'c-muNAP#8!hk`E`8hBxXHUIy=VBoPj_5c4V7GxoaaxYXNmVf{Mr=tq#165ff3-Q`r{QtKD$#^ihk;R5$BbUzn|NkGlqMF5c^8f!2+$cf}Gk}^6P=${C|NmPENr+Q(Do{~9iXZ=cy1LMbfoK2#V)<nh'), 'C': (18, 17, -2, 2, 14, 'c-muNAQG@fZ+QIu!?jI$YES{yi~qkDN^lvi{r{f_EFk{q|NkTqgK;}lWXAvhFPOkAdx!|@r~m)gq8O|F|NsAf6cKBnNE?QlK2*nGm;<uwIU|_W@!uBio&*p><i$CN41?Om|KIY(xol3q(t;Zmv+>D~_ZON(hz$q;?Ylkl'), 'D': (20, 17, -2, 2, 16, 'c-muNAQou+2ZMhfuFkbXh}Qi7|AK+Tbj$z$tGH0a7#Nrj|Np-pO^m@0XoL%zm>^JW7Md8tm;e8dql>-%|Nj~h>V$yi%|sLP2Z}jix^EqBf580v>DpX-29f{(S-4<?'), 'E': (18, 17, -2, 2, 14, 'c-muNAO>jsM}Q?zv6}z?Uw|1?h!BATsK|;Q{32k`L#i(9b}=wyoWUW2?5{Hn!~p<Cc}pk'), 'F': (17, 17, -2, 2, 13, 'c-muNAPhAABR~&CsOJCwH(<sJf&wrA6*y3WPXG)`NYaAU7Muc5zx-h!761S|)kEa'), 'G': (19, 17, -2, 2, 15, 'c-muNAR4g7tbg?V^PMBzt{hMijm!Ukmdmm$6n*;N01=UV^8bGdnB@f%n*IO(OC|{O97Krq^Z)<rP|eo<|NnnKs*p8Ms0~w9ABb@R$oK*lVgs7B8q6|*34v^U%7`i?`Skz)C{!T^jVu4ZWQ(#&<RF9?*kU(6`SJC^>G^T8M28CiOteeo'), 'H': (21, 17, -2, 2, 17,
'c-muNARcJ^2ZI?5JrIToM7ZYv{}*7!ga7|qU}|Y32nV#b2wf0|--!bNe)4LD'), 'I': (12, 17, -2, 2, 8, 'c-muNzy&n^gTV|4ujc>%7ciNDVWYYS8vp=712U@'), 'J': (15, 21, -4, 2, 9, 'c-muNAOtl2gTWQJfCG@H!7#|VjzF#&g6jd~ib9wHPZ=0e{{Mdnl?nJCD0<@m|5PZKE%VIRkB7q;hyVZ+$v~a'), 'K': (21, 17, -2, 2, 16, 'c-muNARcJ^2ZI?53?G2h7npF(|Nk#Qw8`^XEDUIZ{+}z541fq0d<kJd6J(zJ(t-g^@a^XR*M-pqfByRa|0EB(_Q-$#|L<l)w<rtf$kj~fw$}nhXQB%-OaO|up$jrD0*V%*`<-PIh+#rPxG?|#i{M@~'), 'L': (17, 17, -2, 2, 13, 'c-muNAPhAAgTV|Wp_>2yU!bTNbOLW&unIu^0tPNb_?-a&cr-b('), 'M': (24, 17, -2, 2, 20, 'c-muNAQd?L2Z2-wrytA_fpDe(nKu|gEdEbGW(G{hl;eN?|Mvs2$`7H4uUPT_{~;iQ^@%^KxG9ip#=sDNiwRYn;qd?es~8wAWiX(L2mJs4N6GySC%QP(?f?HL?`dK{7iY-+|NqB#aZGWpxBvgoVZan;X#M|B3!69;AjHAp69Qqc`HvhvqyPY-5_Bs'), 'N': (20, 17, -2, 2, 16, 'c-muNAQqVX|NsAA7?^nn$lL=F?fC!yy9JnK@SlePF82SWBAVD+px`wDRIx41AcI&@#Tb_Z1?QlOF|Z#63Ra+sF^Jv;x+nxyj6vi5|Nr08QN<XXe*ORd6HSaE8E7QB7})JRaR2^K0I?X?Ak+~900}BoHv'), 'O': (20, 17, -2, 2, 16,
'c-muNAOUcsZhQ9g^Q{H82qC@O|6c`iNwog|zk~xSB=h3`e=iVY$^ZYWpknj?|9=2xSpNV2-wn)S`~3g^N-&G{&;S1m!7Oc{Y#&6&^Z)-Zff?37u{Ma<{r~?T;Z(==1=Bo+1^@rwN3)kf_SOIY9w5e||Nqy({9$<a|H}YQ@#g>kS8&2T$CbY0`LD0H7dkMI1ONqsSdR'), 'P': (18, 17, -2, 2, 14, 'c-muNAO>jshk)OY=BvQOYX1L!!63il|NqbC$RZ3JPyhcvjUvLZ7O0g6MPxltgd16e^ZEb(r%+5@1vJ?VAp!({9xqU3Ks6Z&kRt-~7Y76J007$UQIr'), 'Q': (20, 20, -2, 2, 16, 'c-muNAOUcsZhQ9g^Q{H82qC@O|6c`iNwog|zk~xSB=h3`e=iVY$^ZYWpknj?|9=2xSpNV2-wn)S`~3g^N-&G{&;S1m!7Oc{Y#&6&^Z)-Zff?37u{Ma<{r~?TVNrJ(V%`^I^Oitl7ykc$A8xM)L`?1#l)32t{|zvI7~J{)GJsRO`TzeloCyD>Y<>Fc|KkOYXyL&1;I<nNdf+&G{r`Ujx}g4wr%Oo*VFmyMabWl'), 'R': (20, 17, -2, 2, 15, 'c-muNAQou+hk!rN*O(zhYySU#!5~r&6!u0HV_?|$|Nm`tu@ayGLTF;8K+WuEVw?W|-;HU<Sp{S<5cpiqjOrE^_b>nd=cBogA@l$LpIT^QjK}}~Kf;J+ufd=H|I<<YJA;9tA4Cff9Z(DaDokQ|'), 'S': (17, 17, -2, 2, 13, 'c-muNAO;AuUitR**3MFGC|~6E|8^M;)vo{lB_IOb|L=h5$uNPV|DP~{Xg!#~p8x+>8X=om^B)MFt}WAm32^QH4*`qWVL}d*&in+4R3qtQcR%p||2YVI&I*Xmum2xI1->YQDAuq4w?GB{-;0uDS6}}Boi0RxFL>_R=f6K+?2#tQ=L`UPXhiA'), 'T': (18,
17, -2, 2, 13, 'c-muNAO@WIj|5D>A{jse$N^D5aEOR;BSfTG;f6s)kibBS?16YngMnB80D8hcD*'), 'U': (20, 17, -2, 2, 16, 'c-muNAQq(j2ZI;}1{V<R0}<Wv|NjOEYsLbYN_vQGhl|ae4-;GS|NkxsYw;AASl9pmcOa~zMKCcNp!4-W44I!AaPQ6g|No{NH@nrDE+jukZGZmj=aWqV3?u;nP839-'), 'V': (20, 17, -3, 2, 14, 'c-muNAQs5{2Lm1;a|4jJfQYX6|Nk8)m=*Yp1**~xD4hUi?QVo?zw-b8Nf532OBybg15{`Pr2E$*tl|6o|Nm?T2F`abNOsTs|NkpLL()w~BryY^=3Iu;1t^X@_W%D?vu}bZVzEGlm*%2+hW#~A&=}2!UH|`|Lie@OKd4to006}}KXw'), 'W': (26, 17, -3, 2, 20, 'c-muNAO~pt2Lk~xYcWt@36Pfqk=y(K|9KEy`TzfWRv>Npk_oCS7pO=cNS^}Iu0XnT4$M4Rph!LggY@6G|Nl<|@^ARStvdVv|9%FB?Bg^4|9{HJp!tOZE>rve{~uw7J>{N2&E^bMYZ1=V1&YKA{#IxE`2T+g!>L##m*4sSe_h;l28NaY|KE`QC4?l?`~Uyf?d=Q<kwDE;_96S$_CMGL2EL#F|NqTHmSKAN|Nk>aAY&)gYX~s+|NrSAIujZk2;lSozdMMQ`uD${fqVb}D&BG)'), 'X': (18, 17, -2, 2, 14, 'c-muNAO^hn4+3)-0zi}tSSS|AY6j98-~3^!*8czh$DD!X<b1e3(U<@K-{h=)z=tr(AE<BB4+mt^7l6%12K*2I|9{AjEF$<6sAvJQ$ch6~fI<NXf$&cXoY(*Ve<cPJkb0ZUz+m$G|Nr$ck?os7WGzr%0+_!B$oj*;FazwpFGK|e0{|^NO%n'), 'Y': (19, 17, -3, 2, 13,
'c-muNAP#8!2Llxbh66x~1tJJ!zTg8fcF%^X)BW@Re;<$zdM^ssJNf_r-&zbD_j3`(3BLaSe-A_bWo9HRQh^2+eRV*#mFYB4Yz3-I9Dzb^s6r}0As6Zhy@2?WgMoMe0GxL}uK'), 'Z': (17, 17, -2, 2, 13, 'c-muNAOigP4+j|#0SgexdFB8AKjugRGk^*jk@N)t`A3-%e7Sf3|9_B2@R<(-6@(*cXae%*A@S}0{{MfA8^ITP{Qv(iV<ZI|fEr4X_}M`IE=CY*M-7Nn|Nj5~Ye@!#KnTJs|7(cxI{+@DNge'), 'a': (16, 13, -2, 6, 12, 'c-muNAP5ACPrmv6YEKM|-}Bv@Q|-wA|D`bgY#`zB|NjjrU!?Em_y0if8p36|@c(}Sr^)~SZy<c*|NoyeFre`7GcdTo`JB)H|92JI2In(a9RK=cOE$<v2f~g80H$O&`v'), 'b': (17, 18, -2, 1, 13, 'c-muNAPi>w|Ns9EiiiW11gakVdNxZ8A@IM8Kjh#4+x&2W-@FVAr~m)2g9|(ZQmg*|Ka67NqW}M|<5q!T2GEwEzc5?Co~wHJ`}u4!2BH7}L7-11'), 'c': (15, 13, -2, 6, 11, 'c-muNAOuuq-~0LMM4cjpXZ_{>3m0y^OE)0goB#h80Vxj%SL6Tx|BeWq_CT%~f(w#$LNfTq|Nq56s^lFzm}~Xr|4T<MyH_PpX{8x=etbNYK+t^*05lCJB>'), 'd': (17, 18, -2, 1, 13, 'c-muNAQsH||Ns9D6cG=~1UwIa`F5xpArSHJ|2Y}e+i(G<XaE1lGcc6E1$2Neuw`Hfh6~sO1x%3*#ZbZY^#A`jWHUgvoI$pQfx+v@SFk(&|JNZV902g0PeK'), 'e': (15, 13, -2, 6, 11,
'c-muNAOtk#Kl=6YKme3y`|bY@!KnZL%OTub|NjRuFueHxTOP#I{Qv*I6$8VC|NrwrT>JkpFdf9z0y69o<}%*<|34E*Tl_Zy^Id=be_+XJd}$d}UT^8s-*3+pvJiA200KKR1O'), 'f': (13, 18, -2, 1, 8, 'c-muNzz5jMu6+6be+z`u_y2ztS1*+F?*D%&m@2;i|NryAI08tVlK)_kfhj{>P72tXJ9xdq006!RH9i'), 'g': (17, 17, -2, 6, 13, 'c-muNAO?6I{_^cm^?xAH0rMmN{XZw8di($X8xVP>XaE1lGcc6E1$2N)Z5bGX;R5zR0aFGB58Nu4p8o$IhinGOmNUq<Ffe!>`TFfp&Hw+`QCt`D|NkK<Ghsi7Z2teh0w(akM2J85{r{t!PyzO^jrV_jIFifCKpX%7U$9S='), 'h': (17, 18, -2, 1, 13, 'c-muNAPh?W0|5`RhyaxY{11KkbifEnV56w<@BdG^5dx+R3>W_Yw?haBGcX+a|34hXP@q5rxdJI5&;2)f0V3BB5f}^rr}Ixe'), 'i': (11, 17, -2, 2, 7, 'c-muNzyWyne`$a+z5f6I3T5&gf{P+R%6}l>fv^Rr$ON1FKLwWy0Yo4tp8'), 'j': (13, 21, -4, 2, 7, 'c-muNzzf7rf6Re%lK%gH1m{Se{gjJUOU8d7;DGT&27)8;|NlQ0Fe~CLZ`A+)2Oz?>*S>$b)gz4G#{i_$Gwl'), 'k': (17, 18, -2, 1, 12, 'c-muNAPiFe0|5`Rhyc|De1PN+WC89ii`bA=NS<jz(PIAaharl<i+}$gh#(6X*Z%*%mj&4j#`XXI_oG<Ld-ebSScK>P+e`tGCx{3P1^{LUOL_'), 'l': (11, 18, -2, 1, 7, 'c-muNzz$OW0|5_&Eimv*uyg*W;BYJh01a3#Tm'), 'm': (23, 13, -2, 6, 19,
'c-muNAPuDa2ZDfO-@hC(GuZm^!#)G3xByUit&s2k|L^xp>HqovkOLvC!@&3(sE2{!&j0_$2w^@3hL8XM8!<3k{Qut@A<V<T@ZtY|ps^SJ|M#JuFxcJyEx@GD2N1c0M4vMN0Q{t1m;'), 'n': (17, 13, -2, 6, 13, 'c-muNAPiFe1A+gcFP{z=K}7_B0vkn*fB%2VjSw(pV7T!Aza2tAn1SKQ|Nr3#0UoeG1i1oWcl<Yb0V3BB;cf;13~)cN'), 'o': (16, 13, -2, 6, 12, 'c-muNAPi(C-uU+Y<|G*?*ZBSaiwbh*|Gzhe@UQ&;pTNM7@c;icFjxKm|NpiO40b?D6T}BGOc@x=fRqz9d4|g{{a4}UpO;56pFwug%^yE*O_n9XsSE(31UGU'), 'p': (17, 17, -2, 6, 13, 'c-muNAPi>w|Ns9^)q`KpW{E*X9DpKS{2~AT-{yx4{N`m~IQ{>B9bDiUkXrTs|6#bm9U!&n|NrZ_RbZF_v?b^-vMqP29{zql8_6AaP@GCo0OXhd|9u#U1_1N9O?d'), 'q': (17, 17, -2, 6, 13, 'c-muNAO?6I{_^cm^?xAH0rMmN{XZw8di($X8xVP>XaE1lGcc6E1$2N)Z5bGX;R5zR0aFGB58Nu4p8o$IhinGOmNUq<Ffe!>`3iQ&4HVaTkSws{Kf*5r005)~O_B'), 'r': (14, 13, -2, 6, 9, 'c-muNzz1sn1A+bSPyg3|xdK4mMPsh%2wo6eDTpVH!s8*Gmjbfy{{aR<006i<CU^'), 's': (14, 13, -2, 6, 10, 'c-muNzzY=SKlu6KbhkE`!}{?5EiHDPV=urw{r~?r0x4q%PvqDC|A!kqIHCIDKKuuQk3~=}hgb6%Am0?k*7(W=B=`RR9|h+9U$4rhd;k9z84!=rcGlHzKOZd9$L}fz0LXtVmH'), 't': (13, 16, -2, 3, 8,
'c-muNzymD)|9?W5GvPlN)R3YFm1B;~(fR-XC4<6$H86+$!~Z`DB~O_lQoa{{d_HM|&&3P?5AQ6g'), 'u': (17, 13, -2, 6, 13, 'c-muNAPi>w|Ns9EgA9=TuL2Qq00}TK{Gdd@9xTB07cQXw|Nlz{1|@_oEI0rEw-;Q95Ma>S`QiJSK%g1_D~ND60|0)6JxT'), 'v': (16, 13, -3, 6, 10, 'c-muNAOu4Gg8&D^jQ{^%fCZ#~|Nkowq^Hh<s#y2`e;We>&nFWo-{t@Rmuw7~r{G51`2RnO;Zg#eU-19`5!<&MaK6CT|Nl?-AlW(R|Nnm~NPNTp|93DD1pu!$Da8'), 'w': (21, 13, -3, 6, 16, 'c-obYEertx0EM61nTak*l3*&qrd_0y6{4nTDnYoW(Ybb$L`^drlP+Bl2yEu_vva%17r(u|_oUw`@FuSY$AqS^|Jc+C%F-OFk~0po6BsFT14m|138f9b(cVFjtR23sh7b0tvxfR?5N!>?yINgXT#At_z2;qI@34v8+Co!WLN6x!oYPW^M^69o1Q=CD!~'), 'x': (15, 13, -2, 6, 11, 'c-muNzz<&h2ZA#?K%xZ9ulxW1wG>18MGlBG)87C8_v^jZfGL-J`TzfyB!u?F|Np<sz<KQFAOHV<m>I^Myh-fY|NqTUp5G&32FJhu|2l(tKnrh3fb9N%hky$i057#NR{'), 'y': (16, 17, -3, 6, 10, 'c-muNAOvjwgMbFZod5ryfCczI|Nrj*q^I>jRZRK+e-i@(??*K#U*q5Zf2s^w`{73H`u~3#!{rD#-{=4TuYs@G;C!aL|NnpLMzXW$Kga|G5cu+cFN&k4{|`suySze}rtnQ!dT$*<PUOUwPxIIrhywsqw=&i'), 'z': (14, 13, -2, 6, 10,
'c-muNzz0PBL%|#{?+cJf`v3or1B|Et{r~?8m}36h|Nn1dgz?t>|9?*a#wq##|A!HbWApp}|1<`M0<f84Pyhd4!~o;PpxB2S006Z}F8}'), '0': (17, 17, -2, 2, 13, 'c-muNAPNNUegEU$WJx%`=l^$CktP3MXh8Yy|NpONU{L-4|1?x!+yDRF3=GVF|NplE^O?T<|6c{9Km7k+3l@<4|Nnn6kbe39{{pap3Q(W`NI(7me+_mO%m_2;Ahv7=+rsqc|9@MEfY<;3>lhf6|NlP=bLoWt-&}+j{(q?jcYEmm4?piul_t*P3;;;TPuB'), '1': (17, 17, -2, 2, 13, 'c-muNAPO*NzWx8-1;MvD|M)+O!2U{cQ~@pq0aO8oK_bxc9|HCe=W_r|Tr+z'), '2': (17, 17, -2, 2, 13, 'c-muNAOeVH@4o-@)7eI0n81eb5xfd({{MfX1QX~661*S(|6h)x@%aD$*HHvc|Np-ena}<C|9>xJf$IPNN|5;>zaKgyahdD?F6TkwD<1ik52SovK>0DBo?0^?3!M261vmu=0082OJdy'), '3': (17, 17, -2, 2, 13, 'c-muNAOdg%EWP^q=cBcbFoBZ)<${7a|Nj4rg$W!4k^BGuKY^n0(EtD2k+`D8|NlQVK=8Nx|NnoB60!!VlHdP71*4cT;s5`S!pH(%Kwa(-=7DSw=>il8g$ir|k*)v#|B-_V{I3@iN&o);e=$_Ic;>ddKfd2yWW_)n0050sJYf'), '4': (17, 17, -2, 2, 13, 'c-muNAQGs4{r|rMiO+oOKdL~*>)R*-x<5ltAPcabTfu-L(ELIeMZom8KLfG=$F)TaC<4y^;ot<4#V1hRL0Di9#EcrE{0#tE{y@n'), '5': (17, 17, -2, 2, 13,
'c-muNAO^ho4*?pu1r*S=U<ec)e*g7yivV2Ub+4jG?f?G|<X{5qAmYgX|C>?twf_JAhX+}p2xzY&gxN9+M7I6^|CbjkaG4QE9{c})Csc9E|88-yhX4PcsXzsIQ#arK_U&?q2m^5d0B6QK`v'), '6': (17, 17, -2, 2, 13, 'c-muNAPNZ7o&EUbLc1!AulDf&at$u$mk*$P=1c#tG6LxYm_We)|Gg+C%=-U-*77Gmua`4J1&;pz|36i5#{d6|p#s<b|9`~5APW>Wg$P{!|NkJ6`t|>R1w>%i|NlFI)TjUdyC4FMa23T60fiq>GyZ8pO-=dxKUDx|ODo(Z)@xt<e!n-EIFB;`04W$tcK'), '7': (17, 17, -2, 2, 13, 'c-muNAOcMJ4+9*y1QviPl|T2GPz2`uPeL(C_San&6oE<q6H)kL-|nC)==dLx!WaB>n;Au*?tdH#pXbdjR0SpfV^H|)&u%g^5DfrZ@G5Z'), '8': (17, 17, -2, 2, 13, 'c-muNAO>j6zWx2rn*$llP`=*R|G!LmSO5RN7%I^J|NnUghLHdN{|Q0_n*aYl$G{Nu|Nk!zh=ACY|38g+mi_;o2Q!p!?!W*4|3CDE@fENAe{RIz`~PnhRABS}{}UJ(1b~K`fccEy{{Jrl(qI1nuK)|M{f7vA{r|reqUHSm{}UM)gn;6{5CPk-|6dsKPx}9V9V66Km1#G={dv77fr%)eGXMbeBvSM'), '9': (17, 17, -2, 2, 13, 'c-muNAO?s{xc%eHg&H0hU*^gGj~0?={$CV?3M~Bpe-Q&i?En9BpaO6H|8Hbqu=@Z12QQe<{Qv*|N(KfaAmsp2@d>8le-uPu1I&#7u@C{>FaJN9OP&S__&`n7-SGbF#q1CN|0^K7j^pqDYfxsyV`d=f|NnmsOyK`qDFMId|NCKz*+Mow`uTjlI|Gpb0CJ>DYX'), '.': (10, 7, -2, 12, 6,
'c-muNzzWo_zX^u0>i_>g1Qojh6T<)i5t#?O'), ',': (10, 10, -2, 12, 6, 'c-muNzz+WWuYfSP|NoDHu+0Dem4&co|6d1T1pIv@0%7^>m14jJ0I-4#*#'), '-': (11, 10, -2, 9, 7, 'c-muNzz#V6gFpislTrWxR2&Nj'), '/': (11, 19, -2, 2, 7, 'c-muNzzsV7XTzA+{>wsHs{hZz1WW$c!I+2t>qA+hfA7Nt6aP<uF*p2ogt9olzGHzh{r)e8$<O^C3}rFB{J{fdTL0e)lkfVU24mj*CyB?+3;_3N9Tf'), ':': (11, 13, -2, 6, 7, 'c-muNzyWyneJX)6z5f4y3uW>i_*}_AB;Yylxg5&${{R0S!h~|%dH_uO4?_'), '(': (13, 20, -2, 1, 9, 'c-muNAOHkf8{urPS2tB)?C`%om0@h<@BgR56)pJx-vh>G`SSn2ER3W3|Nnm$7{}%R|KAKqoL>xBm7y5Gun@^;2Gt)(mNLZsLpX<lA>b{-p$rVdT}^ns2mnOcDX;'), ')': (13, 20, -2, 1, 9, 'c-muNzzu}=IV17v|1aZ4@aFtK&I#v8{`o%*A$9WqUj;a4-v9sQa8BF*|7+l!n*aX~W9OhKLoonov?7wFGm)HgmIubJ`@fD4?uA2M3<LoHHYzEd'), "'": (10, 17, -2, 2, 6, 'c-muNzzRJ6pCOS&a{vGtBMM*'), '<': (19, 15, -2, 4, 15, 'c-muNAQcFuAJRhRbA)dA`TxHToX_Mu@8kdfUzYo`Km`nYpZ@><eQg*gT#5Mq|3A0H@FJT66#BM0lnccs{jSGAgH{A`APX`%&HeEI|EDFsEGUi$L3ISosfV=~C;$KkmMRn'), '>': (19, 15, -2, 4, 15,
'c-muNAQFh5%o9TslKB7s&-NG|WFaPx`S1V#|GLzR1zD8MZ|Ud%|6fh9K+(<_vijTq|Jo=DeV2Sf7Gm{U@Ztae7Zc53#=Fmb_y7NwC7#U4j`+Pjnj6Kbr!bsK9smFu>?#5'), '&': (20, 17, -2, 2, 16, 'c-muNAOSGN?S1<D|Ns9yNMcj}|Igr7JcKO9`1AiqAZ3oC?$Q7MvFPTd{{R2o8C59o!B3!|BLl+%pgl*xLdpOBXLbGm|Jj0pLHWM|ScvDt|KDs3Gyng8r_T`ak`XLs{{R0ypc9w>|Nm0+bPvQd%m4p>vNABRZ2tfM>l;Cc7~9ML|MP$}$NvBSA4)^5b^H4NXN4@k+fkscHzlBg3jLSA{CsdATk#lB^bPUB1OU(sS*Q'), '*': (14, 17, -2, 2, 9, 'c-muNAOQIPSHYN)yJQ)Dr!&?RfO&rJU%R|Y+wy-oM3S%i<*#oWjG#(+D_{NovCaU(@p=2!>t*K7|BJyqsoiowQ<xfxu-HIr002|A9#H'), '+': (19, 16, -2, 3, 15, 'c-muNAO%$X@1c>9#D4_P!6`&zM-Tx3Tem8a'), '!': (12, 17, -2, 2, 8, 'c-muNzzr7v|KAE@*Z=>Y2xCY8|8E0hoB#hW0b>jQ|BTT5?mU8hdKH4bt`EUp(}UGs=jV6yVeHla|HC!7Jin`t$GHpuEkqhM'), '?': (15, 17, -2, 2, 11, 'c-muNAOPg6j=lW#aG^Ssd*zZgSJ1EjpR}Re2q3ZM|NogtI_CcWzZJn_x%2;jH=L)n<^TW3l5p;aA6Gg>5Nbd8pjeH@MFlmV5AY&!KmY&lhg%jW0033nCbs'), '=': (19, 13, -2, 6, 15, 'c-muNAQDLYM*tn1Li9I_JOBW`Z!F~'), ';': (11, 16, -2, 6, 7,
'c-muNzyWyneJX)6z5f4y3uW>i_*}_AEI9CgBaC_e|5PZ8?eqTtC^Po|eO3rd?bQ!csG#a`Q+#Fu01h4$SO'), '"': (13, 17, -2, 2, 9, 'c-muNzymz~pJB-PzlMCy00RI&S`^a'), '%': (21, 17, -2, 2, 17, 'c-muNAOV={`|x~)G>Db^RS_yC@!`K&?*FsQ3=A@#N?{7K|36`n`TyULfnmdW7MNh$|LY9=|Nr|j1pPII8<`1J$@gRe!XEJt|4p<1pJkf*hzH4b)BPV_tdOzz>nl9x@u%Z1NHVOK)-de&-=gyEmli^>@`I%G|NkZoC;qp=#gxBgGMN4Uug<Xh|01~H?qiG$k`R@xFtNB_+CXy0|0d;czcis@!mnGv)Z8bZPq>g0YzzRMGf#^'), 'É': (18, 20, -2, -1, 14, 'c-muNARcIZd}xj$z;|Q2Fh2GF5nu^atmgm!7huK|B1GT-Dzc&nzX%xgkg5y2T?`BvXK;uh`|AvmVFv*2AWsP'), 'é': (15, 18, -2, 1, 11, 'c-muNAOdh)_*aO;o%K5gi5LCVi-Aa>G5^u8j|T#vJlk*ocL+xP|6dN_-unMPh=Jk7|KIW;p637m|E(ApF8u$W58~SYhk@xJt`?ACk1&_<-v9rZK-%KJ5t#4#^Zx@&PUB0<pz?Z4pZ<P(rjUi80|EQ^IMx'), 'æ': (22, 13, -2, 6, 18, 'c-muNAPESRoP6{BVlJc4(QluQ#lb{-e)w|fp7?+C|1lAd|Nr}7qO*a7+5i9l(-|19{{L?P5f$pW_Vqsq1TZk{`TxHeEXZ{J|Nne0ng1}b8Z2t`|NnCa29Rhtk`wg*|G&q;pa&Ff1oG7XyMjeoZ~p)1%(wXe@Bgn|xU`S$WP~VIT>A9a%Z;vT3m*P@f1#3-fkXfR#XnO-'), 'ø': (16, 15, -2, 5, 12,
'c-muNARc&%KxmmsH@|<pSeNkD63jJu|Nn}j<f;GvBOub({{K&7V3_^?|7kE+^Z)<<F3hu^0Vy>Q-ww!d-?GISNI8M{DnQ1IxhxJqN*k=<^#A|!7#I@&|G&Wq=7#`Hl9Idd|Dze0tNt{l;{1mnx2DKJtW)$S!3zuk_kKU5'), 'å': (16, 20, -2, -1, 12, 'c-muNAOcul`Z%8x!R35iCwZp@!Poh($uMg-io67}JcIS+j|(^%hy?=0C*S;jwI>F~@A>Y{sdnW5|56x#Hjwc6|NjP*FVc7O`+p#K4dF6f`2W9v)8zmEHxRz@|NqY!7*P2485msPe9q_p|GNrpgYy|Ij(>f!B^zX-17XJk02RSS#{'), 'Ä': (20, 21, -3, -2, 14, 'c-muNAO)yCUddqiVm69c;s5`<jsO2LBa5j$S;JuTaxM`jhW`JrgD$r3|Nm)dLK^@7|Nq2`DmHQV@BjZZQG~eOo3Hx+{}PH=%4r6Bpl%yvv9oau3|IdDUxp-P_KKZ>A@l$LpJE8H1^=O-5-ue4RSrZ=|Ns916HKgVKbW!xD)fa4G2TjoFz){Uza7F-0ZJbMF@AuJ)FD390a%(&Is'), 'Ö': (20, 21, -2, -2, 16, 'c-muNAO%R@-Oi}?WF?AN;{X4$h5!ExAdAV|+sUNybPXZnI8wJg`}z6S0$YTT-tGUd0=Xnw|NmdY0W<8y|NmYf#*+X4S3$+*|Ns90%&`3b|GyiU#rFCCe~8Oi|NQ^I5X{mB%JxBYJpcdy5}08P6l;Ts-T(jp5l(e%Uog#MSn&V<eKdO+WMBRN?*U>g`u`v9Wy8DwUj}fBH~;^?f)nmJuJj$xe|^2Z(1D~tX8-^$x@21'), 'Ü': (20, 21, -2, -2, 16,
'c-muNAPIE5v0<3?(g;QD?f;34fBv_ih;_fUW0>>G7@tuo|G^-Jfx!ht`#?l@{QtiJ!kV!Frjj0F+u>p}=flL-{QtiT!dg59Cf4=;{~ZYHXc0`z2Izb}5JTpt2Hbn|{{O$}#?5YZrVGi>QQM#Y`uSv20BL~^0C;pzaR'), 'ä': (16, 18, -2, 1, 12, 'c-muNAPoB6STihmVF>4c{NKy`?|%cF-}Ba*VeSik1|oq#@yR#8U+sy3Yya-esdnW5|56x#Hjwc6|NjP*FVc7O`+p#K4dF6f`2W9v)8zmEHxRz@|NqY!7*P2485msPe9q_p|GNrpgYy|Ij(>f!B^zX-17XJk0Bs*b&H'), 'ö': (16, 18, -2, 1, 12, 'c-muNAPhK;UlZWJe1;3gH~s(L)Aj#<8yKJc*fjyZi>J95hy*edZ+!cHbCL{{YyAHIMFqL@|KA%!_*ee_Phen3`2YVJn5+K(|9@Ks20I|73F3norVI>bK*|Z5Ji}#}{;P2F&&wm3&mcSL=8qq@Cd(4zRsdY3LqP'), 'ü': (17, 18, -2, 1, 13, 'c-muNAPUTVX~3}Vi5i^G{P%yY;Q#*x2o<wm>NBi)tinJnnDPJr|2qsaK=MCSlLJVAf#C-w0`_15roV6j_5c50GB7A1Y+<?i|G&N9LWBT=*3J*#&jbR^_+LSc!vW{jNf`'), 'ß': (18, 18, -2, 1, 14, 'c-muNAQD)vdG_ne*%DT`fd8NW3k9VQ{@(-_x$*zM8UsVf|NkCP0gnIw|MM{<oc;fQ5>!M0D8f_s|NnF=31pG?|1TkI0*MI!|NmM5MTF<}|Nj@2P((ui{r~?l99e`R_B)VDLl$As23r3LMTCLx<Nv=ba1oauHf**(|E~lKr2GfDIb`p<59dqRi3}P57PnmI'), '·': (10, 12, -2, 7, 6, 'c-muNzzS5ay$*!1>i+*f2w|z;coWP(EdT(KMhCM'), '–':
(13, 10, -2, 9, 9, 'c-muNzzsP5LjVT`hnfHY2s{oG'), '—': (22, 10, -2, 9, 18, 'c-muNAO&#zM*|$VMF$=L08#lM0R')}, 'SB12': {' ': (0, 0, 0, 0, 4, ''), 'A': (15, 13, -3, 1, 9, 'c-muNAPhYJw;*#j|9`=X;K|+m_dguLZOh*K{{WoF_DCr9|9>qQH*z%t*T?^pVcbLiLEs}dgr|Luoq<9B$NzLNPvSqw(iK4Y5<<=c0I{1REd'), 'B': (14, 13, -2, 1, 10, 'c-muNzy}KcgTU)`@(^yo{|}7PoB!{D^B5SS|362_$?o_+1;zt{KdXchDn&Z~zg0r$6aD``7tRxI{r}$<Zr{I;C!!ee0|0qlF;V'), 'C': (14, 13, -2, 1, 10, 'c-muNzz;lkz5jZlQ3}E-`v1s*+vM67Fh};+|0p131L39q|1X2kRsH`z7lH?rlSS}=`eK1p<^c$|^#2n_Zo8LWP+6ZnAHJOrBj6|o0B0>9RR'), 'D': (14, 13, -2, 1, 10, 'c-muNzy}Kc1Htzj-GUHq!2b`7N-O@~5r**?7&u@5??mtzw*5bk#9Q?L5sKV71drqO|8}^Uip&1r5rW(I<7ST#1AYJi<lQe>'), 'E': (13, 13, -2, 1, 9, 'c-muNzzquiLqHCg7x4cBkW4`4Kmi&D1UMK7Dg$v`I*{$@z~dGM01xyeEC'), 'F': (13, 13, -2, 1, 9, 'c-muNzzquiLqH6e7x4cJNDP?+1!x=~_<>yp2M26V2m^iq0Ed|%C;'), 'G': (14, 13, -2, 1, 10, 'c-muNzz@83zx#G=jtPWQ`v0*Dx5BdjV2<ps|It8-?KPN}`v1QyLRa<w|6B+jP)>${;m-g6J|Ldlum6!i>I{U(Q1<_U9lOvKD38H=_lF<1SNpNxcNGBZASE3'), 'H': (15, 13,
-2, 1, 11, 'c-muNzz+)k1A)L6AaMrF5BUE9NKW~`hJh$91Q4khnTu{O9smF}12o('), 'I': (10, 13, -2, 1, 6, 'c-muNzy=Eb1AzdT8SwuDRFDD|l6e>a09S$-vH'), 'J': (11, 16, -3, 1, 6, 'c-muNzyS*W1AzsEt@HoC3<C|ACjb9)gBe#9%Kl$~h&}lK>3}W+P5=NI!XOF'), 'K': (15, 13, -2, 1, 10, 'c-muNzz+)k1A&0g|NlQA{DA)-7#NfeyD}iSjz?4(5ZtVX{0s>0udo06k+>gx{`_x4;xeTE|6hy5WoY{UzXZu%hPnU$pCRBv1^_L<E;j'), 'L': (13, 13, -2, 1, 8, 'c-muNzzqui1AzdH7x4cBLW)Y9IXZBAfItV2TNnV}R~(Z'), 'M': (17, 13, -2, 1, 13, 'c-muNAPgG*|NkEVq$Pj<|Gxt)lJM*QP9RnP>;D{xl7!{||EVyrT-gp6C^-4QhatFk4MHI1|67h-ibw)%FaEb}U_cUJX#D@*1w}yO*EI&X0MH#hAo|3Am^%mn017`jHv'), 'N': (15, 13, -2, 1, 11, 'c-muNzz-_^|6j+*z%b$e{~9nq=Kuc=AXSn8k&gNF|9>J9xBl4wUk(Uvh1mW7Z&eXo2JMgkZ?z$~44!}f|3cz2<o^Gk0JC=nkeUMJ;sXFStSN*'), 'O': (14, 13, -2, 1, 10, 'c-muNzz+fseEfO4n;*id{(s9rsQLeOK@dm&_y1r92FAPpJ3+kE|No_c)bjsVAPWC;0;y^LUx9dOFuAKBp2DC1L12AdU^DCg-_R3m{(n;lVnxWIPrvT;3KDP?0E2=nh5'), 'P': (13, 13, -2, 1, 9, 'c-muNzzqui1HqqrwM<}M!2b`-PT&6*z&H#HC;qQO$b5s#0QEd*U_vN^0h}DLJrNA}0RRONCUp'), 'Q': (14, 15,
-2, 1, 10, 'c-muNzz+fseEfO4n;*id{(s9rsQLeOK@dm&_y1r92FAPpyFk3u|No_c)bjsVAqxL<0;y^LUx0XNFu9W;p2DC1L129iU^8p}-_R3m{(pf7VnxvYkN>aKaUmSgxJenwIZQ3j@(8#X0Izv2Zv'), 'R': (15, 13, -2, 1, 10, 'c-muNzz+)k1Hqri{p?VF!2b`7x=;T%Be)C<i~p}fk^LJ6=K{e!3kHO&(1!nekhlyoKmPk68#VR+bryuZ0zm2iJOo_G002^UFYo'), 'S': (13, 13, -2, 1, 9, 'c-muNzylQ5y?%EnnFGvbys}q<Rdq)SMB@K`X}Btd|NsAAX;Fppb_03;e}_UiY$<zx|Nnm#u9Pq8?^7^C<dp{xoAaM}5MjsF4}aY6=fUR`1^_CwA`}'), 'T': (13, 13, -2, 1, 9, 'c-muNzzy#Fhky$p&KU-VHUH;;X$A&2D8~(|63k&BpK}Fh%Mk{=004&RA5Z'), 'U': (15, 13, -2, 1, 10, 'c-muNzz=5p|Ns951H+B~|4qRBivMRo)E*HA(zzx7FN3Hf0uXN0{|~GT3`{qfAY9>(|2stl>lVUnw%GgW&(rCA3<LoH*~=nU'), 'V': (15, 13, -3, 1, 9, 'c-muNzz;<J0|5tv!vFs@V7~D8|H(kgvkNM}=>HiYxj`AqwfO(vltFF_T>IJo^B7wF;M|n|-^5Na!?|4V{~xMGvTVZtU*bqywSOxZhyVckN*;*'), 'W': (19, 13, -3, 1, 13, 'c-muNAP&g<2Lc|3y8o37694}%0E<ce`|r%aaO(dt1_qOUsJfH?r!a_p`Ttjhp~W65RQ3NcLt@jn|8Wcln4v;i|Non;)!6udmGV5e4Y&Sxo?=M+|FO~^F4X=1TL**4pZ`xe;X*e5|64FH9Q?l?;WVa~&lnjP3jW745Dx$Vr#2!'), 'X': (14, 13, -2, 1, 9,
'c-muNzz073|NlS3<p2L0U>@_)|EE|PdeWhi3LpM=IIo4Pjr{-jq7XvsivLd#Jf7os{v%Y*4>bApKLyGOpT)pX`u~eMm~-O){}2J7o&SCCI*S1Sr#vPT'), 'Y': (14, 13, -3, 1, 9, 'c-muNzz1ah1Azp?mH%tNT<K5$^B5SM=0jx*{(q8UJ0=R{F`xgxx+Vp#)%@@O1B?ihj{k2#GWQ5>-UpzK8yE-x0PtHMEC'), 'Z': (13, 13, -2, 1, 9, 'c-muNzzstFLx3ZgQv)P6{6E4Blg;`6K_14|{r*1!#^$>Ae*xTx+5d0zAdLHE3S-N^|6c*5DndY<PN+R0c-+DO0Aouca{'), 'a': (12, 11, -2, 3, 8, 'c-muNzy&z||NnV28_K>TBXaD&GhD9be;b%)nf&bU|NpbW?8N{3c`E+T0kd=e@8w?wWeXqqa%k@V{|z`TVgLXV102@'), 'b': (12, 14, -2, 0, 8, 'c-muNzy)^v|8E25T*1kn@bX0$3zR)a;Mo5>DBF{v_Wv=s`hx%Wv53Rf1MQmh@MSj(PRB3+0Q|!z@c'), 'c': (11, 11, -2, 3, 7, 'c-muNzyY*&yn8fN48-Dl{y&m;@dOYv^8a%N1_Lm&?Ee**Qm`ll@ICt<DbP9zV#2n!A6N6^G9LgYA{AW'), 'd': (13, 14, -2, 0, 8, 'c-muNzz_EP|8Ifd-N4FmzWi<REhtCy%Rduan4b9m_Zb+TLOB)xFC+BC|9^mx5&iPt46cX4<?@F`xBmZ^!RIOf==CSr'), 'e': (12, 11, -2, 3, 8, 'c-muNzzKABe|X)`0%r2R_^Dj;zYNTd{C|zX;{QD`yX-#*{Nn(zqyOKAYZZL`&y6o*Cxm0P|Ks}&Qn>A5002U98&m'), 'f': (10, 14, -2, 0, 5,
'c-muNzzPJ`eEfd_%xe2TN%1(Cwc&pvL~_CZ|NlQgm|OlQFp$KW0n|GMyPXUG%5)o{'), 'g': (13, 14, -2, 3, 8, 'c-muNzyq8we_MR(|9=?}TlC966Wjm)Ex;1-|L-#}JcV*9{$FNbxB-`WfRGXW^4|=uhr#9Yhefyln<0#U^IsIgxTeFA^nV*%^zXx|f(&>80REmTSO'), 'h': (13, 14, -2, 0, 9, 'c-muNzzr7s|DS;1ZNbCoKmB<FCycY5Z_ED_7$=LN?SD5yPs{%a1UNJP|Nox?#3gtf#sC2JHz;-'), 'i': (9, 14, -2, 0, 5, 'c-muNzycP%(u6RUywOCJneqRB0)(}N1O`yoe-~^P0RWx@6rB'), 'j': (9, 17, -3, 0, 4, 'c-muNzy>xylZ7&#%c085`2Rl!!rDO=W9R<}5OqlO)_+|PW806%1z4Q`08@<`!2'), 'k': (13, 14, -2, 0, 8, 'c-muNzzt^n|DS;1ZNbaA^ZyT=!#pbxE|b2Y2%+rWugAi0PFm6bt&9i*HvKP$S^D1uh+FVDi~#^eJtm3'), 'l': (9, 14, -2, 0, 5, 'c-muNzyve?|4)Fhwor!wH1NL*7K<1Fumcxp'), 'm': (17, 11, -2, 3, 13, 'c-muNAPi>w|KES*`%0ZNU)OU$M7I3j%6I1f9)Vr|<6r`53`_o3F--X13=>FTSn$7uq33@Gkpe(l{#O8T4G`xL;VK3Ic}6ot'), 'n': (13, 11, -2, 3, 9, 'c-muNzzt^n|KET5^9D``Z_EGfd|Upfz&Ke9ZU4JroCJoJ{}TvsfTsOV0pb!oHZlMJY>y%}'), 'o': (12, 11, -2, 3, 8, 'c-muNzzLMrzk0n{4b0?z@ZZAd-%~yiJN*9x28KKT<3Q}P|CbpUF8r@W7w38S&&=rGGk&mU)s1i7Y|+4N4+8**+Z_i'), 'p':
(12, 14, -2, 3, 8, 'c-muNzy)^v|3Bg7i!K&0=gR*%0>}R6LD`-Rwf~Pn*)|LX|L<cFM^-=S;md9oxOx~sVgv2^Z^D2N005J9DCh'), 'q': (13, 14, -2, 3, 8, 'c-muNzyq8we_MR(|9=?}TlC966Wjm)Ex;1-|L-#}JcV*9{$FNbxB-`WfRGXW^4|=uhr#9Yhefww91ysHi*w;W)KXjk0I(P+&;'), 'r': (11, 11, -2, 3, 6, 'c-muNzz$aY|KD)xZwZ*a<^N^bau~A;ree$gL<BPdlR4u*&<F;c004G%6>I'), 's': (11, 11, -2, 3, 7, 'c-muNzz&%DpZ)#+0n7~h-_NFY70fL7|Gd{4qCo!H|NsAYGK1ON(X0ObHv=o^<`KUCPadN7|M%<347dOQFhv?2'), 't': (10, 13, -2, 1, 6, 'c-muNzzQz>cR^?E_zwg)Wsz9t;jBIX<9pM<ET2a|P6%VS3IObM7c>'), 'u': (13, 11, -2, 3, 9, 'c-muNzzuf%|8JA=|9=65cjdng!wSNj^Zy+fHp4ip{uju<g>kg6{MfkV|Nj6yHZlMJEKwk-'), 'v': (13, 11, -3, 3, 7, 'c-muNzzr<^|NkE&@c+LHm>2c`6azy+3`C0a<9~IAgWOPs^ZvK$%!lc6`2VoS3C3Z3@c%Xw+`#7lZ4CGU0PE@&Uj'), 'w': (16, 11, -3, 3, 10, 'c-muNAOvLo|No!E_+l=@f&Wv$0xtirGnoH>!6>;FqJZVye~sqf|IIVwpgI=+uRJ*8fAbb0C_m``z2%PoZ*7B_$o1`i1oNB!IdCgB{N!U;@Lz_32mk=NFeP^'), 'x': (12, 11, -2, 3, 7, 'c-muNzy&`1|9_|C{|_*m>*oJr$!*LK3G+Wc_Nc>DE&P8F##G$#_<sU~$+Sh$_1{N1F#G@i2|ND(|8IlSA_f2|2pf+'),
'y': (13, 14, -3, 3, 7, 'c-muNzzsD1|Nmbg^8ddJnCJ2TJ`+QMKSYZ0?teFiovcuW<^Naf_Q7<C{`|FAA8y97|K||~+WyZ+GX9nbjFpjXy&5j;@$!)_0|5X4<1ZR;'), 'z': (11, 11, -2, 3, 7, 'c-muNzz$OWgFq6P8Nd+!{}vZST=MN7OQ@2q|J&h;FR?*b3ZH%%FnDBunEhZAGH{sB006@47(W'), '0': (12, 13, -2, 1, 8, 'c-muNzzO)~y#0R27{cE6KT7t+2PqI!^Z$PihV}pJLF~ByKNuM1{oev&=l=h~z%cXw5xDr=|64(9Es*+k{~N&O?ED`k^ZcU>m@P2x-H#)txb0^E0HqEl5&'), '1': (12, 13, -2, 1, 8, 'c-muNzzzKG{%?UY^LmcJ*(?k@;A{p8*fIY>Km)h^05zN#)&'), '2': (12, 13, -2, 1, 8, 'c-muNzy%ck|Nr-LqaK9)(}8cn|5sdK_67z9ga7}HVd|XzzvqK8nRk73hB75~?UIKwz0L$OFm$+pm>Pfog8-Oq@*ly*4gipVAoB'), '3': (12, 13, -2, 1, 8, 'c-muNzzKf*|Nr5TErk6@m$TvjXC9c8(*OTDP$qZl|4Xb8rpo{Sw@qP6I3xf3vH~$QmH>&H|J%UquMQl(zyF7V+5ds&pGm`QKLY?)BOhb'), '4': (12, 13, -2, 1, 8, 'c-muNzymaX{f~jMw|$4RedphSvDr?G!P(`x3^2CDVP-hH>OUCVff)o>&!7PkUxC|t03DVfN&'), '5': (12, 13, -2, 1, 8, 'c-muNzzOF32ZAG5*b+!;I-b4Rq61+ESaDbUe<1>sV*UF+97MAmVqjqV`#%EA{_V_N_5Y0+m<=@X^)^G?_A>wg4@e+h'), '6': (12, 13, -2, 1, 8,
'c-muNzzq^F{`mjj0nE()zd}^$Aehbc{J#QBh3fym-ESV(g4tI8|CfnB`X2>iYySVQ!?5!ILJ*ttJD5EOtf=pQsp!N1eqc6x-}4{W((u?100#6Vvj'), '7': (12, 13, -2, 1, 8, 'c-muNzy)~zgFy@u+Yih>03>wpvcMIt&44rY9<#&Q>k8mZ{g+&D_WDXV)8HK+13mx%Ndpy9'), '8': (12, 13, -2, 1, 8, 'c-muNzzMXrzWI7F3c|kiKSSo*KO+#6^Z$PnhP(e0z~X!Vr%QePqyT0sT>St4V<?y@`trY}(6xUdAa?Nop9~Dk{x1WuHUEIb|5tz&`5$}#{Z=D0ZU+DW^O7fe'), '9': (12, 13, -2, 1, 8, 'c-muNzzOtsz5ldT4b0?y_CG-5*F9Dc+v)#*R)(wp!$E8}2)hBq7JT>LPyN^bNnj23=f3RP|Gx%q)`|c2VEUF5Z}k6tj9~VY|9_uO=EZG40|022B$@'), '.': (8, 6, -2, 8, 4, 'c-muNKnIK;|0+W0e+n3q3;<-+1R('), ',': (8, 8, -2, 8, 4, 'c-muNzyPbiLFh}Tz*OS@2r%7L#()I?0Ll~v?f'), '-': (9, 8, -2, 6, 5, 'c-muNzyuNh|Njp`VGsrYO?n4Y'), '/': (9, 14, -2, 1, 4, 'c-muNzy`$rT0<B~ub3c=jdLM1=QlqH!~ZKMgfVYDgl2k~0AX1F6@f6i4nd8(S<HYP002J!4FL'), ':': (8, 10, -2, 4, 4, 'c-muNzyJ$hs)Ffduhki_fkiLXAoMF$Oi2I{=LX6'), '(': (10, 15, -2, 0, 6, 'c-muNzyVD5b3+(0zpEh(xnHNCay|d+psfA><Dsk@|AR5a5bET9orD=2^s5TSG}^(9-EsiiW)sB'), ')': (10, 15, -2, 0, 6,
'c-muNzy_iw3qn}}hwsWknJWMH!sM_2H-fTu{7-|j*8H!>5W5Cbrwr38aOj34)Q&De23!CD*&GwM'), "'": (8, 13, -2, 1, 4, 'c-muNzyNnTu+tO)06-fAEd'), '<': (14, 11, -2, 3, 10, 'c-muNAPm%6SHYP4sYm}mD}%6YmVNuY*qs?Fv*-U>A%qs&<=;Qdbz*|^`O}X5e_D!cX4`54wgLe1ViU6'), '>': (14, 11, -2, 3, 10, 'c-muNzzY_3Y9jIS9{)d;B?#v-InDj>W0ey^o^R3r6Hq3j?ToiSRzu}-AO1g`4cE7*ON)UB008(`6Q='), '&': (15, 13, -2, 1, 11, 'c-muNAOtkGzyJR~2F|_o*PLfHg8TKCD6-;Z|F^LqcvauO|6jwJ^Z$Pfi0AeHsPdKn8`x?>z>?+v7c=l~{=fSmCzxyc`$r_V+_nE#)gXF3_P_abBC!Ae{{@5`2mpwDDmV'), '*': (11, 13, -2, 1, 6, 'c-muNzy)F!Lm5SNzLPyxfSEFrFWuQ<0cJ{0xO{h$DMUeo-(;^<=-S8v0O4;A4*'), '+': (14, 11, -2, 3, 10, 'c-muNAOx0dA&R%>KNy@KRUb|O0JZrKj{'), '!': (9, 13, -2, 1, 5, 'c-muNzyi|$uY@q1|F=LG^8e!@45lAeP(|0opo|k7Xxbe<)I%7KAM3Fh&j0}1Mhl|'), '?': (11, 13, -2, 1, 7, 'c-muNzz!__|NnKT0K$AAtNh}>JDAzWz;NJyF+>S-*zbRq5T?hkbKy{p9v#?>+xt)q3lkFn0I>HIB>'), '=': (14, 9, -2, 5, 10, 'c-muNzzg>L2ZIx&$`J_wiLeg+'), ';': (8, 12, -2, 4, 4, 'c-muNzyJ$hs)Ffduhki_f#(0RV0z^nW)NlbyAI5anZb-jF#x^U2}='), '"': (10,
13, -2, 1, 6, 'c-muNzzXhkc>I^a$)YL%02@^ZRs'), '%': (16, 13, -2, 1, 11, 'c-muNAOysAe?70qz!0|(%J2RueQOtkzzs1dfBkcY9rqcgX2H~Vf#i)(GQsul`Fh^qxW(L$5B%X~X3Plw@3Q<YBa|z8Q?UHMbi;okD1Uw;Ll98@4OHIxFe3vKihkSx0ROZn1p'), 'É': (13, 15, -2, -1, 9, 'c-muNzz<U2s>9hFcWj}og8vYZ1Lg(%{{SQtkU3C*#sL8i27<~!9G4Dcdphtr5df$TCdL'), 'é': (12, 14, -2, 0, 8, 'c-muNzyqXS6vCJ+`(m)E(B1vvbw3N3$^YV~a?SrTFgx=9H3p0S_rUD3{~+*>1H_L0e;ck<@by18zKop^j?w;)?>9){aS8yJ)g9#'), 'æ': (16, 11, -2, 3, 12, 'c-muNAOtx6|NnJVv+2XzY3vaG9TkaVU;gP9{%?Y-$^HL?LFfM~Fq?JK(?9<qKnTQ7{J)<!<NtHG+RXo3IA{O+AHW`Y0?g-L^XdI;oy}iAZdYO;3;<YtEJ^'), 'ø': (12, 13, -2, 2, 8, 'c-muNzz-M|z?8=3*Dt5HXM&i5&;FTN{e8{^V#oZy$58nDe*lPG`u}1><Hi3qAhz%SKV=N}|0jdkOppIL8vlDG0%AvWO?vTmyAIe$EhYk1GXMY&G9c3'), 'å': (12, 14, -2, 0, 8, 'c-muNzzG=Ve_6}~WlKL(dZ+{!{|Xc5`2YXs&1@+9j*Q5$|ITpjHUHbdG|S{?fB*lV4Q40)-_KL=e-4<P`+qP0Dkxj{$d^NN|Nn2m?HB-98Y6H'), 'Ä': (15, 15, -3, -1, 9,
'c-muNAPBOrF`cQ$$z|~T--4`q^ZysD2%g-{fB(Y~+_vn!{|~@<Y>$Lu|Nqy5aU)kVaDDtg8OA;I9|S&fLwMTf*clk~fBa7e^CbR*EL{PVFCpZ50895MNd'), 'Ö': (14, 15, -2, -1, 10, 'c-muNAON=ZslKs7=DoFqaRLu~{CT^ZAHu2rf6G9q`Tuo65J&#^|6m3N#=HMJLA=!e|D}M`^8Z&L3jcEgscHXTfp}>!xvL<a!k_;^V0~R+Gwc7~&=YL_e^UrzMaZE~zwY!35^yj8-&`=F'), 'Ü': (15, 15, -2, -1, 10, 'c-muNAPBOrF`cQ$&Yki9|Nj>Z3^)G&Hv#i2{+|I+dqfyW=a&4x45E$*K)6x=Kd>?|Fx_N=aD_kq?-UWNTL^Q7#okYUo=)c@?0NunCns_'), 'ä': (12, 13, -2, 1, 8, 'c-muNzzOm$GoGo2vhy!9o`teG{{R1ZGaJgjBO`L`zcXA*&Hpwq%`*Af-~az-gV~Ay_w!Wzp95y+{@=^L3d$Bf^5xLn|Nk3sI{*N9d?D)'), 'ö': (12, 13, -2, 1, 8, 'c-muNzzH}WMFc(-gs?f0*h=ePz22+_W^zCHZ(;QBDIbU({{I03!=3+eAa>dR%M1(`{@0?5^E~`#X7ukFKUlNs#y4-aXyCS=0RZe!A{q'), 'ü': (13, 13, -2, 1, 9, 'c-muNzz5Eho4!$pbIRbH9smE^Wc>eM0O4KvZ^N*HFz5V#2Zqfs&Z_?f@^4`r?JGYvZu$Q|0H0F;#cd_N'), 'ß': (13, 14, -2, 0, 9, 'c-muNzylbo?|#2i1m&dsU(QwdKNP}Q_CHyC=Kqxt&X)fP=RTV;!8nP3--<E7Ww!l)YzpV_Z~Fhu1jb=tob`V(l+$s9ujKy(5PQb|{~iDTzh5nc&tU*?4=w!'), '·': (8, 9, -2, 5, 4,
'c-muNzyL??34!Tj4}=(q1^}hr18o'), '–': (10, 8, -2, 6, 6, 'c-muNzy@Oe13?S}82|tUWdyY'), '—': (16, 8, -2, 6, 12, 'c-muNAOvFm!$AxK)d2vp)C#W')}, 'SR15': {' ': (0, 0, 0, 0, 4, ''), 'A': (16, 15, -3, 1, 11, 'c-muNAPVIDH$>r||1%YtYr1FKdrl<&%*c@cu?Q~L0}i&=2NC>)$qWn={;R?HM}UUw{_liw)&GOR3l=E9y8=X3{SSn2S#Jw~D1lE~!CZ;||NnsK|4<q~007(4B*F'), 'B': (15, 15, -2, 1, 11, 'c-muNzz=l(gTUAGVK9LcTNs#CcK$U(a2Xg({?{OLP5)ORxJ=4BU&_L`AhYiJAQ{CV5b>iCSuew~-)tz{|NICpf7tiENUr*Mdx9VXApii$pD$D'), 'C': (15, 15, -2, 1, 11, 'c-muNAP6E3eE4!@whJ?aH}_d6AD8};{~lmo>OW&JeGJ0AeiT`w(ElmOT;>1m$Xr2GSv0*2i4c>;J_SSgQ=WzJ@;F`E#0Zs-Jo@GHg(6mht_J|AJRWi'), 'D': (16, 15, -2, 1, 12, 'c-muNAOv*&1HsS7tDWH@C$=zf=uY@M0f`R;>Hm{Z_>4ENqwpDK{})8zcm7vGlNUhIf9oom`SA!oyKevAUL^PZda~MyffxV)r$sBy'), 'E': (15, 15, -2, 1, 11, 'c-muNzz=l(L%{;5z=<s&(giOU4#3<U25>IeBm-QsSoAVz9KgnfyXpV~Apigsjws{'), 'F': (14, 15, -2, 1, 10, 'c-muNzz1~xL%|6M|HKv$sep$E17O~S2pA7+NCb8{Onq2+V7HVo5Ci}cS0f|'), 'G': (16, 15, -2, 1, 12,
'c-muNAOeK!e*69As$dQ%ckZiLVRp6d|2YtD`ad%;JrByic??Cf(ElkYeC7Y`X!6rQ)SmzU&p-rjoPy9Bp!~G|b|`#?x$lxi*yIu)?t~c;y7&F>mphW!i0}#k>fI#{'), 'H': (17, 15, -2, 1, 13, 'c-muNAPjW=1Azns3y5-n2%XphrWV|RsUb(;KLk)@2C4uSm*NKiuP-rP'), 'I': (10, 15, -2, 1, 6, 'c-muNzy@^w1AzpDePRntl)5ZrJJ10DbPyHY'), 'J': (12, 18, -4, 1, 6, 'c-muNzzrP!13?Ik*Yg1(LlgFU1bgBO2<@_vfnmidDEqm*{<|6oo2}#J(|$HQPG<lBl#Uya'), 'K': (16, 15, -2, 1, 11, 'c-muNAOv*&1Azp?k^leiKt)b$0TTA7G#QZiNqa>Y5PYVtg=`2DPVC=MjcnqHpZ^<C_**9a??T}-O!+^B5t+|0_5WNZWIp5c|I1jA-N!id|NjDlo?!q0Pa!MJ'), 'L': (14, 15, -2, 1, 10, 'c-muNzz1~x1AzpBe_{)=EbVwcb1->ew}8MLyiR5S03-GsEd'), 'M': (19, 15, -2, 1, 15, 'c-muNAPzYE|Nl=P!d&wI{|pH0#Q(KmTJ6t&6{xxs8~*8m=*8<1Lgrsr11Z(>kq9A$u75fV42uFIkc5Oktz=L+$$%`x(EL|xp%<!<!25%T8Bm27YW_Q;3vn7UAcS=O|Nq|tX6*s8I*9Z$0|2WOI2i'), 'N': (17, 15, -2, 1, 13, 'c-muNAPijo|Gz5$q!a%C|6c(SI`e-cBZz(hQ*&m+|1wko#bbZ$Py}S8UObmT5n!<WeSjH7fFb{X2dV(W(tp0F0$i8ge?bvoP=5a(?$ZBLKn(AH3`79{O`k0I'), 'O': (16, 15, -2, 1, 12,
'c-muNAOeK!|M>lCBQK0Q<z=KGhxM^*;t+1)KQj=;{a_1(fBhJQuKBMHq6Gg>f$+WlCx9sB|LqXI&Ho~7@(kCHLipAHRiNgZfGDo}Yhm_3j}TzDJaSP8=AiI{pMG4c=O)H00CC|bE&'), 'P': (14, 15, -2, 1, 10, 'c-muNzz1~xgTT8z7Eu0)EeuR*2fnDnc?=9@|I3hg=14pyRfI}(Q;-0$Jg{3*7zhFY!pJ0b'), 'Q': (16, 17, -2, 1, 12, 'c-muNAOeK!|M>lCBQK0Q<z=KGhxM^*;t+1)KQj=;{a`DEfBhJQuKBM4q6Gg>f$+WlCxR&D|LqXI&HrK$C4`Vq0Mj>*LipAHRls!SKNAqeb$=a1oN?jv2myA>Bj<%-4vN_K{{QtN4rC|$T()FE@q@#jYs7dJ0PuM#Yy'), 'R': (16, 15, -2, 1, 11, 'c-muNAOv*&gTT*gX>gGfTNoI`rvDE@<}>j8pO40$i_90D{@nu32N}3q71=ztgn!v6<})mMFNnfd{nL)ZXITDK9N|6(ApP(E3WA<t0083eE)f'), 'S': (14, 15, -2, 1, 10, 'c-muNzz;%?zyEq9M+m|R_?^Vh<8XfggtvS@h>U>pmOkJ_(&ql}c8NNI>vHJ-|C{A(aK3Ej{{LH%t!eo$0jB3ffXJx-(h%MqCthy58;2okgbR<p`g*fdh=7X$-IgK_'), 'T': (14, 15, -2, 1, 10, 'c-muNzz6R9hk`p`9uEV<o&yXFJXm-j0OBD4^?52Fm#8oh008cy9`O'), 'U': (17, 15, -2, 1, 13, 'c-muNAPju||Ns97NbmUn{|8j)$rLaZGKGPP0*|JFsjx{ffvd~GR7ML-V8ugb5VbS{CgAXIr52}r%_DBOW4#Z4{PSX^3IlNf0EgTobp'), 'V': (17, 15, -3, 1, 11,
'c-muNAPiLg|NnmjNNWIT9<T`G-HTva{y0oc^?x%E)szMkkoq$VNHSgLg&VWw6E_2c=X`{@0soU27}i=N1Xx}iV-UNDY<1^<?UE8?0k!}A7sXIqcj(7jROiP1_hcXz008W)AN&'), 'W': (20, 15, -2, 1, 15, 'c-muNAQrs&|Np-L1H+orK=z6M{}aH1TW$ae=J)?Zfz(Phh{CM@iVO@^SN}%=WzIk~EB?=BU}%hgzKDUrdJ4?M8(SC{j)~8I!N}0!4HN7C${~1yA?&{)!%;4nnA?B%uqFn9Kb7L!;jUr-GI6d21H+Mn@%acRZoYMaiGiW|*EThTSl0igK+@>{T_mq4{*M8YjL)YqkOTm&<257'), 'X': (15, 15, -2, 1, 11, 'c-muNzz-h$|Np;&p#n(Cfceq?TYzLv3rv2+A4>+E11vDE;FCKd$CMG;UH(0bM>cNVe_te??!GH8Md3V-qe=!pH^8}*V;O+<ra*a~%YX#aq0bPrU;O{Sg@IuY&{cB?xSs(4o!}?g'), 'Y': (16, 15, -3, 1, 10, 'c-muNAOv*&|NsAlfk6dGaexI_&OYV?QZ}n$Dhz&4V_;xEE(zDt_Rp4~B^hA^$Bi4NJCMz^{r6fK#gY>{P%S+|5+CHm|1u23008&L9##'), 'Z': (14, 15, -2, 1, 10, 'c-muNzy}2WLqR>5cLhXpUc1hP;LZGLfKVRrzYxKZe!HC!&SBd3QXC;w`Og!<G5b9M!Qs7gfgNP_4KQ!fH%$gO&mQKM8+e_}000bjB=Z'), 'a': (13, 12, -2, 4, 9, 'c-muNzysvwJ$tuP56W4Q%O%wQm<u7x``-$}FyHg;|NsB~5W)9rq!>8<2Y@-o|9u!3_@NyBPn#wAd!QT!*9+e+C;$K7g3o#Y_u(7='), 'b': (14, 15, -2, 1, 10,
'c-muNzy~J$|1W~Xb-~MXIQip-FPyhUU3ltm4H(abfq~=wEErE3NS-_f<4FL?Q%7MuI|c@JgvuQ%LX)AU0Nvts?kC&^oB#kQCnHV'), 'c': (12, 12, -2, 4, 8, 'c-muNzzG<O?|i>f!wY7&eDdYCd{F{o@_g?HlI38w+5beia<l&la5m5P2|%*556o%)<iqXyMhjwQ$-N&JJ#pK~002eE73K'), 'd': (14, 15, -2, 1, 10, 'c-muNAP5fpe}K%bz|Lcz^8Uk=S{SeAlP7P)BPfsSM?a8U1?B1ePXv<nP@ew(1Rz-pSJ?+7m%vT==*|=L3Sq;CPxBi8|JT6pTmTdKBVG'), 'e': (13, 12, -2, 4, 9, 'c-muNzylb|?*F=5!U*9szqICZ`j81`bAK-bl6?=s9JBurzzg9dBJ}fop9~~jE<p|W8p@-8Ef#8Y@!g*{(;4sr0M+~)82'), 'f': (11, 15, -2, 1, 6, 'c-muNzy)$1{P|x3W{LfeVTKCo{MUi9O8x^u47w<pOpswOaJqy60PKeswg'), 'g': (14, 15, -2, 4, 10, 'c-muNzzf)?y#F+}@&A7fFt6v6Cr{9;2M{T)AN@db36!VzKM_dQLV5cC6M$qrTxB1STnXhd^n7&Z348PaZo`KUQyOj~TRLwil+iFjh&$kW7?dZ}d*|z=L<T|t0D&<j%m'), 'h': (14, 15, -2, 1, 10, 'c-muNzz0hH|JOm{>fq&h?*Ded6wceMEOPJ+oEOBvko=no#xr1G2>j23WJ&-Lyp;d{|3}mS2?xARW&i+==ps1'), 'i': (9, 16, -2, 0, 5, 'c-muNzyd<=u|gPO4_FzngOdOMbs#Jqau`7E|4Xo$3jh<V5di'), 'j': (11, 19, -4, 0, 5,
'c-muNzzMvbaKV_~&$t-yfr9`4bzp2AYBKfzt3xcPWv_e33bpI^B}d#&0RV%T6{Y'), 'k': (14, 15, -2, 1, 9, 'c-muNzy~J$|1W~Xbs@kz^8f!41kY)w2tqD$4HrUX``-d2eT_LkO_5Dmbx#0^$9HQTgj4hX|9_t)K*9j8lNkWBEF%E'), 'l': (9, 15, -2, 1, 5, 'c-muNzyuTi{}+L<T&T<dn*2Wki;WBbyZ;iG'), 'm': (18, 12, -2, 4, 14, 'c-muNAO@8D|L=A9+abBY`|oEkL4<VvZ&Z-FdaRe<?oTL8B#?oj=?@PB!}(5_hyhUV3n1&j448-xP~-_|A}Rm>|BqMzBn004|9^of2QvTw?Q|`T'), 'n': (14, 12, -2, 4, 10, 'c-muNzz0hH|M%Sg?Sd(ktMh-evdF<Ra9$7tL-KDX7|(!#A@DyBjHkoE5I_Vk<^TWx5j8-<0k1<C0L8Z+Gy'), 'o': (13, 12, -2, 4, 9, 'c-muNzylbI@BF$~!35znfA-_`{?r9#bAO)zB)fkKfH-FV6M<yZe_IGA0m0z`E9-(NV`%>5!{hm}8)|gPz2EmMnef@p002(n8yE'), 'p': (14, 15, -2, 4, 10, 'c-muNzy~J$|L=M3=M7&d*X92XRpF_>HDEkD1_qAzvtT?4AbIi_j3*5wPaTEvoEaF{5h^#S2~9?r;&Ac@k_{qA)}!!%ZuuX<Ko|f3O<yF9'), 'q': (14, 15, -2, 4, 10, 'c-muNzzf)?y#F+}@&A7fFt6v6Cr{9;2M{T)AN@db36!VzKM_dQLV5cC6M$qrTxB1STnXhd^n7&Z348PaZo`KUQ(*capaM7Vz<-!qZ~_1{#w4E'), 'r': (12, 12, -2, 4, 7, 'c-muNzy(VF|M%Ye<G&7=qw{~C4*zKwI~1-+=f6G@TZa%k<^TWxdl>Km031aVwE'), 's':
(12, 12, -2, 4, 8, 'c-muNzzOV6e0|z32xhW=tl(0++yZ8c{I_Iah=H&fYM!=xaltf*1}=IV2xe()0}?&AA?)8FoN`BYgV~G`$3DMVEsNVu1^_>a7DW'), 't': (10, 14, -2, 2, 6, 'c-muNzzPz6V6Z0q2Z9z{vRGO1aF)k^S)X%Y7VDO8kG!#43IJ+B6Vd'), 'u': (14, 12, -2, 4, 10, 'c-muNzz1gh|G~hp;r|sVHv!0FXd#OC6G(KzctQWU7#P;Vc*=hZxqa`!cnk&4KK8Wz|1X2rAq)WceH+6'), 'v': (14, 12, -3, 4, 8, 'c-muNzz2B#|Nq~?Q1kzP0hr7FrXEOkMnPq}pD;79U1f*zRQ?4pM0UWn?%K()UlGm=`scR|VJyqjPrgXDG(2QxAOrv=;}xp'), 'w': (17, 12, -2, 4, 13, 'c-muNAPkQD|9^ym@p&|Z&j0^Qz#_X=GB8;EU&Fv)J{O`S^$RCM_pvV=3_TtY0g*q!4Ci(K`!Sqng_^Qwx!!Vy3-iq9!;H=N+!4f3{d$5oOhD|<TTTYG|1a3!Ht$;nBrYvtAPxWk&mknB'), 'x': (13, 12, -2, 4, 8, 'c-muNzzr_^|G$Fg|Nk!#Ud?B9hJ<dY6yx@brn^~S3Pm1&kcI1F+VwjQ&S}aj{i+RRyDnp3+<c82%wF^Vzem7-Ac4nv1^`mz8x#'), 'y': (14, 15, -3, 4, 8, 'c-muNzz2B#|Nq~?Q1kzP0hr72t{zBs#z18!Jz-{GyTJkF>HQC2h@1%5dTJ-bL2WoM?VsOKgt5F|J|!U8GVcQy5-)NJ5{F}*9-Q6s|5FnKVE_Qx{~I*'), 'z': (12, 12, -2, 4, 8, 'c-muNzy&n^gMl`fy?}v%_ht`VZq*SM7&HHsG>mES-37)Jd0Y!)GVR>K$iPq#17b%(%#6WlDFXn96c<G'), '0': (14, 15,
-2, 1, 10, 'c-muNzz=lxe|y@*4CRQwp2BPNybH?fc+JYdkn>9v!n?R0NND_zgz&yi1QJ~TYr!1G|D8aR>3;_nIfjetko9%G0-Blq8)~M+n@Kzd&w5~P(L3<{c?&ZE2QvTwA?6}F'), '1': (14, 15, -2, 1, 10, 'c-muNAOM_Sw7}U+4aa{Ycq%2#KU$EL(wg_+KM-UPaxegwzZN$'), '2': (14, 15, -2, 1, 10, 'c-muNzzYnPy#8`F2F81_QkJjee*%>EL;y&fJb|oy#XV%+**QoYv(JhM4*!*KB+h|c1V`p<6oR9F-33UV5P|UC{|5sR{4Qny0NO+w1^'), '3': (14, 15, -2, 1, 10, 'c-muNzzYP*ul;<!R0hiHd0@_=fBPtmmkuQQUn3OrxI8X`a|-@{&POtc%jy0cWP^kMn<Mem{-;40w<Upu&;MWu@6I-L4y)S_xFI~9d3V0wn<dRa0000goE^F'), '4': (14, 15, -2, 1, 10, 'c-muNAOsY?Y(a1scfUpAWlT7N;K`llMB;5TXF%{$TNw~MnL}(yyypK9a0X#2k|}7s7Ldvk0`3I>CWjzT'), '5': (14, 15, -2, 1, 10, 'c-muNzzb~tgFp|A*MTC3kGJE**E@auFy46!Zkv0jn2;1i{C7a&8UBxhFm_mh<s6~BlRBI>_f9iIc=8i(e!JZ*z(4>10DE;Dum'), '6': (14, 15, -2, 1, 10, 'c-muNzz?|E?|(b)3*|8F-=oT1`=0~Ci~lUhz`*zd%G<FCS=-Agy>H%b*M{<bf9VpE+x}Vv!u#=@iGe}ke=dY~>kL>$KZG~qH46iS{QqJIPvuL$kj&N>qEKVZ4}E{OT%Le~8342sBxV'), '7': (14, 15, -2, 1, 10,
'c-muNzzg>L2ZI7APX<T`epQ9=Jh^~G;Z9`bH~f$|P7j%pc&jRrIO3nhka*QgkT^^atdMv<=aG%ylFC3B0004!6Qu'), '8': (14, 15, -2, 1, 10, 'c-muNzz+h>e0e%g49c<nTf?h${ScJb{~Ac7{)bBTLU<w&p2qts9?ffWV5Yb{{QrLuCzO-;C6rrX(-l4l@9AP7A@e^6!h5|4%qxQMrhgCOmRtW-9m3;ixcTkXPHO@VW&i+C+a<L'), '9': (14, 15, -2, 1, 10, 'c-muNzz^cje|_4?3guM%4COI@I19>qy%b2K{gVfCIR3W)Nr(Rl5V>a{xrG095MIsCP;TQ(|C=B@=8~J=&$<53N3uoxzdclC35a;a4COu4<qZGi163qA;mMbS&J2VA08SYsLI'), '.': (9, 6, -2, 10, 5, 'c-muNzyjL-`@$Gr*yI@iWP}5v'), ',': (9, 8, -2, 10, 5, 'c-muNzyehN+d>!~KlmYx&66Os*%}T8tN;MIa|GZ'), '-': (9, 9, -2, 7, 5, 'c-muNzyuNh|NqZmAQJ!p+`t3A'), '/': (10, 16, -2, 1, 5, 'c-muNzyZ7-!dP?qp$z8NHc*z+3nnOQ%5*4$@u>@xW%ZT?%IcX9Gvl5QlwtIV9m;B14wJkd%77C90B>6k1O'), ':': (9, 11, -2, 5, 5, 'c-muNzyj<)20$1Np8^>O0fLGFEk6ba'), '(': (10, 18, -2, 1, 6, 'c-muNzyY+npbYg}icr@1R4BvpCl{2}bs469?M@i$$T}G7=sHYUgbvG}oDAqDGibnVW6<ux;WPjTvk>_'), ')': (10, 18, -2, 1, 6, 'c-muNzzSwd!C02Jg<;Hzt6?ntKjKgp^UpMx;G+&0>-qv1>&AQxS%eORDR7e!wjo@A0RR%|5jy'), "'": (8, 15, -2, 1, 4,
'c-muNzyKXf@Y7TQ0G}rWu>'), '<': (17, 13, -2, 3, 13, 'c-muNARfq+ok!yFCGP!uECa@4@m}%mPJ=RB*6r2X=~l>^-Cw_*W{F}Pi_gk$cj}c<#Q2i-{XLqFW^MU-2J!#^SX34#'), '>': (17, 13, -2, 3, 13, 'c-muNAOa+;@n=O5P?-4g?KCSCAr|iy-|jT3qKNS&ANYF|MIdSa-(v_ZUdzATZGvl&pYZbSbZca5*9NdLPyzsFQx-J'), '&': (17, 15, -2, 1, 13, 'c-muNAPTsi`f??o1HqU7R>f`oF##bE{-2+LVG@#n+5bdTBRKAVvqk0$oK0W#*^WWt|Ns9GZL<$BFfaS+#K3ri6{6zdYz7AA#ot`Rra`rwyUEVLz_j4|MP8^t<o|8@oT~M2{v^Xpb>98*$JH9{jsO2IA;w<-X__or'), '*': (12, 15, -2, 1, 8, 'c-muNzytPJLm8C~ESrt=_6va6sw<BjpLR2u86p$^?<_xrrLqJlekTPiUfBpze?S1;9O?i7G1d}B'), '+': (17, 13, -2, 3, 13, 'c-muNAQJdIpiCg+KNS3-qM-x;03}Tly#'), '!': (10, 15, -2, 1, 6, 'c-muNzz!b0g|W`vfU$NRhOw5dgRv&ggt2N{V61`)Ocny{IRs<vJB-6}1^_lN4M6'), '?': (12, 15, -2, 1, 8, 'c-muNzzOWPy??P*9m4+8!Kb+YF%Ou1myv<N>%To*UD<zKC`+>Z`(~Kvm0OjpaJB%#RAe?1(0`WzXB)gvWWWaia8ndD'), '=': (17, 11, -2, 5, 13, 'c-muNAOd9khk`#0!~!z3kO~08KN7h'), ';': (9, 13, -2, 5, 5, 'c-muNzyd5j1Vb2BA43=j0oDJu5QfJOeh6dpBnWM`h6B460LRG(+5'), '"': (11, 15, -2, 1, 7,
'c-muNzyUgzFzm@8l1Xa-0BqR_Q2'), '%': (18, 15, -2, 1, 14, 'c-muNAPN|r`?QJ=Nc*2;f(S6)tP<SQ!@$6E&j6}K`ad5-)Hw!*zFr0-k?6AwhWB`2B8<1H1oreYo$^PRY;xh#8vdO13{9^eMj=EcpUC<?S91I=2Nzjg$j~>7f#Ez{k>@#PhJK*Pxk#u0*Bw&^hJfeF_TS~9A{~>#<eNt^#QBl|0Hana(*'), 'É': (15, 18, -2, -2, 11, 'c-muNAOfUa5kca~o{_+zPUk-qEPx7}*a9M5@N(e*%-vxC=YmZ#z$J@CFN4MbY+Sgj4iNMx03W(5GX'), 'é': (13, 16, -2, 0, 9, 'c-muNzz^82)gm}`D-dk8Bb-<@FqYl_b+?2O!fAeK&E@nV6U^rRUIrxl9)dY${~>@E!bwEv=lMPvNV;5t8t^rgNB>$Z)ac^7KX0bvcP{`6#vh9'), 'æ': (18, 12, -2, 4, 14, 'c-muNAPUIMd-i3gy3O$)FQ#%sL{{W;3wAvH63MN7X#qkV@BcMGGVGrem}k2C-G3Nx0SWNDTO-B5@qY$FgYkbK1_s6dCxJ|%&w?Nk{?D5wMb_;8Tp=X0398Wf)YoTiY)1RPJ?Y^f&b<r(M71xe'), 'ø': (13, 14, -2, 3, 9, 'c-muNAPAI%!4y;Zy<Zm`cFKV{-Jkt<J$|)-+5EpIFfdFw^^6U~vG||J(3T(iUl+vD_#ahS!w~h~0mNZ>e7Os#@sB82Q|m8Z9<NVR!EA-C?x(&#tYZdq#N-LPhyeg_KOhD'), 'å': (13, 17, -2, -1, 9, 'c-muNzz6iNy~~Ajb_Ph^6NYpABoG`FWynBo-m`Z*^`M*;xm-f+kGT-Cy#K8r4D&tj{{R2)4-tI7Mv8&se*l<c{NIOxfgj4@|Fl_>zX!@;aJ}&Da`ONGE%=-d0Nvyy;s'), 'Ä': (16, 18, -3, -2, 11,
'c-muNAO<X(#c;A5iN9(#!`TXa8uI=dqVUiEnTpIc-LvgIClY^VWXS(m1efap2ixm|2!6t328Id$)!_UiK*M$acfz>p|H0q|3zXjtc3Rc{KnR!hwg89{__P(wmH7Yv4~YH`rSSs*mA)y='), 'Ö': (16, 18, -2, -2, 12, 'c-muNAOf)7i;;Y7jo`CAij{tAgIj&b{*T|UHuA!_Q(i_2a#$a`CJx~y{xbtn+z+-u_}7m?=$ilPAWHE66bRqze*%b7{@)Ja+x#!WCeLvFD1=}AUj=Hu35eplzZPcy^9TWU%Oe+sU=9jD`02;BdTwI84ge}BEHw'), 'Ü': (17, 18, -2, -2, 13, 'c-muNAPy9tVVJfGS)lwJ!>rXfmHYhv|Njq=-tqtc52(<SDPSsO3Ii1d9!&#NVUu72SC@mSj24){iigY~YH0*az~SFYEl&BGN8E77dLR7w=fz4DB0~ZIjtnS%'), 'ä': (13, 15, -2, 1, 9, 'c-muNzynxrCy2eWhjH#FO1yQzrc7?$vv)i7pqv%CTte-Sxe&6v|E(Yl^F8nW|Nrj~5q!T!ih<*Q0GMO^--m&LAIjnXv{{nB2g+e^z3}aF^8f!W_*@A93_KwQ'), 'ö': (13, 15, -2, 1, 9, 'c-muNzz4dvGOU{f<MeH3*fbfND#qeFzwT8qK{(By{dm1Ub%EL3-zNac?w<l6j@kc2AQ|=F7Q#tDaCpGVx**CJnm_sQcz*1L8eMYl_x(yHyp99_V&Nbm'), 'ü': (14, 15, -2, 1, 10, 'c-muNzz>dAu|J4_^G?=qJdVVwZpQx~3=A9oUx9KHfINm4qIf@nL??_F^q-4?VJ(cO{I`(X_a2PLQ1I+yPuu_hGWcB#081hu$^'), 'ß': (14, 15, -2, 1, 10,
'c-muNzz^I{e15%N0m>2kUd+W`eFn;N{4dH-_2j=Sgy-^KB;bo54+ET+_=KAQ!DC<ZI0nIEVDNn2gT!Mn{jUe*nH*wZVE^wA<Na~wuKy$f;!ODeUo`dFm*chsTnqp%Bqqx'), '·': (9, 10, -2, 6, 5, 'c-muNzyea=YC{<5@3a}n1pvN;0{#'), '–': (12, 8, -2, 8, 8, 'c-muNzy%`ygTM_2$^ZbIFa|6'), '—': (19, 8, -2, 8, 15, 'c-muNAPz+QM+OlLv<3i}z73=')}, 'SRIT20': {' ': (0, 0, 0, 0, 5, ''), 'A': (19, 17, -4, 3, 12, 'c-muNAPqGA--#w7`Rx50G@)6Id;iO$h-kj%@B1HwBDArFA>n^3vWV>)UIxSeJCKErmoqT1|9*`m68e%GNM8Og2Nz+z{rmwCeEJ^<7s|QA4x-Bcx4=YrUwMIP_y5~rLM<C1wAlYw5C+@g?`Ql#42!k@{%=$uHb?;Go-a`'), 'B': (16, 17, -2, 3, 12, 'c-muNAPlBl`TzdGt9OUvU;<756BroePybJY@;Cf91(Kov_dxk~|M39H;QwnNT%LdTK~(?$7zp3;|5gTO>D*u4Q03|W-#vKt=R-X=%)b8-3=FK1Umr?A_=o<hgQ%AOJrMr;FH9gR>;Ez^SML8&Fg^Ew8JPC|KLtp#XZ^hdas@-t)&GB<-?;PSKp__qegy!4FFn@'), 'C': (18, 17, -2, 3, 13, 'c-muNAR3rYIdl5#-8<X8pnT!=pUMS*wC?^$h=AbTmj)14k1mAX^gjUA41@oN(M;|CpNA&0=f5eM$c_K9Xd>7Di=&CG{BH|oO;U!?4*wTJ7|b^rp;DFqI(dP7r+tUu`fOI*J%9A{hCC%=g8=|LmL_!'), 'D': (20, 18, -3, 3, 14,
'c-muNAOTFd`v3idXK%01wLlVV`ybE1!0vqbe-A=z^M6AS#j@{z8eHtbA9gTp`TrJ7i0}V32!rY8e*vhN_5T%6)|>y*P*&#uDk$sMUlu59+J9dNL+Sq=n0bf)%R?9${~KXq?>|6j_Uj*Iph9y04?}F7`#%V#%;*0!Aj#@-=#>vtL}Kps|6d;7y7%B<wh)qcnOQlwSr|wL06!Buod'), 'E': (17, 17, -3, 3, 12, 'c-muNAPP*q`v3id2TxxAIRg`E`yUUYT;{<9HvcyQQ9cDQfd_v$Kol1jl+XA7I*_zcg&S)9e-)72Di0UP{QvgBgNGjw)=vBH&%nTa7$I=@zaj$zizh<h{U=5+?FZ${{XYh=>;P22=l={aoihPUNzT0v^2viIAO43D<#Pa70Wj7'), 'F': (18, 17, -3, 3, 12, 'c-muNAQDWy`v3id2M?Zn`0ou9YWp7xrjJU)L^l7|1=Bm=+8+F1K{bc({}~V!gAlR)KL<#%9Yu&_{(lX$>g8&L$h7|sK+>}gA#(V?D3FxbLWsP7iRNUv|NGEHeEv^D;d9Kq{{QYWUj|YD00f^ZJO'), 'G': (19, 17, -2, 3, 14, 'c-muNAOV<9Idl5#?VIcUU;;wxzE%qXX~QF#P!WOKuZ$tAc2lU(#{Yq6=Ggu}jBfOl|GDTwC;pqE3*GxK3#MDo{eLn8B6Q=wJcN<)zZ|M+)qgjbp<YlSm;YNJjDt`UfS}=j3nv2ucjA{12n!t7-Z^#d>gIeY5<&$4x8*NQ'), 'H': (21, 17, -3, 3, 14,
'c-muNAPG#p`v3NP6$XY0m;T>dpa~Og`yUOaYyPJply3g72c}p2w?GI!_{|2UFaP6#i}C%x2Bukl-a{y~{=W)LYyIDV5X}7l_5ldI{ojlboc7-jOt=0IMF<}LuK=dE{MSGTzW)HBAAM(ri^=^z45kJCpG7G2`9Bp*+y7qx6Ox#F{r{agtPG;Ful&D1kBhWW0|3<?KCJ'), 'I': (13, 17, -3, 3, 7, 'c-muNzzb?m{eQZ|48}|SUx$#I^gj^6+5cY!!FltQ3C@=Me+nVt_J1ydQ~bXG!CCO%8NoUCUkuJ>{{8|Xq49q=jLACv%>U<$B=EZ)0Cf`_#s'), 'J': (14, 17, -2, 3, 9, 'c-muNAOvhyegD5P0?uXr_6$i<<NppMUfBOGBwow^7$n}N|9VKg2ftVm9KQdTknQ`w7>SqlKMTrAjAme%`%4na>#ku?c;5z7m3{Bwtx86MUSR+LXa^lO'), 'K': (20, 17, -3, 3, 13, 'c-muNAOTFf`v1;+Wd?@Xe{RhafeE(#j{}lC8<ub&6mI@+$iSd<u@qVJgFhS$PIugqh4}toXUMsvieiWL|Mj!~C!yM#`TzI4zb^$)-SR&Vh-aXP9saMtAo%K^1+v)tk3b^v|3wyrklg>nK$7w3|6+ug&;O|)O8?InS*VEQ-0T1EEKmZnCjP%wPD(HV04Fv$#Q'), 'L': (16, 17, -3, 3, 11, 'c-muNAOcLg`v1<-P$Yr2|8Xb^Hvcz3;XnAzj?Crze-%aA`u}nie&+uwRQvw>pzsg>mqX#d|A4}k`+peX3SJ1`=l@g?<+u;blbn0~|LYq!?mYipPJ~whzw{#r'), 'M': (23, 17, -3, 3, 17,
'c-muNAQ?=%`u{1Ex#a)*m0mFMwtxSnzzplZ{}&;YZ{Gjk4@5Ja-|@c$A^afje-nt#+A!z88(fs{GtZxGKw9{T;;H|VaAE5c43}R4=^6D*Utc54$ehhE|Gzwg;cX6;|9g=fn8%RwKbY~TA4AapeuVI02L_A(?QuZk>;ESqgx?D@aQ;62K$U@E?SB)vs2s?P7yq{c$y<Lp;le&UfW*8<Tnr3ce{aA9CFfp$wpfKBD};e@@}d9lmur(ArU2QFOSb'), 'N': (20, 17, -3, 3, 13, 'c-muNAOW<W{r_K`fkA1}lN)noVS;&g{`Z3Dtw9Kdb8;TNVF%KWR1jh(ZR-C=F);9dVS)=Wec_k>bAW-t_7p;y>O%&GjX+zn<{-p^H#0DJ0d1L{j}U8U1L}Y9hW&^mLTp_Gkf`||{XqmFc1IgXNdCV03?an*odvA=|4xLM`2{fL{=XY0!ZY*Y+vP?;2IJj029f{(as)I~'), 'O': (18, 17, -2, 3, 14, 'c-muNAQrGi?>u+n>Iy5kfZDY?UO?gczhzJX<q!9y!HiY^oWL~miT@A=gZcl>VA|vVZm443|4+g6(*H?N5$^x5!1VS1@=y`2|7XGU=f5mak%IrT!1VjS>`;+Y|82nZzW=%qfsp_EAPnFC3nA`&@m3b9xc+Z7I|EDX^Q)?GU)Zm{b>-%+7<Qt=0RWJ@H3$'), 'P': (17, 17, -3, 3, 12, 'c-muNAPP*o`v3idSNB(2!A08sM=~(zT>t9~6WIJ;2}nl%Uknp?@ESz=|6c~>^ZnlnqUQWhf(lswuV>)XpZb3l6I3Ac|MLfTPS5j1So>cE)g6a_v7idPzlqA1`@aQMz~_G-GM8iK_5XL5`7#g<0OYkTd;'), 'Q': (19, 20, -2, 3, 14,
'c-muNARaLLZ#sA4@<tDYh}5wcQH%^sS-&U1M1&u|)&ev7{>MUv*27rR|1UroI{&XRLM1=`Wd+ln|Lb5zeE81+rg#6hhKlh0e-B|?|1Sp>3i-bo!npij0d7wmgt7R)Cxl_~|2hkVW&U>$n3lNp*#u@!_MZtn3`~A^?pq@~WU~0yjc<3ecu+lV^!u$WdSKN2zifam*6`}{31Q;H6984;JyZ'), 'R': (17, 17, -3, 3, 12, 'c-muNAPP*q`v3idw=XtY!A08s$1pJH-u`V36WIJ;8%QSop8*qi@QoQr#{ZuP<@5bN38J?A_k;>q1J&}GuKd>m(~<fA)q_v}7iz;TnfBj?A@2WFggXxZ7h>T2@PP|1@cubiSptkN_kRzNH2QxOCgAgb5{NqYA7U!U%<KQ}%oAl`$ohZ1kr<x?04J(CcK'), 'S': (14, 17, -2, 3, 10, 'c-muNAOM2)+`swiMjnKd`#+0`fqg+Kg!keYh%9jjb6EZ!K-PBge+d(UXZ`8_MPCG0b<_X<n*|Yk%k%%YA?fA5{$C74M<sx{)BY=isFq|f@90yox$7?JF)(m-{0RaJ8ZNkW?$WL0ri45L03zEbeg'), 'T': (17, 17, -2, 3, 11, 'c-muNAOhI@e|6{9|DSgsef)0$7RV}MV9@%%3&^^{4HlT8z`zjxzZb~bi_q5kKOWVbP5+Hh1@8ahK;iTLyN;^B>i;TKf%N}1r~*^}`=bgR`mcy8@ct7c5>I~S?*HF5mNO6w0K3&DH~'), 'U': (20, 17, -2, 3, 14, 'c-muNAR6$`d+`7KOg<oM%K10TouQ(u{+mG<MN{D_Z~o<iFczl4gt-3Rg0jwAz{Je{uYoXFzH!6EQvcUM7}~et#!dMj0AWO~fr}mbuLNOq)WXHyePe_$c6-BwnEt<nFhoD{!PPzdFAuhLTNlD}ssAtfD(S~v-pr2VW51nm{=DBG%g8_)003IOE_4'), 'V':
(19, 17, -2, 3, 12, 'c-muNAQJSy{(rO`#Av$pW&saGtml6`m}b5l22<w$e>RxTIt14#{O>x55_n;NFzwnuVIbKz6Ul;E|NR&kR9}fA3B~^JVqn-*fb0y#|Hl}dud|>y?a5E>OCG4MUGabEW;73E|Np6qCZrEC9~Cg&;A0>W002+zCqn'), 'W': (23, 17, -2, 3, 17, 'c-muNAQ2=z_<yz&NV9SPiR?q)mIy+`%l~JBsU#3t-v?9f|9=9I<api-Bsrf*!-UoU?*Nin|967OS#ZNyemwvZSH3)9U|_nbjIi{^KTd|Y{*(U&7($mJxn;wDea7?B^Zr{ioYX}U?)V=bG?StDf12YaWS1xWuRpHL;PHRbHVb57i~kRnFfhpdzrPp7p925?X#=TG|6Nf1|6)CeJaGywSoWKO$hiRw<N*M=z&>~'), 'X': (18, 17, -3, 3, 12, 'c-muNAQF^a`2Tb!i{z^RM=D@KO8>6_$(Hqu2vx`aYcu#?<weq${l8i5p&GJDBERom@<BCx>;En^>t_C+iz*O${`ChAWC5K=iqrpxA_)lG^kA_2zY!t8w5^(ff${M#VYo=!29R5O{%1n@5!?P9PGn%{J^%m30uCYr0swvBE>Q'), 'Y': (17, 17, -2, 3, 11, 'c-muNAOh4}{{MWLCxhjR&nN33B8LAjfGE?8Y%nzs{>w2iu$(oAYnu2!i-DoM4`GVK|LqJ)m$?uE%x`}1>~u!9Xu<#0b5Lyd|NmS7MZoR<Y*e?E{Le!bSoGf!Rp9)85hNbp)UCh&ZS7_t761UA5GQp'), 'Z': (16, 17, -2, 3, 11,
'c-muNAPj>4zrJ_##)JR=jUfDnOc1%~|5B*@Dsdo@{Qm|IlrI3py5GL(A{oJR<9`yekxTwBMCPXbzs8Nk)%*Tc8;Q$%^M3-e>gE6EfhhAX2sh*ZWiAjsIRMNx`0+&(NHNO15(D#B{{ML8%Iz0F|KB0Ps|)}Lwk{|'), 'a': (14, 13, -2, 7, 10, 'c-muNAOKvp9lCh!nmUBj@WPydVf|MoFemiC9gw_s0?c8&dk{!+|D6funf|W?k~aS{!Mv#d@jx>Fza>;#H3I|7&VM{$p5(XJ;lYca-GbWYfBVxsk+07)2{;M>(|;m%'), 'b': (14, 18, -2, 2, 10, 'c-muNzzY;-{-2G+)%st8#Ebavi^OaDuZG0i{EG#N_wcIRs?XQlARPYxS62JQy!#{y=Gpw8%*epd@ZTTI%lhvCB$NM#f_XFk3joQw|At`RvAZDh_)Rc}@zWY0>G3}Z;>`bT3=B?h>mU~JHJm?obc-VcApihPdn%{'), 'c': (13, 13, -2, 7, 9, 'c-muNzzYKQ9zJs^5yGDK#E^lZy9&(C{$~axWBfpDmKVDb8m#}9BREn2;}9J8|78dc&yz=H{1&s^AUxe&AKtDq#P1RSgo_qp'), 'd': (15, 18, -2, 2, 10, 'c-muNAO;BbJp0UuEO7BSGLP}wEM%_S|6F9Q^M3~z(|yOGvk(3YLwT*QEEpIzJcIHg|2qN6YdfJv-a8B=x&QV+xF-LrfTYd;cnCKf%*g+51mXIFWSMvV;ec>OKfekMS@i4%%vSH)pXP~teV$3!p8%L+D)#'), 'e': (13, 13, -2, 7, 9, 'c-muNzzh8M?0e9~1Y!5xQ)Wo{9}H$E{WoV|DEaRIVlzG2%fOxcu^cR6`TxSQH5Jkj9Z~;d5Jq|YuRw74o<FhT*6NIf@C^5Uc(=|9ze@mH*c*%'), 'f': (12, 22, -2, 2, 6,
'c-muNzz1TEUfl>~27D6ZodsoITmx63_`ej+4*%~CW%12@@&D=-c_?r58-$6E_Q9C~|0lrNcK;LM?A-sxaQ5s!9B}r@Yj7sh*A;NK+W#szJLJDNoZb9i7S7)Ij)4FG05}jKBL'), 'g': (14, 17, -2, 7, 10, 'c-muNAOK8PA3k>Lh%JPZ@y?ThA@{!-nB(v_5J=AZ%LV40x&$K6-vDzI|Mvh%wqGm3Jh%VFK+^DkC79><zaL1}|Mvp(_}+a=^qP12zcj=Gm#bgaDjj%(WIxl}oe;)c5Mlp67s7j)%Ee%G^CrY@hN|N)-`?sMCFB<d0DqD#xB'), 'h': (14, 18, -2, 2, 10, 'c-muNzzaAg{@;YemHpp=#Pj?gi^MDYZ;ZrS^p6XPcm5uC->Wyt5DxSA0~-?!ZoY-^H2&X~U|?7S<%Rr@29lQ#LU;}TwHO%Ke@}t%)_!MZU@-ch2I1X24J4BOTR@!oXEu<W_>UXRGy0zmBoF-P=g03k0QMFt0R'), 'i': (10, 17, -2, 3, 6, 'c-muNzz%qBZ-BCd-k*RAvY{&rIPu>B%Ix|t3}x+j3X^`e9m){--vwnk|Br#P3jgatS@VCv3_km9sum6x0RaC56Pf'), 'j': (13, 21, -5, 3, 6, 'c-muNAOwz|VuZ7q?muKk$Z&FE*WtGFe=>rX{@(<_nf3=s&(UiLHsj~z2#(7C3Ir$QzbAsz{9g*e+4Ks@(nnhnY?=SLFy=gl=I4A+Hs6Dbhx7?~7XaLh8j1'), 'k': (14, 18, -2, 2, 9, 'c-muNzzeh&{-21%wfvuo#7p~ciNu@yj~9t|-~qBRZ?`ZoWc^;k59UbyZ)ad#kqwn{{~yh<AsVKz<iGX4S#WI&|L;BX4sPnXH`@09OQ0O)?<*J>PCR3W@HGBcGB5=FPlxbA|9dkqFx`BfjNfkz0BJ=hF8'), 'l': (10, 18, -2, 2, 6,
'c-muNzzz!T|Ko--kKTa^epnA>$o+4Evb_F>L0RShHKDA<KUkow3+JH><{yipERFwVP*&)FPbjPLzYLVM?mf(|TOTH=;BXrNinbU<'), 'm': (18, 13, -2, 7, 14, 'c-muNAPUsJKgB=i<4IxB<)8L*L4@9J-{PP8zj?E3)&DTCfXx4UG7L)puZl2O|BnERc>PagVDS4N%D|BPUk@x&`Co&9q3*vd1H<IsY+#Y)-<cU0*1iL>j$DQqeDyStxP6d;f$`HaumJn-xeN?E|E4f7sQj-0ix~dTXJD}WpT@ut^8cU*ab5rb_cbx^'), 'n': (14, 13, -2, 7, 10, 'c-muNzzb?W9OvqL^(Gn0{jg<Qn!(Mt5RUx+XNn9AYoI*e{~$$|4?=j=|8*G{*ndxf@K*d_VPG)&p9bMwI|C$={#$@K?7!y#$%+5C!92tNIY9EjkA8mq&H@08ts$B'), 'o': (14, 13, -2, 7, 10, 'c-muNzz<mSPaV53Ljc0zK72=$f#>uAMlf&29~~f>_TL=D5&5|RL<Rqk1yR2L^FUPYe;*JP_dg6oZT=|&qAdSs0ZGHZ)4_%?9=X8BVEE`TH^c_v*;mh>Eo3F&C<Xu$8y^('), 'p': (16, 17, -4, 7, 10, 'c-muNAOfVly(+fw(=8vkz^hy9LnGdP5r=Z6{;y|cV5t8e0OfoBj{}m)|HGjCivQXSAbBGwfB9EtAbIQ#Bb0ybD3Gv+E9dw#pMk;nStHCglmAaI9oXs$w>|m4K8o`u|KUL4AG(3e<DdBL#YAZaA^`v($tsx'), 'q': (14, 17, -2, 7, 10, 'c-muNAOO5JZNGT$Q~-q2cUOaf!S8<{m=p8Q07y3cR{-;F?E#US-hnxq|7$?hlYL;G$Nw}SDf+(`%yanP1Qv?{^8`M=P4Fte^j{ll+qLg!qZWK)MsmQllSmxSKQoYcrvKBCcq#vP7!&Xe0F;I)3;'), 'r':
(12, 13, -2, 7, 8, 'c-muNzzOo6-DjzLx&y+wc3@>sW;>Y4{`;*ROpVe1O1S#O|4wjr|9=rUd+!s3nXk6OnUeq88Sn!D4&oFD'), 's': (12, 13, -2, 7, 8, 'c-muNzzLY@E}gu6Q3%W~`YO%9yapn^<}D{&P1gU@R&Y+z^Z!e^U>vRq|9ioVd{rRvd@GneJC}h$?{^WH9ew=Lk&6|Kxb0^E076t44F'), 't': (10, 15, -2, 5, 6, 'c-muNzz!JqDnMCTA0ag7%wM0b>;yA;|4oKU+Wb$3va<ghLs_$ab3j=qufR<Ex*W=4`MaAF%Iy92pc{wn0QJulxB'), 'u': (14, 13, -2, 7, 10, 'c-muNzzbS`?FW(t{|&%A{{Itz<ow_4V4ltYL?C(Y3Pfe*e?tZamLJO?ylEgcI{zymyd#%^M9hCr2=Bvc1_sI7|D_?kx7YO(*YA7_wJ+`M>preC?`!b8iU9y=&>?F'), 'v': (13, 13, -2, 7, 9, 'c-muNzzw2re`aD}Q2lTM%q#k@10?q>26HU`CowRHzSjVA*niGoV3^Yk)pg<=gVR-ZD5w9o&@Bs?d13$e_rndB{eO=eVbx=21_A&8pokZ;'), 'w': (18, 13, -2, 7, 13, 'c-muNAO_f7_{R%n9{VQ&rsMwGF)#>!6k}k>c)<b|(f*&$z|i;Khk;>z5kxK1mxT;+hkiCPXy0LnYCm#`VS(-G?F<`2VP;SGZL*PJ+8gsDaNA=4-_&JD{C~v^E~5E=Ap?WX|0M_)F};xo60c+#hz0-?0wwY'), 'x': (14, 13, -3, 7, 9, 'c-muNzz<r#>|tP#f4T_D?f<XAp!`4+%2W6=QS*!eT<yw_r&JI+3;&lRIH?;?JY<G(s+O}x{11n6y7n+Lus%Bp;b{Dy1tjbK&ymCLDga{d8j1'), 'y': (15, 17, -4, 7, 9,
'c-muNAOu`a{g+{2Q2B5g%J=#24<vW2gmOjyH!(2qyfua?zqgfvp=JSG_wwfqGEc?f+=Bm7%W@HBTmJ97z>MH>{Q75uZ1w4d$UKqjVn{ruO@VNBrnA(_R)kdR_s4k*!~p>Bbso9'), 'z': (13, 13, -3, 7, 8, 'c-muNzy~J2y>R0F{}>2oE;EDn_ib=F_KUB?;hetzzHqk7ziDu`@YCyDaL(FahH!TB|1t&!-o;?H_~-wpPF(&`f!8SjRIC|$'), '0': (14, 17, -2, 3, 10, 'c-muNAOHlXoWF3+AIcHFF@u$%?w<jKxAZP61B2-QNnnoZ-%=3uXET^r|6dJAa{b=~<{fwmBIW<j1yL;Dc7iCc|K%V`_WxuMRq@{%L>d0C15sN(v4beR|0O_@=NniX1OLA+Aer}54PyD~djbq5?=zte6PSPH*kNx%eqjIr0e>pn'), '1': (14, 17, -2, 3, 10, 'c-muNAP9^O2f*3lbN>8ShD*%x-1M0dN#(ucNF2U@Gm&^U|Fe;J+5hd3c(eWsAn{H<LgFxe-GanZ|KEnh3;Q1dW6Doid-wm@WyOTN0szpL8s-'), '2': (14, 17, -2, 3, 10, 'c-muNzz@uK-Me;suM?D4Kaq=pb;d7a2ydALkkI{Khos!(e+3dR<G&e#!*p&Jl2plKSp+BUmMTJ7^G+c+M|x*DBb*a-)EJ?q{c~3X2*`nX&;CPz6an7=0EKHI@B'), '3': (15, 17, -3, 3, 10, 'c-muNAP5pKKD&Nvjy#OJJC=z-{>5W%D0d%-nEKxZS;w^hCP+M{tGC!-Y-VBWwO4fEQWIbNT`YmDQ*r-0U1YxM|7FNr-v2uwjJ?bt((!*8g!{yek%7VF#vu-<{TJ?EzI`x*g|OcMBV;1_'), '4': (14, 17, -2, 3, 10,
'c-muNAPhK8|K~&S7Jhq(;1n#sz6H*4IwSF~1IAIfsc7{-8p`21<HC^kUmwa_QOv+F={GxsQ?U$4?7Ifxc%0<|lCM@lco+XeK`Dr5?*ar>|0`X@;TD$tmqT*q@;3y10st+cCl>'), '5': (14, 17, -2, 3, 10, 'c-muNzz;(IgFyg<*SfL+1jHe{t-8o6@30_oL{1<}xxPJr`Tl+{D36twfq`@3|8QjG|MwxQ|9TOL!}D)5m`;uXkrDsnz`XW$CI$xYmus28yn<^_t~}VE$Vk953;^N|BZ~'), '6': (14, 17, -2, 3, 10, 'c-muNAOu`@UB7>+9?GeDWXr%%v>(Dr`mPNmb*F+ke6M?vG!_5XK;rFx5q<F8tF?+?4)d=Y{`?GvAFr{1c;f#TfvCm*^+1%?|4ATf_J30lCHH?0h}!-~7_9N}2_PZxZ5zbQwEvzAEOTG0Laj)?a`xN;1wwuS06!lpxB'), '7': (15, 17, -2, 3, 10, 'c-muNAOu?eL%?JRchigpAejA82EskS1R{5&A?rxr$B4vJc%g*EW87bWtTgW!6B1ALodyz*>1ZXg(z3HGNIb32`ba#M)6K|AYp=2~5C;G!(i>3'), '8': (14, 17, -2, 3, 10, 'c-muNAOP&P-#mM}lNG{o|J%yQ;Pt-_!aMl_D9rqKH<-it`v8y>`o9{&`>_{DhW(F$sGR-Nk=y<08fFO3?8Ud||8}!OIJKXGm>5jHE&_8*AV%-}1y)(}-yTHm_`?LEn*W;sN#++v!78o(PGMwVpY+oXVoJcVi>IzHHzed408o!GBL'), '9': (14, 17, -2, 3, 10,
'c-muNzz>-6&m6h4QWnZv{ZfO0<KT4`Fvs_QDUkH|9|Pvi|E~iiW&ihrdAt7$14+UEOToM)|FwXm;{VBDp8Nkbe2fZ>|EnNoMqc`IZED+pTO>>8y<<jjc;3~3X@MdT*>;Z`%(Fet!@ySdOa-FGXy?Q0w`NK*5CQ;H)G7Y'), '.': (9, 6, -2, 14, 5, 'c-muNzy!S4Z}Ni~d^e#CbN~Ql7XzF'), ',': (9, 9, -2, 14, 5, 'c-muNzyfMNM?x4~|2IJxjH@O<7z!ulz_i^`MFy+@07Q5PO8'), '-': (11, 9, -2, 11, 7, 'c-muNzz!V#1HlI{Q=tI}Dj3KH02F5j#Q'), '/': (13, 17, -3, 3, 6, 'c-muNAOvjAG9oxf+!1WQ{RlSGWpe~4VI6|aeoqs@DVmF5^F5J8a9Vm1Y>B7B2+p(`1Y6}XH-fVwhk-Bv0QUtA!T'), ':': (11, 13, -2, 7, 7, 'c-muNzy)NVoMMJD<(|Ts<bm|BMKES2f{6tH01KQ4Jp'), '(': (12, 22, -2, 2, 7, 'c-muNzzZ0|i(pLAZ7pn2ru4mBm?-<Db#TQke^g;i{!d%r!WsWl;Os5`Rp9Io@8C?C|3~0#%l~uXY`6a{aJJe13OHNre;2}y2lpb_-oMomoT@V-2u@fHUXKC*flwRA'), ')': (12, 22, -3, 2, 7, 'c-muNzylU*BiN>o>=B&QH)3!$*VkHv#Q7@-_TDcD_R0TjaQ1`m2)+Mqz}Y7MSHam?|8wB%HUE|1%0KN!DES9>kKnVZFedAkjVw^6#I_C?lVPSQ0|5X4OQRd$'), "'": (9, 17, -2, 3, 4, 'c-muNzy{L)r$HFS|79VJ`pZzM?k*@}ngatZ0RZ~M2AK'), '<': (18, 16, -2, 4, 14,
'c-muNAQ4ET@%>I$Aafam&aN{;;xmPvU#5-3XO6x&PX)z*S)ZNIjARNpw8j$MUaR$ogP737RA*et;X)G=YpQ3UA^-pgq7Zx'), '>': (18, 16, -2, 4, 14, 'c-muNAPz`lh|J$%g)ZcJV2?eznC;F3&gf#M8xOmqizWUkLgq4h@7-*N#OFvkKUWipFH(1-O#;P$*#$fd)CT|)j1Ye'), '&': (20, 17, -2, 3, 16, 'c-muNAO#3bxNz$BG(Kb@rXx3n806lsMi$fl-wq`AJVO>U{=b-kLGblTWHI&^zb*VOui;0rqwfE|xmpY?3qSr|ZwnEzIktD@|6`mC46N^FK@~;(nZUrZ?f(X5hM4a%5FwV=AAw4E&itRob*~DlOyU1U5G8*9|CJq#P%++LAK1Z;{QW-@ZfXDjc{~hE4oCO>`e6<eV~jlb=+?~*UJNDw->%drA(R08#6j-'), '*': (14, 17, -2, 3, 10, 'c-muNAP9CZhck0b8KyTdScii-j9Y)q?J8gKeGybrddc5kQ$-+b#w|bQbXKi~$wBnlM8FN&wSr+F006T#71s'), '+': (18, 16, -2, 4, 14, 'c-muNARdSdpo>h&p<HCge<+wjZIiLPnKS?Zj0zEx'), '!': (11, 17, -2, 3, 7, 'c-muNzzNd-FNZN({%63Li~eiCnEPMA)!tbNV=?~7f-%MaYr&W%ui#1pS2N%RHt!e1n6@7l<536z|0oej'), '?': (14, 17, -2, 3, 10, 'c-muNAOH%E-oA0WgB`+Qd||`D5cIzT!jo76B0n8NQqBB(JrXbAe>jZEZdmcY87?vJQiTda*$xk63(xT|5C;yvR72t&exX8G3jmyc7QX'), '=': (18, 13, -2, 7, 14, 'c-muNAP(&K4+T>gC<4?nhjah{A72uQ'), ';': (11, 16, -2, 7, 7,
'c-muNzzGgMSA{VTzffVI1UP-14r6-!{RS7#xB_EwuMUE;__jFXGYJ5dz6$F'), '"': (13, 17, -2, 3, 8, 'c-muNzz6LA_c2ue4}x&K|GP4@|Kfvi!oRRHOx_Pwmb{69VSX8ulb6B3uu6wvFaQ9XXALm'), '%': (21, 17, -2, 3, 17, 'c-muNAO)yx+I@bl0EorD#~&&t^rD)9^KA=|#k497rm*%K4+F#H)j-zddbsWbhZq<b-}f^xRL?{hd1Vm;gYkbChQ#&E2*I`c7+5y#W%Az7iDbF*!9xe83Ywo1wAi)v%48-a8TIorT3@{xl>Ubz#3avYGc39UwD4~=T#WyO4FkjLsSFG<|5IRM?0W(j7+C(7F)+mcm4}Kktx5+`_a-s$UYP+?*bMQA-T6JITUkg7H3k6t=Qo@'), 'É': (17, 21, -3, -1, 12, 'c-muNAOXz!KM{rB@Yo%NA2pvJkM5~g|G$6m;K}PhXJ8_2|KmZF%RHFC=Kn?@%BKJ(@Zb*zh~nac^7;N>2a-0ba6_&CuL6==<>3OE|KC1%@bCk|+G+p&85p<^BLoirS7cyd@k9u`|HKHU{h)lg|HmMf9e@h>{GS1)b0&Z($+_1-K6&uu!~amC!VLff&^59'), 'é': (14, 18, -2, 2, 9, 'c-muNAPj`AfAoWMIFId?LrBfbWMm))`0v^Gpo<C0>AR=Qkn%qm!b$pX&cIOe-vP{Fda{>+JNIKbM9T92g=K3hq@lW^{>LC0=<&Y-iO2W+i50h2XDpO!xc9@mbyfr&1pxk^AY='), 'æ': (17, 13, -2, 7, 13,
'c-muNAPRWxJa}<o@$pmFTp;|;w^j^H$FB-8zPJSDNB{Q)D*Erm!1ZlCh|hTc9FRQlmPumsC0USw$^Rw>2JS!4mM)8C0qY3=pUl9Z_J0!Gih%!>3=BH|r^5xrzdiMd+j#x8nV|b34zNhX)91~cS|@%yY~v%!)c_tIE(`'), 'ø': (16, 15, -3, 6, 10, 'c-muNAR2JhaX?utxkvY1owLOU%H=+ENtQwA{bfcdfBJ6~28Jo;|64=2B0o1WFtpbu{f~q2egBs-)O0bF{fFw0`=6LUoq=KNPhkk(>i@BYj11a;r^75h_gRcV?bcy#DA#GvyxYf46|zFPoZSM%`+)%fjs7Q&'), 'å': (14, 18, -2, 2, 10, 'c-muNAOu(zA79G>=S9>p6lB18ktjTtWhd5iVmHKP+o6lsuBk&f4KK_Y7}kGf0&_zD+X2aIC%_!Wy9a?J_urXdp6UNeAZhbI6U>YH9}gt+|64+}RRb;D`Hu(8ll=BNJb3Z5TTt8lZ-1I6^7VNp0iOW?sk|y6'), 'Ä': (19, 20, -4, 0, 12, 'c-muNAPH1G6qk5Vfg)7<Qc~i19YLK<|97H^NIrZ222E&I<KF-BC?cA#`TPC{p$KiPVMzGjiY#LLhL^$c{|;oK<K+wt?7v?liG;r729lTm%fUrhZ$Ezk1fTu~!i93~u!E@b|1B^P-dA2=+Wr4_m{7|`2rc&i6@<aI`1=_@5W`~azyBK*hz(2tLA^CE'), 'Ö': (18, 21, -2, -1, 14, 'c-muNARe^d6_9_Di!9RlR7l}<F#}0}Eqdp<6IWMQ!3ET=-SGkn*Z(bp3MhZLCk<w-`sW0unNR$OFc{4LZwAvI|93+b^ZtJdrkDOtf{Jkee+8zm|Cfh~X#GD6ra%8>fr=FTp9QAh|7C}YoceDAruY5Vg$RWF-v?p%{$B`j=Zm+pP{s9stJxV?VxM1Ch5N#O^{p#6cg3(19S#8ZaXRP'), 'Ü':
(20, 21, -2, -1, 14, 'c-muNAPulzoW+p#Ochn^#zKb7cj_dX#K1rA!T<9!`GBk`=ie-MhKjEGZw6r$O@*tx`IigASeOPA;`)0F$~tcW6Epk22Et(Z#tjoo{a*)RXy1k#H|2i-gb}$0E_Ud@5`@uF3m1F$jS<4w?F|!R`u`Hb5dFvpSNHJ0JlNK4T?o&m{=ev}q#t*AGdq%x{dT_j^L~FUBZ&b80GL`dRR'), 'ä': (14, 17, -2, 3, 10, 'c-muNAOK_@mNInT;(_vHUsN&lKjLK|3|zJyx_IrHI)u~k!kmF&{Z}S1C-lD^ki2#R%wfEH5J+<WoeAcd{;vd*Hvcohyr}>2Kr;WoB~)8A0|U#>e-NigetR7ry!hEIsBQkYKg|>Q`aF|>qX11iC{_'), 'ö': (14, 17, -2, 3, 10, 'c-muNAOQ5AM>8xv%?RZgzE5CSb%~LIAYjcub?m|n0SJft@EuJCp3?^)`eyvm0g`F|%|RTIpBq3_@c&p4<@-MmMCJbX0a0=P!$8#LpCTa2@_!b{0e`214PiWTfseuP(P3_g4Z^dpo<Cd2O2}0Ji>D;?'), 'ü': (14, 17, -2, 3, 10, 'c-muNAOJjGIxrkr3*&izbYVETg@GVw{k0!R7W_8=^Z5Ty0Fv{6vx9jy{}X}axhoKrng0zL7+8KRgYc$-)ad-Lfbfo71`;v<Jt4dgs~H$1Z~vEu@ZMh6Ph7wAE!4iWx3BxS&b+T7;4A>-1}91'), 'ß': (15, 18, -3, 2, 10, 'c-muNAOeIPJAPv(8;qCnS&u>ddp?xM{;3y8-d_midj0odU=aE`9m;L|FUPm!Sgt0NyZ!^i^wTVGbMG8xc(@SG<Nh~|;r?qG7}w%|21DBa2g*=x+J9>XhV=hOq1-9|`GMq`|4_pYJ^+yupF?HeZBBP#5PHxC=GZUz-<Ey<#OZoAf*u6`-F-2)'), '·': (9, 11, -2, 9, 5,
'c-muNzyb{4Y=Sc0ZegGp000Jg1EK'), '–': (16, 9, -3, 11, 10, 'c-muNAOuwY!+{C|%>e)}8wx)'), '—': (23, 9, -3, 11, 18, 'c-muNAPuPeM+XlW1`z-Ne=8C6')}, 'SN15': {' ': (0, 0, 0, 0, 4, ''), 'A': (15, 15, -2, 1, 10, 'c-muNAPATq{ntR^y8V06iNsxgu<;o)oG0)-MdiOYoSXTBpW)aVIQP^lpwLfYC{O#p9|MEn&par%=RX*nhwxZlG=M1U{{~>L-+yfo#rR|*n7jTOMAf7>Y=m470KvH<Nd'), 'B': (14, 15, -2, 1, 10, 'c-muNzzaJ5|NsB(awd%Tg@J)5<$n@_$G~uAGYW4jlFG!tVF*+H|DVE)kYhK$y%Jep=6^*bUe<p#IFHTj_IXCQDZd^}m%#601^}i>D-r'), 'C': (14, 15, -2, 1, 10, 'c-muNzz>*Gj(+-lu}uQZVP5|-PK3+(+zK$S=(hog;>ZN^?ruWTCH%h%iKqNO8>bw@J!E|h#lQ8D%w*p5GFF%qW*-A{+VRg{F11PGcQF9X7aWK'), 'D': (16, 15, -2, 1, 12, 'c-muNAP74C|Nr;l;v_XV{|f^HpUwIoAxL~6SoTE}g|G8J3x&`4btVd*;l*-P`EN5&_`3fyQ25I~3nTcvHtW6zBDwF=C4~F%0sv|5DG&'), 'E': (13, 15, -2, 1, 9, 'c-muNzymt|gFy;}^95OkNDjmR4N47Y!RJZ<dK4gc'), 'F': (13, 15, -2, 1, 9, 'c-muNzymt|gTMhO=L@n7ksPoA9uyexg@GUd01_J+YX'), 'G': (16, 15, -2, 1, 12,
'c-muNAPkt24t@A`bEPAc%e?VbvIM){y#F!~e#vhGFr6d?;osYcqFeZX6$)SZe>RY;`Tzfa3W~f4ln>Jn=a>G{Md34Ve3>A|rcnJq8Rov^!ykX#-5$wCgkJzZQYEb'), 'H': (15, 15, -2, 1, 11, 'c-muNAOJePfT=YXsKEUX0T-xlG9CZ`#8M^#'), 'I': (8, 15, -2, 1, 4, 'c-muNzyKXzXhWj_0NO1ORR'), 'J': (9, 18, -3, 1, 4, 'c-muNzy><L(2CLh5z1J62TU=Uyq^qa9Dh2K7pq$Uu#*+u'), 'K': (15, 15, -2, 1, 10, 'c-muNAOJeP011|5U)>N~_KhEH5VG96UmGJ7^B;Mth0y!s>^&tUqyGHZ%8G2V=Z|$P$QF73T*HEFug}j_%*f90`?Z1@iOUf1Ybi4!_X7ZgP$ez'), 'L': (13, 15, -2, 1, 8, 'c-muNzymtI3^?aM7<k}wB>)iJ6{7'), 'M': (17, 15, -2, 1, 13, 'c-muNAOdv!zXhV0pZ~9c3Vi-)38cI}{)P#>STh|+t(fxzF5vr)oq_+m9YTQRRR}}sJw}88!-UNYM;aNB1Pp&${!>8~V7T<)C<BT>@&9yG0WiQRKmY&${meBS'), 'N': (15, 15, -2, 1, 11, 'c-muNAOJf4?*dU94nVno|2racU+g@A!ZrTykIZFQbD0U5tMMlWnaeQmE-Nxu?q?P<mto?wUC3Oq&wr7*49))!5OO{P0Dd<vbN'), 'O': (16, 15, -2, 1, 12, 'c-muNAPiUvE`0lRI1J9+{ydmlDC>JSlwbPa97Lu6cZKlp?FLh<&(?xz;r|^F@tu#sl=A-q2!Fw6tnv)^cR}^9gYe7#n}Vp+|87wGcRdZ{63qD42Xhc>(Z%myjzlsL0|0Y7CoK'), 'P': (13, 15, -2, 1, 9,
'c-muNzymt||NsAdlQxv|g@Hlk$V(wOhr#530)iv(zYf7MMv_rJ^hy|R+KbJ)2-6Vu5XZp*02V+XY5'), 'Q': (16, 17, -2, 1, 12, 'c-muNAPiUvE`0lRI1J9+{ydmlDC>JSlwbPa97Lu6cZTrq?FLh<&(?rx;r|^F@tu#rl=A-q2!FvRH2FIa`u;8y{S0OQO+i%Ze^;peyPgJe31)ojg*k||=)(8^{}WN%tn_v*BZ`2_pH?Eg$^ZZd>MHC'), 'R': (14, 15, -2, 1, 10, 'c-muNzzaJ5|NsAbzcY;Yg@HkO#Scvck3sf-0Sd1i!IN6?RRv+n{|{yeQ<#nJZ(&5z=kz}eiN|p8A~MhGzb6up;nD&8P6hz~uqSN'), 'S': (14, 15, -2, 1, 10, 'c-muNzzaC4u6}vE#umz3_R5P#%<lj@g!i)@S>?UM0!Tc!m){Te*u%M8UM)xdZ)QbO5dA+FS@+Au5V{FOaQ>JE;r-ZV%AvmYmnnp2H2c=~#~aKT2mk<@mmeS'), 'T': (15, 15, -3, 1, 9, 'c-muNzz=x-!+;4)NaKG9vWh{%#RUM}UKj='), 'U': (15, 15, -2, 1, 11, 'c-muNAON<U0aF*&P@TK^ESS2u8p2)i5KKLr58;;mkpYs5e{&&R;b;4FxbzM`;)gm*aoMXsFBZ!(5Cj11k|Qt'), 'V': (15, 15, -2, 1, 10, 'c-muNzz;TDgU~bHuz@JQ|K=cy<NZXiD9elKAS&X&0Yp{Ldv+kX<2+Qe_Wy7O2B|-JFvCu5XJDxKDGcLg{*h$3z6NfU!1prq|K13zmtUR!j2Xdo`~R~O$ze>7{%bH00RWJpAO`'), 'W': (19, 15, -2, 1, 15,
'c-muNAPyw{mj{wP|KowA$A5E>kmCP1AbINTJRsTrnFXxu;amm=-amDBfy`suAvzb`0qS@y{$GZH>sL8MC<(}EU(0YKhQSqL6a$0O|7eC|`3$pWGqgaBVqkbQi|dyGL(DCP!`orbSbWp@JrjfMf90R$FrnoCb2bC12eV;DF)*n7|5XaI`4`+M28PFA>E!?08Hfh}NIE$$'), 'X': (14, 15, -2, 1, 10, 'c-muNzzcR=We1Wmf9=3L`A_W(4ASp=p^_PYOc-`t<ACxQ_g=~WZ35S+_~m~C!W^cv|IHA*vhU|Eu);VxKZ;bo)<Ze0=MOS56#UYI@LE490JR=D%L3w<|49Z>YTv5yI~f3&z#$s'), 'Y': (15, 15, -3, 1, 9, 'c-muNAOJSr;sQ~7F0+BT5^pB}$+X|bQ0b_DwhXc#o8ijW-r?SHkqyojdwu@5A(ClP|J#ra*Z3boEiNtq0B^4t-v'), 'Z': (14, 15, -2, 1, 10, 'c-muNzy~z`LqP#TjP=-eLj-T?|0Dz__WvvdNB`R?b~s1i&TBb1hjGgv7lgX{{}l+1$KUmgaE{#Dn|uhV5SUx$;B_(s09!mG6#'), 'a': (13, 12, -2, 4, 9, 'c-muNzylio|Nnj^9l_`J`xJ&GJ#_<wmR<Px_y7OrA)K>2b-5XOuRzrQ_XU#2AsmJWYedDm|3f*($G^W@HTMcW+Zg~URvaJ'), 'b': (14, 15, -2, 1, 10, 'c-muNzzde_Aey(o^Un991~A_LRZ>zbUh_kFpLiJ<cs`UsdB;KIk%d@!5S68HQ>3MqzY&1jaQDYCV+H~M0A}eSk^'), 'c': (12, 12, -2, 4, 8, 'c-muNzzxDqetXo)4rXTjE)<up@&GZJUQL0kQ2ZYRXDj^=gtM7mO-2}#{wq&Zy2>5Gi8%Y?K??_NI{`%75_k'), 'd': (14, 15, -2, 1, 10,
'c-muNAPfxtYY^r!Ha!1%It#`t{^-Z+{Q<^%Qx7DnpghU{?m*H3%9BFjp{isk`RL2*{T{|+YI^zeOcsjm*Z=@Efgx-'), 'e': (13, 12, -2, 4, 9, 'c-muNzz4$4{CG2s6T(jZUn#70aXy&M_<SvpwEU|G;wb!21d`0Z0zn+5{}7N1;xN5RMlvk<b+916-Fj&V&;Q8Rcl-VE+71B8?Hr5'), 'f': (10, 15, -2, 1, 5, 'c-muNzz*u3{hI)082z_lga}3afy%A;4+JJ)W(-V>A{GV!0E1u?^#'), 'g': (14, 15, -2, 4, 10, 'c-muNzzdjKUi>_r^<M+REC1lb>-i4Gds_<<g7T#Py8}skIL{48I>1!Et3gu9Q2x$~$Nepg$JF}r=b7UFib$4berJO)bea`;y<bd&3Nu&U{C2&Dje!6F0N@@a3;'), 'h': (14, 15, -2, 1, 10, 'c-muNzzde_Aey(Y>DJeiW-#9W$r8dVAG1Pv_n8<N^#5x@dAopw%zqmsQ^?@q1OR(K9To'), 'i': (8, 15, -2, 1, 4, 'c-muNzyLFjpwhU+Nu^N$02P%DnE'), 'j': (9, 18, -3, 1, 4, 'c-muNzy@X<L1*BRB9Ad|7lanN(hH_tzU~yq>J|WWaT09'), 'k': (13, 15, -2, 1, 9, 'c-muNzyp@-Aetj`<fIskqjqO4CrrlfZ7&l{+4G;}2t6l`Uld0ez_aI;9KtmA^^epMMl&ybWr)v}00)E|x&'), 'l': (8, 15, -2, 1, 4, 'c-muNzyLFj(1u0<0Ek@<^#'), 'm': (19, 12, -2, 4, 15, 'c-muNAQCJ&F!A>HlZH`Of86kf3H|RAkvaA5m=;g>XJM$&Jw^tG)c*zy45I(tph7!=M96<m1_qY@5m2EWU?C1_2oV7QM$;#M'), 'n': (14, 12, -2, 4, 10,
'c-muNzzde_Yr6IIq#2C&f3k$|%Ezow-hCzp2L1n<P~I*eA@kn`%G*I64<`Ts+$<Ra'), 'o': (13, 12, -2, 4, 9, 'c-muNzylZyZ~uDQ%K_o!eT(3Acs3WpdD9If68_18*pmMPfTYTQ4+zH}NUB0O3~#!CL>xpJL*CagUb`oAu^5d50001E8XE'), 'p': (14, 15, -2, 4, 10, 'c-muNzzde_@4WN<r~!=kf0dNfir4&5-X~rL2A&TkP~LG6d1N709z<m++!Sf4<!=PwHr)Mj%ot|F4iww*@NfbEbl4%1'), 'q': (14, 15, -2, 4, 10, 'c-muNzzY}~p8q_Z^<M+REB@%m>-_=7ds7c2s-Qf{|L#E20m_p?;i0NzDEa8i>-`?aV`_T&^9<YuFfbsRhYbJ#MmiyE'), 'r': (11, 12, -2, 4, 6, 'c-muNzyX%*YkT%r2g3Y6TM8!noE5HMKSJ#e;+a?g0Ab_~vj'), 's': (12, 12, -2, 4, 8, 'c-muNzzHl4e0;f50nB86(=Q|#+ze(5{dYyEng3~Cf((pfP`dR;141tA4;zTmU24fKzU(eoh$-^umsji6aofoN0M_di)&'), 't': (10, 14, -2, 2, 6, 'c-muNzzXIZz+lbz4+Jf^WU;cQABM3?UrIq)0-N7MO~C*FUGx)3'), 'u': (14, 12, -2, 4, 10, 'c-muNzzcRP01_tuRmkF*!FbCy0f{&mFZG8rm)%1ckGbpFhy9r_9!>xNsm&PS'), 'v': (13, 12, -2, 4, 9, 'c-muNzzt%4i2_N3|8^h_=Z7L7Ir%n3YQ|*-2DZ1A5RTb@Q--iVQczu&r!(x>0yCoMy~^J}7)SKi*;lM^)7Sp*Wxx*r;{Fy4'), 'w': (16, 12, -2, 4, 12,
'c-muNAO!6G%P}yV{v*i1aJ>=4XZ@VSAoTZDFoVp08?b^c%NRm$PM*P#_?Z>V&ws@@Yl`1phGm-}259})zwgKUTlr-^)Wjz<e)BOLnekr>%3tvNFatyV@24;uqyN`2Fj)Ox#6Sc90F~z^BL'), 'x': (13, 12, -2, 4, 9, 'c-muNzzz6suVG+d+I@i&%+vo?$k6mr6)KnXtLASAT;-Dgli+OL8-I2%!Z<7Ln18N;vU7eIF+~1x0<%qjW&p{lFC_6;&j0{Uz8BU'), 'y': (13, 15, -2, 4, 9, 'c-muNzzxEGNdQTc|5hLl>$4glIrkz&s^JkcgTU7e2uJdlA4C2pUZ}2>+ZnD;gBfA_FXg`;+`x-Jk04A>{~wLu)V*ehvsGSK!r2$TuViB&008Sj8lw'), 'z': (12, 12, -2, 4, 8, 'c-muNzy);vgMkf<&%EV<2#h`By%vmF`O_Z8jQSf1V><k-fH76y&w!g5gJvcs004nU7Y_'), '0': (14, 15, -2, 1, 10, 'c-muNzz@uhe1Fly2IVMx?B_9fG!x33_?Vf2A^xuvgm-lzkdXQx1L1vd0+GM!z#PW^RUqn92NpRreNZ!{q4s_1=h27T$6$8!$ID)J0uE*X01+7?5d'), '1': (14, 15, -2, 1, 10, 'c-muNzzf)dxBfW*=Y_8I*?j<6dIvpuD*wSi1HX$I02SmHng'), '2': (14, 15, -2, 1, 10, 'c-muNzzfu;-~DnSl@ZFjve%F&@@FlSSIG<{<~~JMKKUgQN8sfe1c!OcXH^7m_D@#?r}wu%f>Zw|48h6&8;fM#i~nH2gWtsr08MKgi2'), '3': (14, 15, -2, 1, 10,
'c-muNzzaJ5|NnKTg$p6T;rwa|vVz*5Y)HJyUkDzX&C_-`=g0s58@Lhb*v-zKV@1+u`QH_ZXaC;?!dT`l%42`!D%4E<mCrw4Zxd!9000d*8x{'), '4': (14, 15, -2, 1, 10, 'c-muNAOz$-{#Su>824R5;uTzrM({MgScbrPET<+gAb9onxDh<HU(O5&p38p-*n+Sy1jz>cJgfi!2#OzD'), '5': (14, 15, -2, 1, 10, 'c-muNzzY)ogFp_9_X9-^AMfAmuNSkKp}e468KI<avym0l{u4*y`TRFSk&}QhmimeU_05F}>#ut8;cNyA0|5X4CNLb!'), '6': (14, 15, -2, 1, 10, 'c-muNzz<lfZhbpu596)5V#Th%2+9fhqk^Px(;;MSkLFJQ@MfDfl=tE9d@-4guSFodXCFBj7)1W%LU@O-fXKJK5MC`rE(^jFdOlxFdgD_8s4*Jbzr0$fOu)em0INeHZU'), '7': (14, 15, -2, 1, 10, 'c-muNzzdH22LoFqp)Idi5ghT~y+~5U|Fw~Lmrf#ajQ^)2@g{xaLvUDMFGi9I{O^dw+jy4|!4dsc%Rm?a0Pjc^<N'), '8': (14, 15, -2, 1, 10, 'c-muNzz?F&e|ff44$ATWpU<Oq>Iw^lxA-cM@cOR@;Vl61y#H%Mc&1-LDmTGQN%-;q|49ibC;w|8xBQw%A`srQ89+kte;$PQ1jG~ipAF%4gH?V~gz#9au77*E&5VG9832mqCIA'), '9': (14, 15, -2, 1, 10, 'c-muNzz-5HetS^G2<7Db4Ck?X-U#JAng=BEzw?4Qtp6*3r00Kch}<)<-2XfXukvRYkL?q%3Ls!Ey#C`_(Em&%Tde+DBJpP3f?60*ASPV-%^oVu)%oo6PICrA006-9B5e'), '.': (9, 6, -2, 10, 5, 'c-muNzyebKYoIaE0032s0~Y'), ',': (9, 8,
-2, 10, 5, 'c-muNzyfUk`#>1(|IHwb`cqJ;U11DZ0RYTQ1zi'), '-': (9, 9, -2, 7, 5, 'c-muNzyvP;|Nq~>KqdeH=mZ1u'), '/': (10, 16, -2, 1, 5, 'c-muNzyTs3!C0#%LKz&N9iS}VH_TAhym?Rt^J`xy%kc{blr?EJ%#24-P=@I*ekiML2TbyM1_Mq20I(4b)&'), ':': (9, 12, -2, 4, 5, 'c-muNzyfUk`=Bw10R(jc08KFl9R'), '(': (10, 17, -2, 1, 6, 'c-muNzz&$sq(E5-cUYjTs})d&`F~|7tKt<*!~9b)*7`k|V&$)4ER+ALFy@si7%ToR%nrsgsW@B&0K|I{G5'), ')': (10, 17, -2, 1, 6, 'c-muNzzVunz*xectzgUr>tHOeKSEHJ;J+Z4;QJ~V>tPp$7($)bA7LnK{(2}w=(7!!)wz-Z7XSdeKM^t'), "'": (8, 15, -2, 1, 4, 'c-muNzyK3A;HRkq0J_Ho0R'), '<': (17, 13, -2, 3, 13, 'c-muNARfq+ok!yFCGP!us}9Cv@m}%mS-&Y<*6r1Y`7TUI%H3aonCFZvz`)|O^4qgM6BH}>lJ@<*S%+qA`FRHN006tq7XJ'), '>': (17, 13, -2, 3, 13, 'c-muNAOa+;@n=O5&|LQQ?KCSCA)c6Rzwb1vqKJuRANzL{SwJM~=)Yrd9(VNC-*=nfS~Qn_eLLM6+1j-MYz&kD0L@hw3;'), '&': (16, 15, -2, 1, 12, 'c-muNAPhJrJ$ti62Ep%qX2ca$kKi9(f~vmfjWh~B=l@kvByQMu*K?Od7#Q{}g7EK7WDvP>QJDEn3dFYmX$%Y!x6bFh=Yz;UTL>g%AN<dQ>QDSvCm|g6_|G9OsDR6Xci&DV>%88{PS`I1M|CHx'), '*': (12, 15, -2, 1, 8,
'c-muNzysFkKp8%ZW!LD&tcP$+RzEvY$^~a1FM+VVmjKnouE)?zeE<M)&kd*'), '+': (17, 13, -2, 3, 13, 'c-muNAQFVUpiCg+KNS3-qM-x;09_3eJp'), '!': (10, 15, -2, 1, 6, 'c-muNzz+5tAda<bAB?qjBaAg?F#{fe%@lM103pr{{r'), '?': (12, 15, -2, 1, 8, 'c-muNzzM9jy?MP*5W?Q*!eR7mIYMs9LpW3Z?OYgB>h>XS82j)kE*O*ZZxmd$#Qy-SmZ|)Yz{<u30C&d{dH'), '=': (17, 11, -2, 5, 13, 'c-muNAOd9khk`#0!~!z3kO~08KN7h'), ';': (9, 14, -2, 4, 5, 'c-muNzyfUk`=Bw10dU3c|IHwb`cqJ;U18X@008`A2x|'), '"': (11, 15, -2, 1, 7, 'c-muNzyT&~U^r1iB$L(v0JzBs@c'), '%': (18, 15, -2, 1, 14, 'c-muNAPN|r`?QJ=NJm^?h6pg;tQ0!f!@$7*)Eufr`ad5-^f?BGX;T@HMb0vqKjDXoFy5*Z*wf2$Aq-)%$%RjA_)E4kG`)Tpg%Fi{t>pV$$^N?>Tx3%vL*Fb0hI4R5L04EA`hg<nBcTGkk8Bti0zkUtp&}DzgUF6Ik79`PB?ABiQ7eW'), 'É': (13, 18, -2, -2, 9, 'c-muNzz<|!I>OmZ2h*^s>G%%@DG<&VWEmnk5Cb$QHJ}BbPXJZbBIf'), 'é': (13, 16, -2, 0, 9, 'c-muNAOI$u<$$y8U&+JSymwr%YY02@<IOZq2s`<IrLfk;`CvBV^R+<I@~<L@qwqfwNHYHl1aXx9LqINw!}KZ{$*|<t!GipD>!l$)|07@D?f1v)TmU^&AZ7'), 'æ': (19, 12, -2, 4, 15,
'c-muNAQCkE|Nr}5kM8m}KQH<tM7jMw{l9F&pZC`sN$J%8x<GQ<1_)1f;p5-`|33sVYwkjX&hFIZW@z~j1|J~i{PzWtD;_W+8S`+Bs9^4b#S7Hgm2=x5LMDg5yy#|QuDbo>cE2RCE@uD$;pi|#'), 'ø': (13, 14, -2, 3, 9, 'c-muNAPD4TAavfXpZ7YixP#f*Un6*3|L%oIyy|6O+PL$d0*Ec~KZs${Ou7HwAdbv`_rmQgs{g@y7~k$X&&v?^7h+oH|4eSXC$qq8g&WPcem?DH2XllC2)l>@0P<5IbN'), 'å': (13, 17, -2, -1, 9, 'c-muNzy~A_f0_j6^j7g7w1smj_zu{>l^yv!8LR$=|Np;VNk{Ox{XT^uNl)DXp=B37{{8>|c?jq1PF-$>-YXFG|9yevaR`Uu!5UGq?*CAZ@$v8PR?WSF*ZBYrLL~$'), 'Ä': (15, 18, -2, -2, 10, 'c-muNAOv{+7a08a!No-fOppF+AaULPz34>ZE<f1#j2X@o_@1Kj-y6=&{K3y~Yz>@yY86oEr!bVK{ojv)LGWiDl-u(k49-J%EH4^Bl=XiDFxT(DHi%+;G7-#Oe+{B)(i=8Hegy#gi77P'), 'Ö': (16, 18, -2, -2, 12, 'c-muNAOg7jx5)S}f}4*9SPCwD`*b)A&fWezm|H08dpDF{`rjNxrT=$@@bB#gQ>@R{f@$IZ9T4%IkHM7k{{jeq!Dp=U4EJ|I^{<2Q%l?~!sMP;%Q2Td14dfEc_|^w=5NpxJ?_Z8Y6613Q00g@&82'), 'Ü': (15, 18, -2, -2, 11, 'c-muNAPCl6V7RabCl>{5IRmC(@>Jw*J`1KUu7+?|JOoqE=0mt;e`J89;@?~dSNPdJ9WK4YkNBa^Qe5`x&x^&fguMy?C;=%T'), 'ä': (13, 15, -2, 1, 9,
'c-muNzz43ZVEEC3m4gf#{{R1eB^|-%_WKluBt3NlgqB_S`1k++=OLW4J9W7kdapp#|Mvxw#~~bs2Wv#dy8lBt#>c<ETQ&CzUPl4|%Yq^h'), 'ö': (13, 15, -2, 1, 9, 'c-muNzz3$hVAyd4D+d`c7T*5#w3h?I$@><;>+ozYg!85wNF@A|1+gXn2LMTx{~i#IKaf;~a2Vcn0f{(>GKRdbVZ3%v=3+4#2LJ$}k01*'), 'ü': (14, 15, -2, 1, 10, 'c-muNzz<q}Fs!(OgNFikEC3QF|5eE1nZbC=HUWt^7%%mQGnd^%7>~K@*@yj^Fdj|-0F?tC(E'), 'ß': (13, 15, -2, 1, 9, 'c-muNzy~5Oe0|W!3}HL|OXAjlln3GTpJ!kYUbhdzS+a-0>~+5*oU?g8Oh1sb{Wv><WBuup8Jxo)zy41EoWsDdcL$uqsC=^z$|?B&_vuV-e2xSFh~^}g'), '·': (9, 10, -2, 6, 5, 'c-muNzyebKYoIa6006|t0~Y'), '–': (12, 9, -2, 7, 8, 'c-muNzy)0XgTN66>Hz@R=mrD'), '—': (19, 9, -2, 7, 15, 'c-muNAP%_vM+Pno0{{SsnGJj')}, 'SN12': {' ': (0, 0, 0, 0, 3, ''), 'A': (13, 13, -2, 1, 8, 'c-muNzzYt%XNR*DzTXIibLuu!Zh>>|L@NCjhq7(H@i3e&gmPxDW?(3}0AX`}{0{>9U{2&KHXymH7tGnw1tNoAu;6nE0K7;T_y'), 'B': (12, 13, -2, 1, 8, 'c-muNzzMGW|Nr%%E|eX^z&rUOoXueN3(n@5co44s|65DAI7iq=X}EfZ=MgYAd+;B9nEIdB5^&qk001E|9s2'), 'C': (12, 13, -2, 1, 8,
'c-muNzzu>=e0#oH9n4Jom?SP5I2pv`e4heWVe_9C&i4PpfK{CHeKJBK{e6Nc)EowekdxnDtWw8qKL8Um6Rr'), 'D': (13, 13, -2, 1, 9, 'c-muNzyq%Q|M&4k9y62^!yp-SZxx)wz+mv#6v1J*RfNPj(2T^nU5Kp57{-wZy0;u=&;L&+a+&ctg#iGNI~>O'), 'E': (12, 13, -2, 1, 8, 'c-muNzzMGW2ZAk7b_|j@E;dMg2Z`!0;I^Lu07=^yod'), 'F': (11, 13, -2, 1, 7, 'c-muNzyYrO2LclaGX^1woe5NWg@H)5F${PB0K|L|`T'), 'G': (13, 13, -2, 1, 9, 'c-muNzy|`4etmn;AHq)mkRruzyIvf`=6s)oP-OF;7r_bm0wm7-{~v%Pb0+|zCjr4>NPm|k$!YlpYIfkUukTN!vf^_J0DjpTVg'), 'H': (13, 13, -2, 1, 9, 'c-muNzyq$t0Evhjq;dX(zzy;ZzySb-Xc?#'), 'I': (8, 13, -2, 1, 4, 'c-muNzyMcbs6(Rw05iG@u>'), 'J': (9, 15, -3, 1, 4, 'c-muNzy_|wP=|5P7fdnQ{#F1p=0DBHY99jtjo}UW'), 'K': (13, 13, -2, 1, 8, 'c-muNzyq$tFfh1%2!wNdK6t}rg5JBpm92kohtTus2s?t4d14DI!Zd-iYgrIR3tw8!jIc-S+CnCLZUF!)2^e1'), 'L': (11, 13, -2, 1, 7, 'c-muNzyYqr(1`gT2o~V76#$1O4)F'), 'M': (14, 13, -2, 1, 10, 'c-muNzzeSYQv{Mn{~JJfR~s1^)NlWQ^2+WrGIUnMcp(RznV-nOdGSkpb}+zs+%I>BA$SaP-?Ag|KmaQbCjbEBQz8`'), 'N': (13, 13, -2, 1, 9,
'c-muNzyq#)5@ukCI0NOp?Ly+ze3C$LLKaR!;wXKVMQ|8q&PL+MeyK)q7$&_%;z)cwgU=}p02FB+Tm'), 'O': (13, 13, -2, 1, 9, 'c-muNzz3o){&+c42*S>KAHlD={Tw@p&G|kFNOC<-195Er^Ma_Et3hPI7qH@n{UFj7S%&iiL{B<cLGJr-evR!HIUr`oUHbWIwlH3&000tT8)*'), 'P': (11, 13, -2, 1, 7, 'c-muNzyYrO|NnZa5QG`SAb)BmjLA@b0wFpJruNMWVYmXA351wf0092;6@m'), 'Q': (13, 15, -2, 1, 9, 'c-muNzz3o){&+b{7{bnaAHlD={UQg5&G|kFNOC>T0C8;o^Ma_Et3hPI7qH@neaJG)!FoPG^dx{4<h&2(*VulN9b$IurC<NI@geLjd(4mEFrS`>*O35B0UlW'), 'R': (12, 13, -2, 1, 8, 'c-muNzzMGW|NnZWD3l$;AbV^soXt>v3eJ`}J{7M1{{c>zIHUO+4}|){D~xb9_gh~$o1ys#ZU+DWsYn{#'), 'S': (12, 13, -2, 1, 8, 'c-muNzzIwbe7e`l17@<ns^ym{ivzPY{<FiCaK7kMXM}Mymc4pAOBgPvvTp;ztdJLAN^`L(m-5~%U^Y|a@vqO9NZ_`g0RUh@6%q'), 'T': (13, 13, -3, 1, 7, 'c-muNzzsP5LqH5n;EfBCEDbr>007t+5Z('), 'U': (13, 13, -2, 1, 9, 'c-muNzyrS60Ev=4<a6FT0*T7)5YB~UATeh;gj051pUdNm9fZSDfA`zvC<eR$0AJM?Dg'), 'V': (13, 13, -2, 1, 8, 'c-muNzzudbfk^)sEFdcKJ|mD^(+ig2{AkC(AoxQcqHgva28Q$tP)#-;IT?-?!i=~Rq4Y}}#;My@zXfi%!mlTx2&)dfXJ^0<05W(L3I'), 'W': (16, 13, -2, 1,
12, 'c-muNAOtG60g2mSA_By>{>aQA@!$oJ_%8+GvwbsW2%CQpNZf&F*k8ynC8-ri%!BY7)-zmG^#Bs_5WdrE!DkG7F9rW9Lin7&%2zWmoG*V2v+>x=JO+lzFPFmj?f;D!7{dOiGY|m)XPYHu'), 'X': (12, 13, -2, 1, 8, 'c-muNzy)|7hA}YkJqiMIJYEVj%v}zZS-iyag)o#Y{PKMuT+90RyfCKkiyc#;Ou=V?lJ9JwT9+~~q}*T!G5wwk0m;3sI32(M0GjX>p#'), 'Y': (13, 13, -3, 1, 7, 'c-muNzyr2S1`-Z$CBYo&cQy>1cM_mdNjEuqw!;<f-0)rw&XN0>k7ULh7t%S{000_e5Ly'), 'Z': (12, 13, -2, 1, 8, 'c-muNzy(77gF!c3An>CGjH&i97{=te+6h;&avw8{S@c*G#<crt4r5Ba$bc&@hM2zrrvn%OLn{~E'), 'a': (11, 11, -2, 3, 7, 'c-muNzyZ$u|8dd?#^KDo%?y{hrw*nvZ~grL-vPu@e{aUYaNh;QG<u`PQ}Q3oWa#<uZ2A=!T;>A+gkTgM'), 'b': (12, 14, -2, 0, 8, 'c-muNzzJUH5W%jv{%$54lzm=N;d~909mK#8a23inW?(RQk45~fg8bP!D7*5;``PTc-NFC>9zhsI'), 'c': (11, 11, -2, 3, 7, 'c-muNzyYLIzP{rFW-*<fE3VWJW*UBEhspb0fh$E4Wdy2Kgs5eZUi<czH!kBD06~%shX'), 'd': (12, 14, -2, 0, 8, 'c-muNzzcdh@Uyi}e%!VQ!e+kN#25Sr!Zv%&%)qb(!VWkOB&I;cUm?VqZ#VD-K-DwooPwK!9RL6eTNp('), 'e': (11, 11, -2, 3, 7,
'c-muNzyZWpy?s~+W-%U{EU0nI8^qLq&&<G(wE)EQ`~T<fzyEtdOv9&)FkMW?`@}?&vLPlcdHHgV2rlyh??M!Y'), 'f': (9, 14, -2, 0, 4, 'c-muNzycIc|0w}8`lc{LMAoK2=pFz6|JMPtHb6y4W1s;56gdv;'), 'g': (12, 14, -2, 3, 8, 'c-muNzzK9tecZOF1I%Q;UC-zL8^Shw#mvC43BnFI4<sf-*yc#$EO+Yp{GjR?^iO}>wz3If?ygh_oo>UM@J$-RR@wLYqALR)003HQ8!r'), 'h': (12, 14, -2, 0, 8, 'c-muNzzJUH5Wz0F`e_9_l)X<@>S{8S?ZCj$+K*6QGlO_GRsaB&such'), 'i': (7, 13, -2, 1, 3, 'c-muNKm!j<u<(edkN^O5<_Mt'), 'j': (8, 16, -3, 1, 3, 'c-muNzyuFWu=7c!AM1fB`ENoX%HmT47P|o5&kTb'), 'k': (11, 14, -2, 0, 7, 'c-muNzyV(95N4V`c7rmVo>)Ugs~#D`6ug`aSL<}G60S}1Rx#WJnLGKo8~^~CNfd1'), 'l': (7, 14, -2, 0, 3, 'c-muNKm!j<s6inC02Cw&$p'), 'm': (16, 11, -2, 3, 12, 'c-muNAP8PGUi&&n_vE*2d{F*gNwqiE4FnIBLir913>)eh7z!3c`8o^?D{>eZGS-mC#|r?EG8_5'), 'n': (12, 11, -2, 3, 8, 'c-muNzzJTIT>Z3y9m?J(D|Iy)%64F2Xzhoxbr=|GW)RQD3IO%65yS'), 'o': (11, 11, -2, 3, 7, 'c-muNzyVZtf4Uw9W-(vu;`jJs2x6MPXJufR*8^huUj`C2%h5!cuXpmhe>DQ@Q``IbMkFrd831qx60i'), 'p': (12, 14, -2, 3, 8,
'c-muNzzJSdTz@x{4az>RsBpdp$_`>+2)GJm8#6E%yvHJbRzd!39h6;p<Na)QC|d`~d>m}7000Be7)1'), 'q': (12, 14, -2, 3, 8, 'c-muNzzMWYe%!XG1I%Q;*~Az82f{Xc&CI~C1;P$E4<x2Q#a|)BnQu4n1whp^=$wL^0|q@rurUAt@Y)zf'), 'r': (9, 11, -2, 3, 5, 'c-muNzye;BUU>sy9FvENc)+A|VGJFd3^V`$QRND3'), 's': (10, 11, -2, 3, 6, 'c-muNzzP~(yq&=bVi-SD<xh13vGndsz+~eN9<AYmvU%3DgDAgpDS@>UK`hSJrytgdU^f;3H?$8A'), 't': (9, 13, -2, 1, 5, 'c-muNzyh9_pfT3`|NlP+yA*=)2*x;*$OvHsJ^7b|&3ph>Mh<c'), 'u': (12, 11, -2, 3, 8, 'c-muNzzP0HFfdGLA)ft3fq`KOlzqI3%l#XaZF=S7`o%4{?O^}_Od=7%'), 'v': (11, 11, -2, 3, 7, 'c-muNzz!<b0Evl{Kuq~>d<@LbEx^J@;uu`-LR4gJXPDm%VTyj2`Jf5axPA9|m>IGEOBrwi0J`N5X8'), 'w': (14, 11, -2, 3, 10, 'c-muNzy}gHGcep)#lY~`0K`-Jz$E$bDTC5`Ca~mVqlj6jG!i#KlrAZn7TuM;pcukS-E>*Td)a*x2v6<v9R|L4pO~ShKA+FPaArFL0RR9z7aGI'), 'x': (11, 11, -2, 3, 7, 'c-muNzz&q(88Jw{asabauXF9_fr@Xse2E>(^!=X-W%1md^Hd1JoV$u))+#W|A1K6gCmM(O3;_4R5U>'), 'y': (11, 14, -2, 3, 7,
'c-muNzz#~*1Bs~<Kuoc(A`I+rjlsej@)^ReLR9#jXV_K&VY0mN{3Qd`*!^lR%nZ%{@i3;rR~{&fdEsm*i|7AU83x<{08!x+lm'), 'z': (10, 11, -2, 3, 6, 'c-muNzy>1z1HlO>hvRe_l(lp!lu>?w1;X&YD*|C?Jky8D)gbFd0|1Sw5QG'), '0': (12, 13, -2, 1, 8, 'c-muNzzKL)e0`b;WzXI(;qciO%w+vy$G|XW4w$X_pO1kd=Qx;c_@9x1A@&M}IO|u0dWJa&a~OD6etVY5fCm5oP5Kwa'), '1': (12, 13, -2, 1, 8, 'c-muNzzH_||33r4n?iMV%YPu~z->PR0KcaYg8'), '2': (12, 13, -2, 1, 8, 'c-muNzzG6Re!1ueVe+pt<%#>Df{?ov4rfaK)`l_J_RfScS=Mc4g)*5}?qY{BnHKHmgsD*Y4*~_a?PmZ0mX;Gh'), '3': (12, 13, -2, 1, 8, 'c-muNzzK|ZeZHLvWzTTncKmFEkUNkAV=>#j(uOjp{Qp-0SHWU@F9D&xZ$6k3p03Ja{U`+@7JKE}jS>bt007(W6KV'), '4': (12, 13, -2, 1, 8, 'c-muNzysvJ?0~bk?1QtzR#m{*{I_J_>=`8tFt*tx7C1ZOKM4GQ8&rWX6NQZl0CwLMjs'), '5': (12, 13, -2, 1, 8, 'c-muNzzMee|Ns93jGcfaj?Dh>?Sem?$CLQe2qCwz5sBRZri5py^2GfxhKR*q`*Oyg0S^EGVAT{U'), '6': (12, 13, -2, 1, 8, 'c-muNzzyPVewxJzVfs9A;*NKNu+PQARj~gnfAM-62bit&|FD$e#bz*D^1nX=L-HAjqSrun$|(rD>xh)%r8=nQS)X1`V8>%W08ecgW&'), '7': (12, 13, -2, 1, 8,
'c-muNzy(<TgTMqhpZkj~oSkqNp>BU2oT>0f0nV=5hfs1S9?rD=%nfJHna_Y1004?h4{r'), '8': (12, 13, -2, 1, 8, 'c-muNzzI}$e}3M>1YsYW$EW!)6~g{#$G|Xq0))L}4zK!M7YJMC#{d75AWYWVwLFT)>mbJb=V4&TIRa+0zpLh!KQ;xT$nM0~*9-Y^+s^<11cn+`'), '9': (12, 13, -2, 1, 8, 'c-muNzzNj%ez_Y4VY1xl<8%I^3ubHo<78l1-3w;x{spmjgW0V2yLlbI9))NyIQs46oRtW(4irJ?T0P;aXWURVXTI&$WWWOexP2Im'), '.': (8, 6, -2, 8, 4, 'c-muNzyLd1P-zqZ06gFVc>'), ',': (8, 7, -2, 8, 4, 'c-muNzyLFrK<KSmV2b%VJEj^20AI=jJp'), '-': (8, 8, -2, 6, 4, 'c-muNKnEHB{~ur=8UO%`*8?X'), '/': (9, 14, -2, 1, 4, 'c-muNzy@R<K^a-opo|?J5Sr%=JA@Ik1}d{C4ni}(6oxSD4nbvlN}!CJY7E!`0Dl4r`~'), ':': (8, 10, -2, 4, 4, 'c-muNzyLFrpwcAC0|3Y{1n~'), '(': (9, 15, -2, 0, 5, 'c-muNzy|6oAhh6fUI-(1F;r$-GL-Sy7RvZ+0A)OaiEM$X$yx+u@IU2&vg#_ZS_l9fz6+r'), ')': (9, 15, -2, 0, 5, 'c-muNzyglzK^Z|Cp$xXSGEmm`WGJI=5|q)f2weoGhV88^gb}z2DsxPq0V@Ci7vu}3'), "'": (7, 13, -2, 1, 3, 'c-muNKm#{4uux<H0LbG50R'), '<': (14, 11, -2, 3, 10, 'c-muNAP5*OC#;3BO?&Pi%$0($b8hd?mVm3uxxFt-0!f!y@BITgl1QdlO<c=B3IG6%Pz}%'), '>': (14, 11,
-2, 3, 10, 'c-muNzzdd4v1LT?#54CkoM4G0Aez4WZV7^yw(D*wgejJ>=g~wfn93zn?U)!y1ptwY4bK'), '&': (13, 13, -2, 1, 9, 'c-muNzz1@lJu85*6~CJaP7;Q4G(K}9RI%ON#t!E!ubjG_gJDi7h^_pCgK_>Y?wf`nj_wam2IiHwH-J^KTw5V6T>Nh{6PTy4?%l_g+E@DUIRyaELmH_'), '*': (10, 13, -2, 1, 6, 'c-muNzz#w}Aaq84XlQ;0h{c$4>2ew)n3a6#aw?dWQ4kthkb$a$Q~&^Mr3&K'), '+': (14, 11, -2, 3, 10, 'c-muNAOtE}h~n+}4+bYl)rS)R01oL5X8'), '!': (9, 13, -2, 1, 5, 'c-muNzyb{Z<7DW=80z1l42f5SwW9$5IPM8L'), '?': (10, 13, -2, 1, 6, 'c-muNzy=ue?tEOt4q_=y5>vRJ1rtA!3Za=M?PZ6sDt53!<yMtonzN+_lZ6fdo{J1o'), '=': (14, 9, -2, 5, 10, 'c-muNzzg>L2ZIx&$`J_wiLeg+'), ';': (8, 11, -2, 4, 4, 'c-muNzyLFrpwhVHw`PGU=IiWO6afJL8U?i'), '"': (10, 13, -2, 1, 6, 'c-muNzzS|?EQrC)qACCYI-mvh'), '%': (15, 13, -2, 1, 11, 'c-muNAOKoF91>+<2%8DvX<ZlTX=UKKAOzw1&u4I1&Cr_!RjYeVxT{_FAR|m~_s1jR`}J!-9Fu^FBur4eC*INr<q2Hi18TR~4CPLbWKg^-*4z)_nd}A<wI5DM5pp2_bBP`L'), 'É': (12, 15, -2, -1, 8, 'c-muNzyl<1i@@3Q0%5Ex|AAl&lpTXmjgt*h-$A1K3wWFb0A-XJlK'), 'é': (11, 14, -2, 0, 7,
'c-muNzzJCQhrpOKV=$$~SG|2$2xc)Jn=Ght%NxYhf6vUokhK8B^!xwk@4x?hK}^G^j4)kH$NR)YlCmKtEP45IjtDO60q2_*lK'), 'æ': (16, 11, -2, 3, 12, 'c-muNAPCO<|8qUG{OQM4f-n)z%>Os^`TCY2)ZB|=VBq-424-j8`uYF=pFe;9{Z|5U)!&<OFh28#D>Ztf#@F=!iV>H^Qiwp;+qatx=iL5s%#pBL7yxtqBt`'), 'ø': (11, 13, -2, 2, 7, 'c-muNzz3AUq}rZO*ZO9HSS&X>`E&l8gP3OTS;Y>n?glXfF0${`t6C0Xn!Z>Nz%Zv5#ALj^lgIV5F^Flsarc)SkzliAc<@>X0HlT&r~'), 'å': (11, 16, -2, -2, 7, 'c-muNzy<0*R6tq0#|4kELz%|}j<UlPe5}CKb>{z%lSVKOXXb5YxXe9uFqL`h=l}l>AeQ=jGY*FPE+D4S8#SJi|6nFV&xdEzuejiH6#zX`8%+'), 'Ä': (13, 15, -2, -1, 8, 'c-muNzy}sgh`516>cD$;I9uWSjZiqJZbRi3IOk5J(r<An+vXb&!|6gOXZC6ahLQ^qHs{CxAfONCM80AJlDm4roE=>tGWZ1xK1TuoK$sg?'), 'Ö': (13, 15, -2, -1, 9, 'c-muNzzhBx?5Myh5q<H;%b7wDcGmj{e$DOY*g<U0_ensK>v<Z8WAmREM9o|cA_KmF6*ue$k+#S(oF5>1(!mOH--q*SY`@3>F+1+k&sVdB@wyQJlwBRj'), 'Ü': (13, 15, -2, -1, 9, 'c-muNzy~632>e&TCh^4vNR;d$pYz@kNK|fza4sYRi8<3DoU-fsTpnNSARLzZyWcKH;dLVe0OG_Mi2'), 'ä': (11, 13, -2, 1, 7,
'c-muNzyTaSF#NE<5Iyt%$4Mg?hcojwGhF7LI+)75_4EIK2M|mBy%`6?eHReZ=#3gr$$v1Dq36T1=~rBE*$M!d4HkU'), 'ö': (11, 13, -2, 1, 7, 'c-muNzySpQE1bx{5LMaz>3SHL#eA)c-{XrRh-vzsm4RVi4~Xf18A#MDM-yef-pTL&)d;LlZSUtBk+>{n004r&6%P'), 'ü': (12, 13, -2, 1, 8, 'c-muNzzJCX>+C7PBK}8$fnh=m@$4@O3=B)4?Bh*b?%$wn(<>j>FK)qYKLY@G%@iO'), 'ß': (12, 14, -2, 0, 8, 'c-muNzzHO`e7fTcWiMUGYxj}|!oF+C;Pu)Z!hT^8a$b`G#-35j0B0w>GKaGn%D*JT*$kea;B4lY$53|2|KC?#al3^90H^vI{r'), '·': (8, 9, -2, 5, 4, 'c-muNzyLd1P-&t70C+e8c>'), '–': (10, 8, -2, 6, 6, 'c-muNzy>n@13?Z082|taZ3NK'), '—': (16, 8, -2, 6, 12, 'c-muNAOtf0!$A%M)d2vzYzoT')}, 'SN11': {' ': (0, 0, 0, 0, 3, ''), 'A': (12, 12, -2, 1, 8, 'c-muNzzu|dPJpxX*FR^2u`gI|4uLX_ZZHIIgR&=AFtELn1~b{;{s)38Fgxrhkg&TAW^c~~5{&okaN7w0Kv@&K'), 'B': (12, 12, -2, 1, 8, 'c-muNzzN>`|NnL_8<efXAagAm&X&IB30L!f6$4ycVowR2&5*Sd&KBD>5w8B-N<rLqG5`QYvKea'), 'C': (12, 12, -2, 1, 8, 'c-muNzzJBJ?ti}!17R;YX~wOyNEpOa{V4-i5_T1#JRFIw`coRgS$^DvOJ^ZiF9Tca!ygx8aofoN0Nc$G0R'), 'D': (12, 12, -2, 1, 8,
'c-muNzzN>`|MPsU36!nFqSX9N56T7-OXnllX{QkEbR_n&c`&_-P2cokX1-i!g4<380P02<bN'), 'E': (11, 12, -2, 1, 7, 'c-muNzyaR;2LcTUQwJfcgQDOM13m?)YX3XnvI+omKNOY'), 'F': (10, 12, -2, 1, 6, 'c-muNzzW{{|Nnmjgrx%)(?OPvz%7e~g#iFHv=3_'), 'G': (13, 12, -2, 1, 9, 'c-muNzynwt?*6>l$^+pnIcdSIQW*_qtNxThs0zD=q$TVs1B1o?{|lhXq=94!gu}4xxH*^Ll=%=2Tl4*&_hv}qvz-9|k*F2~'), 'H': (12, 12, -2, 1, 8, 'c-muNzzN>y0Es6C_}TwKz<_x5NNlVC038$+Oa'), 'I': (7, 12, -2, 1, 3, 'c-muNKm%`d$fJ+|0CM99!2'), 'J': (8, 14, -3, 1, 3, 'c-muNzyxn}$fG|igGfe~&+H(&|7k21vjKQ%3(o'), 'K': (12, 12, -2, 1, 7, 'c-muNzzN>yFmUah!vtmXAL(O+iaVWefU9}ah)}=irX)gd<qb)MIaN0#;B1EK>k_yv1pudY6VL'), 'L': (11, 12, -2, 1, 6, 'c-muNzyaRqP?Px|2n29h1pvUv450'), 'M': (13, 12, -2, 1, 9, 'c-muNzysbqW@cc>_@4ve9P(#iIC})jiQ2|szHJGVqi{}Pz8{>EIrSzpoWuL6o&nAQk=Qsm008B{8(0'), 'N': (12, 12, -2, 1, 8, 'c-muNzzN=*Wn^G@p#fn(2uHBvZn41G3fs~VZ2iZaa5lrzG6Y-c#YZ@sVak6E+?E0W1}_-X'), 'O': (13, 12, -2, 1, 9,
'c-muNzysL3p8mWP3gs+2uE!hlJ_yWK`6&Y=^Us4hVOK$<-alpxj_OZoAejeI#<22;4sX!A5D15(=h?3-5e#?%04WO>PX'), 'P': (11, 12, -2, 1, 7, 'c-muNzyaR;|9vwQ%G6;A`7R7)GBCV1g)*5#en3V4|G6E(09U|(kBJ2U0D}M$rv'), 'Q': (13, 13, -2, 1, 9, 'c-muNzysL3p8mWX4&^L6uE!hlJ`~JW`6&Y=^DlxqVOK$<-alp#<qP5bVggYLKcs<V-U)~S^N;B82EF!xa5(y&|NrfYu!?o|Hcos_VE_Prv>2i'), 'R': (12, 12, -2, 1, 8, 'c-muNzzN>`|8qME#@1o+|0x1vGcdd}hq0OczX-zA|Nj>ZSI?StjUAzWT{(iS`bHeLr2waQ7F_'), 'S': (11, 12, -2, 1, 7, 'c-muNzyYGJe?4jsW+{C0<TPIlW?DRe%QJ7@TW-$`<!B{sIKc^*y5<iettV)3xO_DSF<El2eZQ55%O(Z@kGB!j'), 'T': (12, 12, -3, 1, 7, 'c-muNzy&z|gTVnP*Wd+0idt+e009224r>'), 'U': (12, 12, -2, 1, 8, 'c-muNzy)~z^8m^J62!8(|MN01F#Z<@YyPapz##pL8O&b2OjKy@7Kou@E8e_YE6IQx001u!6F&'), 'V': (12, 12, -2, 1, 8, 'c-muNzy)@s0}00ab|7}x2_WHk8!XQLR*QjQQ58hd<Squ@Ptp*!(Q}rRZ7|&ze2#{|*!gE(v%%QHKPNEY0|5EF5gh'), 'W': (15, 12, -2, 1, 11, 'c-muNzz<rcGcfr4*JfbYk__UyTw`G9Ig!o4{6PuC<@_PWaN1`zgUKU^>cgRYSD9}!lq`gBo2K~8WZ0&?B@x1Py4(}RP?7sV0m9|@en*PI>ed68RR?Y}FtC1Iz(5cH0N(u`a{'), 'X': (12, 12,
-2, 1, 8, 'c-muNzy*Y#m@qIju7+>|uCSRs5{Akw>$~9vSM`2AT!+h>D{N4vzyq7*tx)!o4xm}aU}o?|pn|~5Y&b1t000Cg5wH'), 'Y': (12, 12, -3, 1, 7, 'c-muNzzNpYGB7Y6NCmUSp6WB??tn^!T+nzT4O6xJLmXU(@hgOGgBOI^SO5SpO$|i'), 'Z': (12, 12, -2, 1, 8, 'c-muNzy%WigTM<opX*#SoV~IW&aBzO1Y`PL;e#=?AF9BZLN{Fzios_7=fP<y0|20e6YT'), 'a': (11, 10, -2, 3, 7, 'c-muNzyV(T|GZTU#^G-6gD@JO{{6ol%(A+n%;L8P%yhmYDtj2hWLo^?diNe&W-<T(zl{-{'), 'b': (11, 13, -2, 0, 7, 'c-muNzybafWR^X@9{^?c^SZthg)oH}7`FMsncIC~3S3|c%3eGOz-1`|0P^P)1O'), 'c': (10, 10, -2, 3, 6, 'c-muNzzVESe*Yf>Vu-wn;e-hJ?}bSQ?18aF-b8XhnKq|?LUdpP07~x*kN'), 'd': (11, 13, -2, 0, 7, 'c-muNzyto^V+K8VUIJlCymRK81YrhkVqg%$U;-8JPQuWJ4FCY%+7t8'), 'e': (11, 10, -2, 3, 7, 'c-muNzyYjIeZA@lW(i$1WHWuj1!DUB2LT-r(|<o)smSYOE*RVV@YnxeaGA*f0LxYpCI'), 'f': (9, 13, -2, 0, 4, 'c-muNzyd7p{TBf<*2Y6cP8vYy1ONYDfUwR$MTlac0RS|745<'), 'g': (11, 12, -2, 3, 7, 'c-muNzyU%ZJTLhJW=Xzx<eLOx25n?u5P~p+5lqSV_Pi4yOos4>&+Fd8%;0O;3Sq4I|7DL7E}Iwtx6&2E'), 'h': (11, 13, -2, 0, 7,
'c-muNzybafWEMVq8USTB@pwIgGC3F+zOlm9e&N8w!~y`0H4!x'), 'i': (7, 12, -2, 1, 3, 'c-muNKm$KGu<(eWkN^M}D+d7'), 'j': (8, 14, -3, 1, 3, 'c-muNzyv=yu=5GhY+y?11DG=TRE))J0PAT9ss'), 'k': (11, 13, -2, 0, 6, 'c-muNzybafX0ptk%K~BYY-@yxp2>hK=-SK<SKGLo3vNQ$VLn{80su9O5P|'), 'l': (7, 13, -2, 0, 3, 'c-muNKm$KGD58)60G=WV0R'), 'm': (15, 10, -2, 3, 11, 'c-muNAOQZ?K7Z^u<;xXyD7T(F=X)A=+af5JgF*fc1B3NZD3^gj<_QCX#R+1#cmM!K-4>q'), 'n': (11, 10, -2, 3, 7, 'c-muNzybajK6@GfWj676J%Tbh7#O~>LYP4Og#!;03jhF4Mh-X'), 'o': (11, 10, -2, 3, 7, 'c-muNzyZ9kecq=6W=VYT<ZU|vW(MwJU|{{l3t|Q#m_P+QEhk{wzCg8M0{~mV4{`'), 'p': (11, 12, -2, 3, 7, 'c-muNzybc3J-;6SW%l#Bz7vHog%}vN`NEmoePIe*U<%4!Jb-CKGK>Kq003}l69o'), 'q': (11, 12, -2, 3, 7, 'c-muNzyX3DJTLhJW=Xtr=9>gz25n+s5W-*r74Sk8AZY^w>`XKO0AipL_y'), 'r': (9, 10, -2, 3, 5, 'c-muNzyki4JZXk7+PR@3yf7&SoD4Jo0JgaZbp'), 's': (10, 10, -2, 3, 6, 'c-muNzy{cse)|6a%<|dC4;52?F(rfx!j#M3bcYivEcaRtL}mQ{_pFKmI{*NyNDZd'), 't': (9, 12, -2, 1, 4, 'c-muNzykiTpfR@m|Nox{yA;E37~_pPlu_{ksu&Fb0GQGYLj'), 'u': (11,
10, -2, 3, 7, 'c-muNzzzi7Ffg$Ez{BKy55y2A!z*W=HYhXV`O|_Q47dOQ+Di^C'), 'v': (11, 10, -2, 3, 7, 'c-muNzz%Br85o4$a)X$1&si99=Rt(``Z1ifg)n2+>fC`U=6b!L2BvY&UpWSx006Dn3>y'), 'w': (13, 10, -2, 3, 9, 'c-muNzzx!;GMN20Wtf%*;;7tUs61A|a8ns9^-yMy{chO@5Owp@FEd=pm<Qp+Jea{S^FcI(BlSO&A?&{-13mx%Z^IP%'), 'x': (11, 10, -2, 3, 7, 'c-muNzz#GX%QG~rfUsjvxZUJ~iZA$P3}vyMe&z*bPMo3rNCwObxX8hfe3%7?p$q`nGz}C'), 'y': (11, 12, -2, 3, 7, 'c-muNzz)hMF))a|-~us)pK~&lcSD31#53MhfG|ytx~+$)K6%~|#!S2nW3kUmfwC0-?q*}a4FJ|<4e|'), 'z': (10, 10, -2, 3, 6, 'c-muNzy?zO1A!-$<G!8+!Z6vx1!1Th5{59u4=X?wwSsi`U^R>Z0HGocUH'), '0': (11, 12, -2, 1, 7, 'c-muNzyUN*{XD4(VIFG|Xxa~E$$sTv;P@&5Vp`t<61U92%$q>swi%iNh7&+-2OuVBpZRr49hXfE02c5Qng'), '1': (11, 12, -2, 1, 7, 'c-muNzyZ$u|8D{3+@X-U<p2Nwe{k8v003+{4j2'), '2': (11, 12, -2, 1, 7, 'c-muNzz!HwZhqV>4Q49MQWIFZ9xmg13dUmEQUFsuYaSzn#k_DXl*O`gHk8F+@E-`CFyI0J2D}hf'), '3': (11, 12, -2, 1, 7, 'c-muNzyaLOem!XkVb0d&EV~X9XD`?fWu5r{R0Af;U3QZR#%B8`0-{tKB?W5lf<>5$AAQ)Vjmstm0A@E3`v'), '4': (11, 12, -2, 1, 7,
'c-muNzzNF#+dx@bJ8nXm%=?vYK$+Fq3{a--PDU8B;y(x^z>I*YMP;G`0DPwrk^'), '5': (11, 12, -2, 1, 7, 'c-muNzyU7&|Np-P$}~WTA~8RF+@=iU2v0fzmyr6!2p2sLrZxWmf4@l)mrV=+qdF0y'), '6': (11, 12, -2, 1, 7, 'c-muNzya8&y#0Ry!t6V!3>D=3p#hWEe%JZ+ZUmUA|G$RY^@|LMDfmx}f#I?XSa@3vm+L1fFjL{+kDCFwY+?WaIam~o'), '7': (11, 12, -2, 1, 7, 'c-muNzz!t-1Hlgt7`J#iT;`e!jAebF5yqTf2V?Pml7lhRcfd8B3T40z0PF`0+y'), '8': (11, 12, -2, 1, 7, 'c-muNzyU&U{<s+eX0d$pW%vKa0%9`W@n!SB15sf0{{MSRFpKwj5NF799uU*)F_3s-3StU>4d4v?A_P_ubp8AF09-aP007je7F_'), '9': (11, 12, -2, 1, 7, 'c-muNzyX49e%~ttW=Vf?;i}sJX1ZQtU=aVy3u4NAcI2x0uLTy4y!*B7lPXN7-Zxe#OXXMxgmLEoyUA?0Y+?WaYwHwp'), '.': (8, 5, -2, 8, 4, 'c-muNzyMbQFvS=E7t8@A'), ',': (8, 6, -2, 8, 4, 'c-muNzyLc^z!b-6PE0ul05Sss`2'), '-': (8, 8, -2, 5, 4, 'c-muNKnE57{}(V24FG{h0_O'), '/': (8, 13, -2, 1, 4, 'c-muNzyvYf5PFRbm}0-n1g5>`LWF1ef+@y3oM75=9YnY@9ztIc#$qG`0IWm^Ap'), ':': (8, 10, -2, 3, 4, 'c-muNzyMov7>EK`)d2uoxB@`'), '(': (8, 14, -2, 0, 4, 'c-muNzyv$Az?9u)2zNmYgnp<DrkMY6pwKXJh6T|O+IBOlIVb=CCBF%`'), ')':
(8, 14, -2, 0, 4, 'c-muNKnE<Rg&>UVRtPQnlo7(Xr46C?`a<Y^J`nmQL|g=_E~^bpF`pJ@zytsxzX`P'), "'": (7, 12, -2, 1, 3, 'c-muNKm#wZQKSI?qjUnf'), '<': (13, 10, -2, 3, 9, 'c-muNAOJ*iPIE(8tO4sE^&3Oj4G))kGQ*TKJY3=d=P<AZZg|vZgk(VO8E$+Q001}h459'), '>': (13, 10, -2, 3, 9, 'c-muNzymfnDkC@w)z=TF@+0^r6CW&Rg>j50JXitY$X8uEk_J<@xk-hA5C8x@5e%a'), '&': (13, 12, -2, 1, 9, 'c-muNzylbkeLSKJ<G5WDHz|N|{P!a%llxT)XLDS3-Y}WjaVwbPe1?IkciVbTFh}NdESJ*7=YkM*p69;bO|Lk}j?a1k*cKIg'), '*': (10, 12, -2, 1, 6, 'c-muNzz!w|K<I+d2}&!uKrH6!hg-G5V$4+!w`ifsB6JW30LbDB5C'), '+': (13, 11, -2, 2, 9, 'c-muNzz=Q+5awL@4+cD>=)nO1bbAa-'), '!': (8, 12, -2, 1, 4, 'c-muNzyJ{ku+!oDA#}iY2<^NIyFL^E0Did#YX'), '?': (10, 12, -2, 1, 6, 'c-muNzy?hI|9_DKWivVdVS_Ro_Cp!5SNNf<llCw@_cbuhd11hS0{{T=DGGD'), '=': (13, 9, -2, 4, 9, 'c-muNzyq%Q2Lm2bWQYL(+29Se'), ';': (8, 11, -2, 3, 4, 'c-muNzyMov7>EKpQot0)X-+JX0DoTt82'), '"': (9, 12, -2, 1, 5, 'c-muNzye+XAr1y5005&a1#t'), '%': (14, 12, -2, 1, 10,
'c-muNzz0}2eObuJAaalu%=25$z0-<efi*<VAH;K>4pqsv<;yaz!vaWpTf<zQK5>L{v^OvuGci8|;V|w}U^s4K0p(?sFfh13d+LnWAq)WDCKv4'), 'É': (11, 14, -2, -1, 7, 'c-muNzy+8l1z-xk`40pd5T*`7R0l=D9|n91P}Tl-z-2!G<RcY&'), 'é': (11, 13, -2, 0, 7, 'c-muNzzMXD@j+Q!JEbwDtxkQt>Ir5ET{L7feZmD|`uzt19T3xhKU}HE>trq%+x+m?|6g$02>_V669N'), 'æ': (15, 10, -2, 3, 11, 'c-muNAOK$c|F+Kh_>U_tFahr77iMe*x4FQa#;1S(gMk5vXLUoFCG<F4tIHKp#k2o2xuIO<g`e+Ng`E2G{|_NM82~GK9?}'), 'ø': (11, 12, -2, 2, 7, 'c-muNzyrit!Ib~?&uh0!gIF@3y?M^=1Pg}jVVL0ioeM0#r9Fi8mjH;#^KK$f%XzQ@x1|@p9@GFcWm)jq!T<pJArl|'), 'å': (11, 14, -2, -1, 7, 'c-muNzyUZ9zp{feZD!cd#uP;YFaCetDhA_lH}^ppjZgpn-wtM3-B4!n+XH4gUlEl(3}G@Y{&Ky04=(!|07-!tGX'), 'Ä': (12, 14, -2, -1, 8, 'c-muNzzwdr?1{l9F8p%>oSnb^IU9_9!E$p5lxcK>A$S{<J-LE`?Ugi`$^P~~5LAKLVMl?4-EA;?dnS-zyl02oEdX!u73='), 'Ö': (13, 14, -2, -1, 9, 'c-muNzz1Be=)A!y!QS=s=cQ06XW4N*-jMe}V7AIn86cT|9?S{53L^FXF=KF4e@X+%Jcu%el}B`VgWiQeI2=9CeqD*c>nsKUal{#a'), 'Ü': (12, 14, -2, -1, 8,
'c-muNzzrsJR4l+0<@wJ8B>zhg%jW*i%fP_+UmUFYvl;_~^e<*Gd-XC=p}AWihKj9t^KPvq9=8AhULF;1'), 'ä': (11, 12, -2, 1, 7, 'c-muNzyUHg1f0MWeewVERxucdySWd-Xngwj|8_9T>V`6l-ySg2`HHCQVF;6H@t5n}dvMvr005>M6U_'), 'ö': (11, 12, -2, 1, 7, 'c-muNzyT~CDEz<_^}hCbp9+{I@xha~?F5(^xQl^-^%pOQ8H8X074Wp2fNA>z)rJiK072~$q5'), 'ü': (11, 12, -2, 1, 7, 'c-muNzyS<iNc_hT6nMkH!14nRllMIkLzoP&oO#-y%!ubt3x43Ti2(q>01#X'), 'ß': (11, 13, -2, 0, 7, 'c-muNzyS=;e%UDkVV+Lq>hFXwf3YfWngn6~XE<)p0ApVAhBMt>7QvVdl2<%nOx^=w5N68%PfOWw*$MzCx)zQ'), '·': (8, 9, -2, 4, 4, 'c-muNzyMbQ7)S>IJZu3a'), '–': (10, 7, -2, 6, 6, 'c-muNzy>P*|NsAkfp`D_%G?BQ'), '—': (15, 7, -2, 6, 11, 'c-muNzz-_^!$1WCMF0Sy;|b^')}, 'SM18': {' ': (0, 0, 0, 0, 10, ''), 'A': (15, 17, -2, 2, 11, 'c-muNAPg@2Uyj6+|Nrg-D}tN%KmWfgg1h%7*N-W1p1|*ZhMkY#+-RW6g8xP^?y4_r3~K)yp**%v8-e7V3sA1de+W>3aHm7Ld0-yn(|0UDO8Ng@FxT||LWo0u3xcSY{{dib?f)1;UIPG+%QH#'), 'B': (15, 17, -2, 2, 11,
'c-muNAOL#)|NsB<_6#{BE)cvFgK-@gSd`ZP&qZ(<7<~WNBFU=m`0s?Q_hA8wQ6IXQ5sF!rXZ){2Hj44ZJ!CG!!yiZ{%eMT#hT^LKQ3&qe*V{cA2m%0T14Py'), 'C': (15, 17, -2, 2, 11, 'c-muNAP5xZKKXvFkr&D{e*Yf?3LrezTmR>)vMM$uL%4zecOdJW`ackvyYs&?GWW=TaXhlqQ1yoV--gU(yZ3*N3cE&K5|nT83E5Q)49W|h{<sczGj0F?5RfVF'), 'D': (15, 17, -2, 2, 11, 'c-muNAOOz%|NrG`zYG!=2;P~&xPKV9OqTw?%L3;D!S4UQ$lSR9oyc6X|0|HW+W)tp%C1D_#{Ta@=I;FO2j_AcFaCd@71>oEED?_UdVQiC17QFF%?~?X'), 'E': (15, 17, -2, 2, 11, 'c-muNAOKwcLqH1-ZUd@f{9Fidz`-TSD6A%Lz{<q~0I%0NtN'), 'F': (15, 17, -2, 2, 11, 'c-muNAOybr2ZIwhxK~gW<L5&3THxT4WE3e}+yDS2oGrl'), 'G': (15, 17, -2, 2, 11, 'c-muNAP78nz5jF~kp;>t`ws>V5T5DZZ<!*zW)rO;+@=3hk#)ZK#*W0}{eK=L_W%DDFjwOLVPr1v|8rm(%4K-@g%z2*{C^ZO*Ye-T1VL^u7?+_Q?5KY+FuVNsef)aRk+9zYGTJwc'), 'H': (15, 17, -2, 2, 11, 'c-muNAOOz%0g)R2mr#NG9|CZ2sb~=@7Y_gcVEQ;D'), 'I': (15, 17, -2, 2, 11, 'c-muNAOLLsLjVs}E)dlG_d!-aAY6iu#03C|c`XD'), 'J': (15, 17, -2, 2, 11, 'c-muNAP9E+2Z9V-Tp&oG88`WV8Zx)`e*}cVy+2T%!{ot#T?m)wKNuW?sdHQZ@Yl0>qJ+K1007`oCpG'), 'K': (15, 17, -2,
2, 11, 'c-muNAOOz%0g)27J{TjoB3HgxA!PZ_eRD)8<~jD$1EH65|L*`Kqjvn?iDdHszi0jjBXJXiU%nPYwm0<u1{7zk{U49a6@U9d7TJ-p|MxH=aT&J!&mrVH02M$p)B'), 'L': (15, 17, -2, 2, 11, 'c-muNAOK|kuNewlC}6?H#RCBQL?gZ'), 'M': (15, 17, -2, 2, 11, 'c-muNzz-b$|Mvw__5c41K)9b)0;yY{VB7`Yco{5yE`xDX?<X)!-7p2lO=;c3`X&Uy)%=_Jfdj#1IQMlf0}{9Bzaugi1gOBp2LL{0JoW'), 'N': (15, 17, -2, 2, 11, 'c-muNAOKGMUjrm1{?CDNe@i2CzkX;$=6;y?j0Ksi@jn!q%dl@h3OD4x7BZLR>11RsL&HZEWUln@24pV7+NUU7=l>{Nh8r+09smH#@I8_'), 'O': (15, 17, -2, 2, 11, 'c-muNAOv_PJo$OMiUrDJI`kg|W<a^Y|8E<zyS)3S1>r9H?*k-D|JOjcSO0SZN#p;kA>6lbL8RFKBM|P_ry!E=|5>cE5WPk)z03c51IZGY$zlI*8n8LNh1tt=6vb5x{F9#kx>L<U&~FR?8f`c%'), 'P': (15, 17, -2, 2, 11, 'c-muNAOKwc|NsB*?REzwE)e|nf^i!dn3Wd%KaJorFfhIS&4|o>_XojcLRO4s6wsn~I~*C1jY4t;`CL2z0Cb5oBm'), 'Q': (15, 19, -2, 2, 11, 'c-muNAOv_PJo$O2ngz;ZI`kg|W<$Bb|8E<zyS)3S3*j#N?*k-D|JOsfSO0SZN#p-(A>6lbL8RFKqY&=bry!E=|7ld&J;-{E{x5@>><uJK{^vlrA^&e0usOZ`E{o!-VwjuxCO!N2e>Ji%*th(zMCP-tp2R}X>i|mtJE;'), 'R': (15, 17, -2, 2, 11,
'c-muNAOH^h|NsB>i9}{3E)Xn&b9oqq;(q*BM{pS!X8jLG=1%|biQw`DetE->Y}8E~WRt&_Bkbj2RNVeQ0?8r<zGn~EkxfqeUxLhKzW!baiOUf3e*z)j0RTw4JeL'), 'S': (15, 17, -2, 2, 11, 'c-muNAOz&*KmBoYnih=r@;?YXfpRDRU#rcb6t@-1J@AVIS?kij(#TwsU(eb-1rdDR)t~?W+NzEaU^6Ot`bid9i|PMHWUlJ}1rSDSv$-&r#nJ!u5bhkXqyE2?gm8t6j=ui&aE?4dzcBy+tvN6#'), 'T': (15, 17, -2, 2, 11, 'c-muNzz=5phk+a{To9=EAAqc3aB^`001)aYga'), 'U': (15, 17, -2, 2, 11, 'c-muNAON=f7Xgws|2t^S-3;ZnL%8eyivmg8|BVpt?EjiTGUR^&gq!jIur{~V?f<qAF3;`%Ag~AKXz@8Oen05oWFQCt1|Kr2'), 'V': (15, 17, -2, 2, 11, 'c-muNzz?GTSAyxq{|!Nu(4T!^?z5*5>BB#`fTZ^SSrBgde|I2R@ZS%@)%o8IB)9zFh8lMN0s{l<=j|}Fr~DIRu>GG6<9hy&WN7-Y0OPWMnagnO3c@8DAM*X~KycIkm;Sd!aHamgeanpG?sNZ_G7td(3vnuN'), 'W': (15, 17, -2, 2, 11, 'c-muNzz^P@f-*iI0g=aFKzKs`=YpsO|JcD?ga2h9s_MTAnCti7A4CQJcVbxhzl0(8zb1&Q`#*u<_V=|6-GA6XT#mnWBL62pV_10`V&sE4exFtTE1cK@;qKhkzKh{e)U!Sack+#cH4IB<{!NE)bH07GV@QAf-vPpP`~QQTLG%BANeEZ|{~;jx>JtM&003!YJ4X'), 'X': (15, 17, -2, 2, 11,
'c-muNzz=vIKji^ZOy@q!f%$>|JAq`@{~W0Nrk`pIBJYkeLAi2YwlmEAsR`F!^1tO@Ey6UGi~ldNBALGR|0X0}`2Umtec?R87uPv2Jm7+H=l*wKaQNR2<vIRe03_G^g4o1y>#YcoQv9(W%x(Lh45ecU_>KVpSbr?)'), 'Y': (15, 17, -2, 2, 11, 'c-muNzz>rC*MaFZ|13ci<Ebx_K+5X>LWs1*zd1ni*e407@`Zo(7{dOSz;sJ~+QoMF1}ogOvj3a@dms#FyY+tqvSoGu{gAme|9z;%#RUMuMIzh'), 'Z': (15, 17, -2, 2, 11, 'c-muNAOH&fLxBhi_Z}OP8lOMbNIc=^O~?kUKFNZ_i~gdD#FKuXf~<7s24r6La}gw-$`=nL9`mtD$V!V~j)bULfXc-K0ArOeKL'), 'a': (15, 14, -2, 5, 11, 'c-muNAOxJ(KK_2CkQvI8`40w@p<L-*zJeSkSAGg3>qz|X0A&U3d-o5h+6Tgmh3Nes0O20|6d=sRkPhd*wO|trdIsa>gH-;T3ga@C-Tr<hH~_}Q0|4d%GDH'), 'b': (15, 18, -2, 1, 11, 'c-muNAOL*+2T;PTe)D0OIGnrwKM-7Cg>k<{@oAs>9|z-329ieq7sI$9apvC#P`UeI+$liP@c$x&QM_6w{>Q+$>rgEUsC|oY1|9$a%2_po'), 'c': (15, 14, -2, 5, 11, 'c-muNAPAJ^J^699o&(C$dH){-LZI9u|CefWsg-*{c+&q*Fe2%+|KGrX!mUT<qA3O&#i>&43FYddTEw6<|LKowW$Xl<3jlgJBLD'), 'd': (15, 18, -2, 1, 11, 'c-muNAPSWH*C2<hy5-B`csN)1`Tzg_|80PAoBwZ65G?!$<DU2~1SEIBxKFP^)Sz%%VBF*11(6ju{a+`KWR&PjkVWg^&QRa}^=TrSBe4PioV_)D'), 'e': (15, 14, -2,
5, 11, 'c-muNAOzT|Z~S~YQxM8y-uWK{&agqassHyGbI8s8p9taZ{mKhc^Kk`)`}jWu97g4yfN=LeVnntl<NtC)ZV|@?(GV`nZiwO(m@~>ReSf__frFrX0hK8<HU'), 'f': (15, 18, -2, 1, 11, 'c-muNAOhsw{_{Tq&U5+?1PE^Te+OnHwM)Mu*dG5OAOb5F2v&SSv4?J4TmS$iIw!0'), 'g': (15, 18, -2, 5, 11, 'c-muNAOw`Retn!+@?QhO6L|dp|Nnn$Vcfd^+f@W||H8P(eux6e?J(}s>mafj&b@}hMN<qiia+N!j4SvAXwlzg|J9++P}%nFaeVcEd1R+8{mlVoEsT^Di2HRACUF6%_y2Eu7*}V-^KVC;83+RajpaR)'), 'h': (15, 18, -2, 1, 11, 'c-muNAOJl6hfu<ex%+*aIGj86-~a#rH^8}{qIiv-{NaUhrvS;u|N1a)JdjNLZ;fnn%6}Wmxp)8otIaJv'), 'i': (15, 18, -2, 1, 11, 'c-muNAPj8&r{Lk@0|);9M^=o+C1f($+=BlQFas+W4*&oaYb8A'), 'j': (15, 22, -2, 1, 11, 'c-muNAOh@of{%*_wEX}7{|QbmL6d36J#htz!{qX3Gn^9xbmRYEWbW%mqWlT~h8ra1'), 'k': (15, 18, -2, 1, 11, 'c-muNAOzkVppe`4zW|Bb^)Cxaw*PN3Lh-@L|5K6l{`viXHWK%T&$R!+$R=}Me<y=%k<qUMOvv_@|F1^oG9CDBLCCKF7bq+;'), 'l': (15, 18, -2, 1, 11, 'c-muNAOL3k|NnmuPA(7(6!+sQ6z=(t#>m`UpgaFdz_~0F-Xn8y0RVuSAma'), 'm': (15, 14, -2, 5, 11,
'c-muNzz=x-*Pnjr81(jnB9!~?|NpBm|NmbC<?iL1@xO=v_;o0^iXr5`6GP8CC^whE^S>!W<2NWbhr#2&2}8pVin;gz07xn_zW'), 'n': (15, 14, -2, 5, 11, 'c-muNAOJl6hs50dzD*p?o%-+p|Nk4{+)q)wMo<3m!njj_WaEE*7&jhBrv0~u8wDg&{@YN_#RC9PWG2x'), 'o': (15, 14, -2, 5, 11, 'c-muNAOwVGJo|O8g$>GMzxW>n)<C(*|IZonI6e7q3E{5zZwMq~{?|dcM}IN`NtOR|P`R^_6-UDqC;vZV!0qq|W)#$-wJ>Lh%zXaqek(gc=Q02Qe*!Gl'), 'p': (15, 18, -2, 5, 11, 'c-muNAOJ%C`_#OBw?G)qUHcyhjx)iyUn6*R&i)UCar=R!+5c%UZWNGY{ks{Jy9LIb03=QS&p<Lt`}F@%7<U86qBG2JXEeS0uviq~Dl|tD&&2}(141=^'), 'q': (15, 18, -2, 5, 11, 'c-muNAOs{=e0*6D^WO!+W4rPn2-d>5N&io1@+JI&ahLzs1Ck41+@n7kfn+wE`vZl$^1m*SoDbus{y(O{7xxp!<+y=j5rg!qPp^vM&VT?)xL5%I@dP!h'), 'r': (15, 14, -2, 5, 11, 'c-muNAP6p8VCj7Rw2cYQ?fwr08Zhp|M-jpb4XQBie}5FcUr>#@hGsJPT$}&^5Dprg'), 's': (15, 14, -2, 5, 11, 'c-muNAOr*_-2Z;FTNuXO{vQN-pghjMSG3uc3(BEfrq3%-^u~NS-jghg;PVGHp8S=7qGa<sC_{c%pfrc|li$n`t^(Me|4U%%T-QDOa;1WupmP}j3t%Mi'), 't': (15, 17, -2, 2, 11, 'c-muNAP6k}rx44%@gD+2uyRQ<3WIC<KMR?w_<y$q5|{BdibV_t2fiY6aRC6lPA7Z'), 'u': (15, 14, -2, 5,
11, 'c-muNAOJl6hXBcx|2C9!-T#LI$pRSH_J1LeTnyt%{J*Wum-rRNWjOTz|Nr09;9Q0MKW+uWjlu%}v<D{K'), 'v': (15, 14, -2, 5, 11, 'c-muNzz<m8?gmkekB&k3v;K$yN$dZ)5U#`jOdvVwk2r+O^yC1Lc(x0syZ5gYgX8}M7}w-~KEsS3d~m~W9%FgE7GYPzztsQ12(J47PaipuoO1U60tO-g0AnB@um'), 'w': (15, 14, -2, 5, 11, 'c-muNzz-g8f->&!1d%IVLU^M8>p)cQe|a$1`@b`YGWs9Nkn`V~q45t7h|Bz?hhfvF7KUwSA)59cV*ONphT-)@2)F5r(;c24=KsSWT=)N5CNb>Y@?RRl<@@{JouT;u1DHcDer0FS{J)feAOHaRMJo9'), 'x': (15, 14, -2, 5, 11, 'c-muNAOPn5Gy;<0|4SfTuIo3s8RS1~V}wfUeV@mC<f$lJdDj2ke;tstZ~fni#1nt<|12Av$F%!>#GgrUZuS2#hPwX&P@eUlc?=B9N8ZVUc|wnF^8hLN564*vIT!%Lydj_'), 'y': (15, 18, -2, 5, 11, 'c-muNzz>-2p9j-NUa^7c>i_ycQt5v;L|XE9ACPSLuMSnd?j;KY!<_>#-5&pa8EpPXBMe*1FzYP`-0<q3Qtu}s?2`Pw@4pF>-Ru9~M0QHz{|034hX1Mv4s+<gqX=HY|NsAkkh!la7>EJ@V+JT$'), 'z': (15, 14, -2, 5, 11, 'c-muNAO!wHfC>utg#eNYsaxhqJnqvWNIa&E708D5&qL;A?qfybd0Y`h;>mnMvDX648Mpxeke4Hu'), '0': (15, 17, -2, 2, 11,
'c-muNAOu(&9{jkL4(HDM4+4cyp6>sbHtaz^KJh`g4gWz3`~QbQxEub<14;M)Z4mCsKaBOC!`1&UfN(E<V`%ysE%$#VToy>eWzqCD{7*wRS?~V~YoNWK`JwJu0CrU|%#mzO4}adsWFQOx?w2{D'), '1': (15, 17, -2, 2, 11, 'c-muNAOz$}PW^v^;NJNEADO$e*Zj^C6!inbUGN_a=3wXI1^@<&C!z'), '2': (15, 17, -2, 2, 11, 'c-muNAOHl4PP}__BoxM-@E;61q1^gO)<Q!0|NaOgYuWnW0GYeyD-RM+`CBs*Pw47y76ec9{81#OGS`ptB6w;K4kPi5UhU^bGG+zDRsRF9a`6BFe^)Ii'), '3': (15, 17, -2, 2, 11, 'c-muNAOJX`cfNUhESeF@&G-)ny-;raTst9NpSQpHk+m%OuYln22fw??1mkr4|Nn2N3Ih`N|2|D5ox<U7UZEJ3{y!F(oAJLG!dO|P%_$Q0`o9~5dj{gF9Z**)wqN-4=41vd13>@)P%tq*'), '4': (15, 17, -2, 2, 11, 'c-muNAOdLr`fr2aF&=$`%*{SO0f{U9&ZGy4yS|qJi5q;M8;Q&R)Pn(uJ7XyW5?A!!e+c*i=F0p>;X(kiMFhFn0RUucF3J'), '5': (15, 17, -2, 2, 11, 'c-muNAOH;hgFyu@ZUL%dH14erUk>}C8I=a*>dw^TRO<Nui4R%J(*K^w+=Bmc$lQf6*?BqY9P;)5KJr4i2fzmZON1&@o_XW@hg~iVgaH5^nKZu'), '6': (15, 17, -2, 2, 11, 'c-muNAP8LdeE7Or1;$JG_a6whKzU-H|F=qUc=bTJdH-i1>s;|)1DSj5o%n{YZ&oNkxfib-0~z&15W+qA`-B09`mX;)5bmb`W<XN={~`#t?Y}9I)cL;<!nODhRIIk^e*x62wIGxJKj4RQIa=@kdbL=Fu-^coHaQp'),
'7': (15, 17, -2, 2, 11, 'c-muNAOKGMhky!Ht`V}DZ5NPvihuKvxm`bnk$CK{S0PKr{r5nz>@gD(&**;(vgF)<%1AtcuLqDN3;)L<@fdG@;$k2M0028;BA)'), '8': (15, 17, -2, 2, 11, 'c-muNAOw^bJ^X&VR|LwFe)k^)uCYV7rT;f6vguy<?+M}7{&xkEMgIdJT-`tG<=M2)z7~XPb~^{ux>pxwa^4Fd_iiwh7xjOQ3WwqGf2I)buD?7$(&+yr2>0S&UNCnBguCkhIu&;PqyHNqT%+$`S3MJlnx(no!S~zKBnkSB0RWHJJzM'), '9': (15, 17, -2, 2, 11, 'c-muNAOy^JeEfbP8OAgE@gD>Vq1=`KCrNU-z4*if;okbl1SIqS`$D-N7{S~s2zT}WehDtO$NwilxMsgVCe8mp18SDtzAx{m82#@>wmkKJ9ukk`;(t>pbEz4p`uhLpVKQ$(MtwGcaUBnTeYH}PfiM67keN9$'), '.': (15, 7, -2, 12, 11, 'c-muNAPlzrZy}zG3jhFNF$Sg'), ',': (15, 9, -2, 12, 11, 'c-muNAPi>wUx3V=^?x=p_w;{DB%a{k4akx~f3+Ei0RXWU38w'), '-': (15, 10, -2, 9, 11, 'c-muNAP64(|NnmrPA*LV0L1nQBL'), '/': (15, 19, -2, 2, 11, 'c-muNAPVICcR=DX-#d*g8Sy_9nS1sQ6B5tme<rfzu2-B$JcIwW$db#x3L)_n{!Buaocu=ti6{JZ8M0*ke*+{Q=j&a_lG*=VkR5;b90QR601$l{Bm'), ':': (15, 13, -2, 6, 11, 'c-muNAPlzrZy}yb5}=C702qP|O8'), '(': (15, 20, -2, 1, 11,
'c-muNAOdhaXhr5$eH29EalW5~ESdb@6q&o@6*7<c(`IC@;{SeRuG#+@WUlG|T4b&Qs$%9(TTtA%{WS_V@xK`|m-F3Z6zR&3LZ}{WBO(|8^I;ij'), ')': (15, 20, -2, 1, 11, 'c-muNAP6?>N8#%K3qaxTJ&(do`frZRmH6L-BK_bD3U|+U6z<CZyvW>D|9S8zeuQF_B&tOzsLt4b9*-B+A7CH~000c88I}'), "'": (15, 17, -2, 2, 11, 'c-muNAPi#u>rjh3*Z=^X?gyj'), '<': (15, 14, -2, 5, 11, 'c-muNAPR8A9p#5}H2UBDzr_V%vqc>E|8=1qgd@=P>i>x}UYI(I|L^^g%n;~){r_MBH$s3d^5Fl^b8V26XiPwu46!%<7(WAP000Li8%O'), '>': (15, 14, -2, 5, 11, 'c-muNzz<Bf`Z6PN)t>)<TrZ8_v-oZJ{bz#*6GBA1^!opMl`Kela)168fU!mLFaEz@1(9X;Ui0(MMo*|-wP*hyHy}(l-R8&4Ko$T17pNOa'), '&': (15, 17, -2, 2, 11, 'c-muNAOv_OKmPlF1DreWKM)|e_it-4At~N_3`MW||3W05(9tLVf)U*9dpTBoH3k~d4&qt;H)7yC^HhrA16WJZe`y8=>1St*|C@lgh5xgFr1_7pyTDp?{(UQw;`X`sKL=t|FUV2<uOEBL3E?N6{qbg&P}u)+LY@NvpQ<-k'), '*': (15, 17, -2, 2, 11, 'c-muNAPgklAlTk>d4OE0ZAuWX)Y>}%Z$e&8;(^KgKKysV458fT!T<9naC27P2?Q$c<A%!30~sZ~T^XxI^Z@`;q8F|'), '+': (15, 15, -2, 4, 11, 'c-muNAPhqOYmmjY_zwdDSh$p!OacG^OdcLr'), '!': (15, 17, -2, 2, 11,
'c-muNAPg%02T+S!{@)*&oA=)hnH&G#0+}1|UyFfgfZtwR002eK68Q'), '?': (15, 17, -2, 2, 11, 'c-muNAOy5#-~4vFfdj_9^B)9e!nhlg6uCpb{bEDbvH8Cg5>NQWRV1F+#V^JP9@mA>_DGV&{{xZDS@fR^nY-dY3m#|g_%DEmiwgh%A#ol~'), '=': (15, 13, -2, 6, 11, 'c-muNzz;0`!+-!5F75P^003=(B>e'), ';': (15, 15, -2, 6, 11, 'c-muNAPlzrZy}yb5}5IS0Wx>i|Jlgg)Bi1zc!Ga7AWH`Q)h5ac058lCOa'), '"': (15, 17, -2, 2, 11, 'c-muNAOtx6H!!TYLly4e0{|};4>$'), '%': (15, 17, -2, 2, 11, 'c-muNAOJESzG!2C^E}^~$X_XkbLUNDV2C>p=gyzNzz}~C&h>t6D0iiXfk7mN4b0Dd^tw+hamUjcq7ZrB=uJ;%Ix|B!qH7<|b`@Fr{-O(*%j^oYblGO1kS_`_<CwmiGBE5fhH;s{n=ml!D}~#(VzZF{H#Im{aQVmU-h@2I003+`D9Z'), 'É': (15, 20, -2, -1, 11, 'c-muNAOggHwnO4My|cxo(B(e_wBX=2pen}Cg#ZT}T#}5!YVroGTs!~(t4}?t'), 'é': (15, 18, -2, 1, 11, 'c-muNAO<XXri{d^c&&xR^LcBCQy*LPjh`=P3PO3zJO6{g88!$v_5VI&4!ODi6CvEaUwJ`lKCXapAODAd!>HU75bpj*jL7z6{9kU!E#kN!8p37S4N;r|b4K~4@2~eKa1it-0Esy`+5'), 'æ': (15, 14, -2, 5, 11,
'c-muNAOPYne3{EW<;&9)Fi+q=5F7;JKe8Y${~`r}MgM1W`}~iGsW<uW!ocvR4$KZe_w_#*bb@$x|NcWk4~X0I!HUcIza329lsD>}6aUW>5=r$3al=6B>On*dh|Adg>_aU>&huAOxd}NK0QG@CU;'), 'ø': (15, 16, -2, 4, 11, 'c-muNAQE^mL1^iPFMpnMGyNz7=JDVE4+Os-<U=G&{+}`AcKh*z6T;p6Uz34t?dAVb5bp7h44m8NDE;q*aJPQqJus0`<^Mbgx8wiSHU@_1|6LHS`TwW7Tn>-^dqKF%PJt}?e*oeN_eXpQw|_nC<Az8oS`q6D1^^=gHC+'), 'å': (15, 20, -2, -1, 11, 'c-muNAPAHXe_G3r;2vz`TRs`V{i?*^eFDKfRL{G73WBS8^z(WFTn0O@ef<4OAv2UG^B)XgMoaJV7346v@>3XDN8*16C@W~+yMI8{J`i3kMDPCqs1rX02s1IH!?|xQ*aU-~!MOP#mH(!~xQu1Dzh4OsfN}8v05*L-u>'), 'Ä': (15, 20, -2, -1, 11, 'c-muNAOuYQ&tN$4p92RM16=sO9Em6Y|J?^x1UK)0{(n~lckfNEA5-8wf#3ZMJ0HQh(Lj|2|BYbWRbSW`)c!X@d2F9H0?9iUpj?mt5TF3zPKR>yz&ysM?^uA8^8dYHuIc}U5QqL21W_&j1Hjzc|1pF@0sygxI&J'), 'Ö': (15, 20, -2, -1, 11, 'c-muNAOuYQ&tN$4p92RM4e(BQ^7D2T3zWxn=syU|fO3QX-!^1-dG}8X!d>>?2S}FwuYqu{{^tgg#{XACxNqNrNU{G%Al$D{K_uV*vsh&zdW~Rum;d($k|i*c!~WkiU~_s4vzO^8imMp-Cq4ajr<#ReKrjFRJSjg='), 'Ü': (15, 20, -2, -1, 11,
'c-muNAOuYQ&tN$4p92RM6>Rx00witzchH)<8Om*kaM%481(LS^8zJ1;|22VR$o~QeH{<_dZEmaE|7{^$p4<OHU=PgE;&Wd7e$c^5Fd!HJC)+vB'), 'ä': (15, 18, -2, 1, 11, 'c-muNAOuYQ&tN$4p92RMKX6|A`1_SYW++eQKNw7ga;10q3UZiS`6-O7Bk{ijlohn^-9Mme9|$iNqW6CQgnRH)fG`t7I-L8~f=w{!8H}3`Qu%KxjLTSd`}>vP02mh!001$SIcN'), 'ö': (15, 18, -2, 1, 11, 'c-muNAOuYQ&tN$4p92RMKM<br?AN^(HYkt%;(riW1LY?FKWE6}^yI%KguCLuA&`vuUkBkH{mBR<RsPRG<<3S{91T;P{Qryrx5FctQBaH4!ki&8^ZBp)t?Y!|3joT7Gx`'), 'ü': (15, 18, -2, 1, 11, 'c-muNAOuYQ&tN$4p92RMFYx#u0wh!Z+fdGR{~rn@3t(K^|AjzuF^ntm|F$+?;#U}#;n4s8|9?+|a~1agxD^OD3J(AP|BEgF'), 'ß': (15, 18, -2, 1, 11, 'c-muNAOr-a-u-zyAI?4U9|U5cJnjEy)j90no`-S+|Hm;fNbdd02;oNj_hD##k+07H=UV;`g_{KAI{)uuMB*||`gdFf!DV1DKK;=MiOaxo?i@0gVak7Q7<ZX5r|pYx%rNc`kSk}x75kq3daIs;pkD!JQ#&6'), '·': (15, 12, -2, 7, 11, 'c-muNAPlzrZy}yb2LJ$5@dl;'), '–': (15, 10, -2, 9, 11, 'c-muNzz_bz!3`{2S^)s+UKO1'), '—': (15, 10, -2, 9, 11, 'c-muNzz_bz!3`{2S^)s+UKO1')}, 'SM14': {' ': (0, 0, 0, 0, 8, ''), 'A': (13, 14, -2, 1, 8,
'c-muNzza_PH-@t%|DI@ub285*T!wRYHj4gLhO+s78Z#U(hH@gGGBQ*hhH_T^2ZFz1U^d%FA0YW48O-tgD*z-HZU%E^oClE!-+Ayk3jloM8`u'), 'B': (12, 14, -2, 1, 8, 'c-muNzzOdB|NrG&2$bEzz?t?}55{I-|DOP3a~1s3gsK1kB^IupJLIbaTs_04RS5Q)O>i?kzGlGme!W_R+bs+Lwl5=U'), 'C': (12, 14, -2, 1, 8, 'c-muNzzwuEeSFc+31%w1pQ9j9;ss{UyMR#gtQF2=`JV}Av;NP(s)k|yc?4VO!z?-R0*ILmI$J-%?7|8F#7`7o'), 'D': (12, 14, -2, 1, 8, 'c-muNzy$>U|NnNWj2X%f;c~vS2*ze$aQUwdXS4p!g|iu6wIkRsJK$^<BsI=(y_}A>7Q^iNez}~50XF~uitZod'), 'E': (12, 14, -2, 1, 8, 'c-muNzzJ6T2Z0O-dk>O0E;d-b3GwPN^mgEO3;<1`8_E'), 'F': (12, 14, -2, 1, 8, 'c-muNzzH(`gTNdJ`wx;hE;d-b4)N-7u(1LForD&z'), 'G': (12, 14, -2, 1, 8, 'c-muNzzw`ke7jr53}*WM%o9<r*9S2fZ_kFSQ2Xx<XS@72fU{lyYcM$c|K9^q;|wH^fZ2@qy5VewkRNG+(l;P%hJZ6ao-9_t?G^xQ2O9V'), 'H': (12, 14, -2, 1, 8, 'c-muNzy$>UhXBbZ4aBp-pn*KS2sU;A0C)x;iU'), 'I': (12, 14, -2, 1, 8, 'c-muNzzG)o2LT=^ujU0phWcz&yRZNNWPuiM'), 'J': (12, 14, -2, 1, 8, 'c-muNzzs_N|Nq~C;NBpW-Hu@2Z2(gy8Vn4~-%`PBhewV)rN8CDY}T@CUoZONaS8(fcZw8J'), 'K': (13, 14, -2, 1, 8,
'c-muNzzqcchcGbko!rX_<8U82$OV((+;@}*rYw5LNj|uqXa6T747d>W&jrb}`Huw<9DyfGk?isQABNyCEPN}8$6*WrCSM-%'), 'L': (12, 14, -2, 1, 8, 'c-muNzzI6;(2@Ng1Ww>~3;;nj63_'), 'M': (12, 14, -2, 1, 8, 'c-muNzy&h?&u3t;_<se=e)f!;Vfsx7`_8;r_NUEIw*8*a6(vwM<DD~}Fg8QOb7nXj2#9B62LSg2BtH'), 'N': (12, 14, -2, 1, 8, 'c-muNzy)~zKVe~DxKjgR{|!d4H||5QLq2N3*&dUpAlMoodEsn^Jy{5L;1vX$`OzOZo1yA|4Nk`}001O%B;N'), 'O': (12, 14, -2, 1, 8, 'c-muNzzLW-UVh)F0by6awGvx)pB>D8(#*gh{yzZ3l>8q8B%ii`*n0n+f#j80Ah!O0ClGrkh%JSrhT&NgNN*sRUHisLblC%lnao|UejL!k?G^?A@Hrke'), 'P': (12, 14, -2, 1, 8, 'c-muNzzJ6T|NrB95tO}$fiv<?I*iT0uyZSdy?Yys%@O@K3$FKOIU_<10|U`)tN;L0^&4d'), 'Q': (12, 16, -2, 1, 8, 'c-muNzzLW-UVh)F0by6awGvx)pB>D8(#*gh{yzZ3l>8q8B%ii`*n0n+f#j8$Ah!O0ClGr&h%JSrhT&-wNUtB5UHisLblE))Fq^sS)&GxLaI3XH*C5;xyqpQQBLOR(Ao~'), 'R': (13, 14, -2, 1, 8, 'c-muNzztab|NsATy&8-Y!yv!s4m+H~VDsM?!Lj;p4d+O1zRn6a;QwA>xB-kt&#MroF@%4YM{pR=FF<e@eE(|UaTo&tGnOE='), 'S': (12, 14, -2, 1, 8,
'c-muNzzMi}9)8?u4Ph@juE}G!8q8$+8i-KyZXzR`9slFuf-qJnM=ER8=hK{UIr*;%2u=42z|<N~5&ptox?r}&rq>^jdE<5q0|3&^7#;'), 'T': (13, 14, -2, 1, 8, 'c-muNzzx>?hX5HUzv2y&B)vFT0RXy?6h;'), 'U': (12, 14, -2, 1, 8, 'c-muNzzP1R0Er(t6tn+;+38^Rn`{OK=D(p}_VSCW0`=b|!EFAi&%PY7!R;0X07a=B&;'), 'V': (13, 14, -2, 1, 8, 'c-muNzzxdYGXu%?Ct!}&e+wXaW(Gv+ZY=|Y@Lz8TXX0T7hOn=k5RU6_UWVBlp(e0>@?&_A3NvrbWYvF?Fi!l<tkZCtME{<xL)d%lzYzm|003ww8CC'), 'W': (13, 14, -2, 1, 8, 'c-muNzzyD{fk?)m5g_VlD~Oc(ZwR91Edh}h|G7a_`C*2Ie|W+kgY^VFVz_nBxnvKRqxnbTWo_-`X<!cP@0_*vJ2vJ+%)WIbpX2344+v-TKSPEi{}dsdo)1h6?LU|p@BsioL?em'), 'X': (13, 14, -2, 1, 8, 'c-muNzzvkX#RJK$`x(K!@)vvzf!|ahQY;tyxgM6n6k7aTb($HjZSj9|I9uTPhgLXe?kVdZnozd$Z$pN~2Ow;&yFCmHQeWc1oZbiAK(gwU5FUpy005S(8rl'), 'Y': (13, 14, -2, 1, 8, 'c-muNzzs^@3IWL(H`zcO*6R})7_|O)K%`uMsWWWf08_Ybv+H+77)Sowi$;VQ6FzYwI5jUANakP#0Bfui>i'), 'Z': (12, 14, -2, 1, 8, 'c-muNzzI(L2Z0-KzWnD-ID6+c4j41>j~R?9`Mw>lV*M3%7&GjT35+THvK6jk$z?V;`vcgnKe!zO0C=Gp<p'), 'a': (12, 12, -2, 3, 8,
'c-muNzzIYqJ^psU0KzWL7UJ)H%!-ivuMeh`*S`Gs|GzbueQ|{>qriU~5R?1AIRk?ugw61H0=Mo-DBJ4%kE?!AHdX)t<enMB'), 'b': (12, 15, -2, 0, 8, 'c-muNzzH@?A%eYd^N*XZQ1-ug{<_bC5cUZM2IiMp5cYf^aikZC-HlN5A_JzEulkb!%*>xRTyeXL0RV(_9u5'), 'c': (12, 12, -2, 3, 8, 'c-muNzzx(ketgl(24-?US}ZG?X#r;EykLhbnYo<-D?8^U2b|6Qc&V&Nss+@{O`l%0v*NZB0J>@ro&'), 'd': (12, 15, -2, 0, 8, 'c-muNzzbCVE8u1GEc^O62g;s!RY~bGgw6ORj)5Tx!j}AR&cI**VN3isgR>bw$HLVxOt`EF)62lK{M(~!B)c#G0A;it_y'), 'e': (12, 12, -2, 3, 8, 'c-muNzzquSeLL$4VP@Pl;|l+#0%kvt022EvK}^yAfByXa_kSjYZI00Tq7cE(dh5rdJ;4*g$-VjWY9SkLI{_007)J'), 'f': (12, 15, -2, 0, 8, 'c-muNzyk!gef{qOWmjGnfQ!#r3S+JL4+1bX3zi`CQj3iR000Vk6l4'), 'g': (12, 15, -2, 3, 8, 'c-muNzzMjPetT5%UjfYSxv4IH0m5edl*GUg31Lh8H)milfUqTz*vM)a`fh5-oq@8smw$U$@Lw8khr=%>Fzs9^DYa`EM2x-d`HKZYxZTA7021{e&H'), 'h': (12, 15, -2, 0, 8, 'c-muNzzNpOAcDPM!IuZVQ1<r_o~{=x5cVDh2Ic?q5cX^a29f{zaJ?e`4TxrA1pw(&8le'), 'i': (12, 15, -2, 0, 8, 'c-muNzymyfU}qzM!~g$32&*TJed0d|RN!_N0JP#0as'), 'j': (12, 18, -2, 0, 8,
'c-muNzz3ehU}wXD!2kdMV+gCKg#9KE&UF8)2xaa0|1ux1%K;sQ6kh'), 'k': (13, 15, -2, 0, 8, 'c-muNzynfV5Y6%Z=nm)jz}P^JH=NCo^7HFQ1vuxI<IY1&2m_?wS0I@d^UDy)o;6oF@VOEIidGv+'), 'l': (12, 15, -2, 0, 8, 'c-muNzzJUb|DS;1J)r^nRyu;cVhbmnt#IV`e*xSM0{~P<5w`'), 'm': (12, 12, -2, 3, 8, 'c-muNzy%!M?0J=U<%uDf{ZDP;cey#U!R*%z(bpNWcY)bY7(y;Eq#Q<KA0d{F9RL936doJ'), 'n': (12, 12, -2, 3, 8, 'c-muNzzNnYSn%b6FO>Z~gs1BT3xvIgfkFAdJcK=)fkEWIK7>63#5N$BjTHa@(|s1z'), 'o': (12, 12, -2, 3, 8, 'c-muNzzJBoU;a3#3t^W$GZk5QpB2o$Tgkv6^2Z0P<c~j)d{Tg5Kh1}$5r(K?D0^xwJpTbiFKh4XpNI8v+sOa`vYi*b'), 'p': (12, 15, -2, 3, 8, 'c-muNzzMd@+xFv{J(T@7hQIkO4}^V$fr0g1JcK<PNStX#Vz(lxNrLNb{J;lc&)@O$x)apQ2}pL~U}FUU!}%Tu'), 'q': (12, 15, -2, 3, 8, 'c-muNzzJBVeR`4l-vZ1od!#FQ5X!z&#=zhJVKe{nXJC+kuvz~4!PyM=O5ti4svqh|?uWA3W_^B<3}u4=4-sq(005qV9qR'), 'r': (12, 12, -2, 3, 8, 'c-muNzzsT%&VK#>36%YRz6@Oa6&pg$Atd#CNMmCI0Ob!3%K'), 's': (12, 12, -2, 3, 8, 'c-muNzzG;zpM2V)0%3>0)#r9^g0Rc4BGjn9I^E>P1m*CBO!~MCAs6z88BCXDO9{@q0ud9P^7O+F4cvAz003LQ6D9'), 't': (12, 14, -2, 1,
8, 'c-muNzzqccn_ywf{09R8d}?sBx&B)qEO^$!24@G}`2#Z(8vp>DtrMa'), 'u': (12, 12, -2, 3, 8, 'c-muNzzNpOU|<mWZ$LDAHIOY1WzSj0z+eGoXTH%A+XQ8EuKaR47Rts701xFB(f'), 'v': (12, 12, -2, 3, 8, 'c-muNzy(zQs{zT~lfj&G)eH>6ziq(m@(T<MDNh)|Y=!@-3_JRuI!;yz{xXNMi_RxLfSDxo?@A}!*dzaq8SnrAv1Ajv'), 'w': (13, 12, -2, 3, 8, 'c-muNzzrTpfvH!1AaYedh*bD52BHd&FqGbB2)hH8H~+@6^@&3FVlap8yV32M!~<Cn6OPPWZn5-}A%xTYJ%#z@7ZwO7@V_F%rUMLk0RS*$8+i'), 'x': (12, 12, -2, 3, 8, 'c-muNzy&xicQP=jfAs`&bidlOoSq1k$$dEC5(iA#&ObUZrr@I=$uRbs9X?;wAk4Hkk_<D>vVoYIUjrE!xNmjiw3Gn=;B*x6'), 'y': (12, 15, -2, 3, 8, 'c-muNzy+lLS^~*M8^D~M(-;`IJ_mx?QE%B8B7qnLI6nq3Y@GttF?+4ZZ&N7S`bX_`xKX!%RlwObe`Vq9?mcj(+WRmVbI<o_j12ey05uvIUj'), 'z': (12, 12, -2, 3, 8, 'c-muNzzItJgMbX2KkFJhj2Zn^8^+Z95(i^)U!4P2yyzk)jG6dJ4K6$f%}fjc0H(1N9R'), '0': (12, 14, -2, 1, 8, 'c-muNzzr&&ecLJxVa9)VliGV6!agyBfkFSj5s1nBGns*b@q0RmE%e_XNIt0rv4#KpmtEn6u#wd;oSe?Up!eSxV&*p&$vwwmc0K>TO$Lu!00@B|kN'), '1': (12, 14, -2, 1, 8, 'c-muNzzJBRPW_L8vb~m>!`VPUb+*QT5U9cJ7yu-c6e9'), '2': (12, 14, -2, 1,
8, 'c-muNzzIyZynDVt9Kv23AS{3Q7(&kfza*TU{aX;m<i0f*#$;N3fd|H(ejBd3?SUMOS@~2MZpN4YAYg;rF#sE-7Sa'), '3': (12, 14, -2, 1, 8, 'c-muNzzI|qyn3}p3BsNpDlEC~CPL2hzc`F3yYU<ogyr-9{{;z{Fr&iybF6UnBL6+%Y|;N-Ac}vZHIL%jC;VVB@BJTMuGhfr76t%-zZVn'), '4': (12, 14, -2, 1, 8, 'c-muNzz4ejXTX?_$9}@t0=G1Oz}U;n8DQ+#Q_L{7%qwjM7~AJR7#x8c3fGH=jR636w;7Q'), '5': (12, 14, -2, 1, 8, 'c-muNzzL@O2ZAY3_8KH{WcKH8Pi6{0*d^{f=GS*1<lO$N!P&C^UEyq(|0*Dgd7~M((dEq$vEb8R?oZ&u?G^?AYrYt('), '6': (12, 14, -2, 1, 8, 'c-muNzzy6^eZOi2VOsqv;Z^B`u(z#-t6=&P4QC7f&%5~TQXrTu{QsT_cm8iJ5S!(91CV@~50*FwV!z4*vooIp)%?@|vl;82emn1t$1MQzQXFI'), '7': (12, 14, -2, 1, 8, 'c-muNzy)~zgF!f4Ao?pGoPA&coT>KT7S8Uz31_mtDuc7beoMgFyEnj@ivN7z?AE8u4EO*5K1UMs'), '8': (12, 14, -2, 1, 8, 'c-muNzzGEAz4&s<4Z>b<LzTPby9AhhzK?-H{=Yq#U3OiWtMN7$n9Vrr|NjR%5cN|psPi?w0;^~L69bfcUkGAz{{yp2!D{wgP~)xr3DF?F@cEaM9=P4Y003};AHo'), '9': (12, 14, -2, 1, 8, 'c-muNzzL*Rz5cRM2EsmYNLF~sDKL}gpC1E*%zpz2+lPTc_J1N+;^01M;Uz!Iz--xd@7~m0D}kHE{3Qy`cKZu4G&qdM?A|Ph82^&bkK0&ryM+M&z4jbh'), '.': (12, 6, -2,
9, 8, 'c-muNzyntN7r@HK0swsQ18)'), ',': (12, 8, -2, 9, 8, 'c-muNzyl`y*MPI<{1St+Z%>0W<-SYdGl2mBF6{;c'), '-': (12, 8, -2, 7, 8, 'c-muNzzrt+|NozXLI42k+5?U'), '/': (12, 16, -2, 1, 8, 'c-muNzzfv>sKePaHp7`B-yGoVx^r+Q`-^BeJNYpyoPDJX&h+>!0B7%>0B7p`QG~M>tcEise_G;q9|Hi`JP(2'), ':': (12, 11, -2, 4, 8, 'c-muNzyntN7r@FU29Tf^0LQBa-2'), '(': (12, 16, -2, 0, 8, 'c-muNzy~6Z!<lT4T;c4P`;2h**2xIv9~0nA-v6F(Hs5~_tZGp7#@u5>vdax25q=z>3jv*q4(t'), ')': (12, 16, -2, 0, 8, 'c-muNzzt##BG^pVgAtsPBM7#}e>nu_V>E(&s{$*V@nZ~}t^Qvg&MrHKu<K?B!VQNQ@B#pm;11O'), "'": (12, 14, -2, 1, 8, 'c-muNzyngwkjADV002Bz1i='), '<': (12, 12, -2, 3, 8, 'c-muNzzamnHb7bS%YGb>0x|dtuD|Hfgb1emU&sYh%3pZ>Wv@0|r^E7}Cu0!ily6`l3IG5D(hzh'), '>': (12, 12, -2, 3, 8, 'c-muNzy+cgTf^B(b3R|r;fL|K6OVkEYYdn4e}4tS;7LCEb)E@`r9A)3m0YO$m?bt0!~*~gT@ZW'), '&': (13, 14, -2, 1, 8, 'c-muNzz5o2{{I1EyMEL|Ncg{ELU1^q6(Tq_&wg0K*mmz_8y|}>Jl6zqdY3RTZr#cLlLN%5Kg_@&aOe1Lurie|&7vaH|0hB;neYGfczW#%QGD(K0BR>4x&'), '*': (12, 14, -2, 1, 8,
'c-muNzyoyVz*rM9_2y`8mjts}vQ9i+pa>CX$vp9Rz5-NDmfjp~s2XIwQ~>~F9Spt'), '+': (12, 12, -2, 3, 8, 'c-muNzyo4V5MZbL2ZJlbswWHpOc4$X'), '!': (12, 14, -2, 1, 8, 'c-muNzym7Y5N4OZMzHhlBiONL83+PgW?}&V(;*7Z'), '?': (12, 14, -2, 1, 8, 'c-muNzzNu^ZhSpy31NG;C<!io#RQj&_`?ljO5dCTXFiz03}ZK+LYOpv4R#yW?7+^(0s!;c55)'), '=': (12, 11, -2, 4, 8, 'c-muNzy(tNgTWOBJb)NAgaH7(vJPb'), ';': (12, 13, -2, 4, 8, 'c-muNzyntN7r@FU22A*`0cX$oB?f2To(5;ieV4*(1OUtU333'), '"': (12, 14, -2, 1, 8, 'c-muNzzsGui2PR|flW&Q0DTAvjQ'), '%': (13, 14, -2, 1, 8, 'c-muNzzvj-e_qQC<E+Z#no$nptj^(_Udg~94psJLJ&(++UYMjn$5M4Dlf8JOB}`a<hd)Eoi)Zm*4kt5%&@*Mlhhk7k;b)5Sk0oGA(_X$zW55Rh%$gX8'), 'É': (12, 18, -2, -3, 8, 'c-muNzz60}hcmrSurc5VEB=E(286u_NgNj&tlorp^%#0Pa61M7?HL{z'), 'é': (12, 16, -2, -1, 8, 'c-muNzz1aB+r!zL>fy|=15DUd7u@@H))m6cxNF80{!InUejWiN_E&<KqW}N=`TOtxObFW?q4h-}f}Qo&k4JlgCxnxG^XJt<Hry@*04z2e+5'), 'æ': (13, 12, -2, 3, 8, 'c-muNzzsNNz1tf6;$=FRW1qmY;E%TbcMhne+dT$`PZ}T=@3Qy*LBJTqY1%98eHCWF`T~aV7ckC*4ZI8f2Mg76gE%tBzV8fq__m4x9{>QbQ6F#'), 'ø':
(13, 14, -2, 2, 8, 'c-muNAP9^h6ifHZ&wDzTLpUW*O@z1p=7VtVlrU&s`Rxy8GynDyykPjC2+U#q=eHxA;b}fZ*`xa{48niBA)KW@OoZm&X92Ta4z@o1aYzp$p(#YzMGOGw*&cQ'), 'å': (12, 17, -2, -2, 8, 'c-muNzzw8Ny-R_y`_iTEvBB7B5_e&2>C*@`NI+!L<8KEHAnf97A^zUStO&XP`e0gl?aP1v|67CE7gxwK3jDVLF}eSnGcY(p*bI*+aO<9gvaQblxatRGV+8>C@*)%'), 'Ä': (13, 17, -2, -2, 8, 'c-muNzy~f&Q2B4eKp33-ZwzNk{yotQ=VYEsxD4m)Y!v;g3}y5EG-fzn4CO>VWn`#24CSo+4+MY3z-+dUK0xw8GMMA}R{%&Z+zjT-I1eHdzVqO77663g9+v'), 'Ö': (12, 17, -2, -2, 8, 'c-muNzzr@;Q2B4efEO@zy!^gT1H!I;YbCbqK0BEGq?v(1{C@z5DfvGHNIq==vGx8t1Ia71Ky3a0P9XM75L*gK4a2i0klsKryY`Kh=&}b8Gnu<y{Wze7$1woU1|ak'), 'Ü': (12, 17, -2, -2, 8, 'c-muNzzr@;Q2B4efEWBv0TMrQC}#fwv(v%sH`xpf%zs0{?By3#1?s;`g4z62pM5!k&piMnb{~%'), 'ä': (12, 15, -2, 0, 8, 'c-muNzzr@;Q2B4efES2Ndi?Ex0fb$gEyUmZm=z)SUmr{>uYLLN|9@*R`{D{&MgfSS-2crP7#yJ%Jf6U<dlJgFI{)LUA3lo#frA`^'), 'ö': (12, 15, -2, 0, 8, 'c-muNzzr@;Q2B4efETcIzx;7f7s4)iW-7AqJ}a1gw~~QD<c|+n$sd0p`J@2Bewq(gBMec)Q1;YVc>V*3Ue?~%KM(8Uu@nGLf*O1'), 'ü': (12, 15, -2, 0, 8,
'c-muNzzr@;Q2B4efETQp!N4H$-+*ZLY9L!2%AT`~fx!aG&U~XKwh7AST>0g8ER>BE006AJ8Ib'), 'ß': (12, 15, -2, 0, 8, 'c-muNzzJ9<Jo~s+7Q)VXsm;G~Glacj9s^_UR|tE@1m+#fO&OtV&zDRLF!6vN3UD^t{x`ueHUn$b&tw>zfuZXhoGr3#Bb0sT|A)=8xE%%nbMGOP'), '·': (12, 10, -2, 5, 8, 'c-muNzyntN7r@G<0ssIZ&jW7'), '–': (13, 8, -2, 7, 8, 'c-muNzzzOGK@J1u003U{2xR'), '—': (13, 8, -2, 7, 8, 'c-muNzzzOGK@J1u003U{2xR')}}
)

# ---------------------------------------------------------------------------
# colours
# ---------------------------------------------------------------------------

DESK = (30, 36, 44)
DESK_DARK = (22, 27, 33)
PAGE = (243, 237, 220)
PAGE_EDGE = (226, 218, 198)
INK = (29, 47, 74)
INK_SOFT = (84, 96, 116)
MAROON = (122, 31, 43)
GOLD = (176, 141, 60)
GOLD_LIGHT = (203, 172, 96)
GUILLOCHE = (213, 221, 231)
PHOTO_BG = (196, 206, 214)
PHOTO_BG2 = (178, 190, 200)
VISA_BG = (219, 231, 224)
VISA_LINE = (52, 96, 84)
STAMP_BLUE = (42, 77, 143)
STAMP_PURPLE = (91, 58, 140)
STAMP_RED = (163, 51, 39)
STAMP_TEAL = (31, 111, 106)

W, H = 1024, 1024


# ---------------------------------------------------------------------------
# canvas
# ---------------------------------------------------------------------------

class Img:
    """RGB image with per-pixel alpha-blended drawing."""

    def __init__(self, w, h, fill=(255, 255, 255)):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        r, g, b = fill
        for i in range(0, w * h * 3, 3):
            self.buf[i] = r
            self.buf[i + 1] = g
            self.buf[i + 2] = b

    def set(self, x, y, rgb):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = rgb[0]
            self.buf[i + 1] = rgb[1]
            self.buf[i + 2] = rgb[2]

    def blend(self, x, y, rgb, a):
        """Blend rgb over the pixel with alpha a (0..255)."""
        if a <= 0 or not (0 <= x < self.w and 0 <= y < self.h):
            return
        if a >= 255:
            self.set(x, y, rgb)
            return
        i = (y * self.w + x) * 3
        inv = 255 - a
        self.buf[i] = (rgb[0] * a + self.buf[i] * inv) // 255
        self.buf[i + 1] = (rgb[1] * a + self.buf[i + 1] * inv) // 255
        self.buf[i + 2] = (rgb[2] * a + self.buf[i + 2] * inv) // 255

    def rect(self, x0, y0, x1, y1, rgb, alpha=255):
        for y in range(max(0, y0), min(self.h, y1)):
            for x in range(max(0, x0), min(self.w, x1)):
                self.blend(x, y, rgb, alpha)

    def hline(self, x0, x1, y, rgb, alpha=255):
        for x in range(max(0, x0), min(self.w, x1)):
            self.blend(x, y, rgb, alpha)

    def vline(self, x, y0, y1, rgb, alpha=255):
        for y in range(max(0, y0), min(self.h, y1)):
            self.blend(x, y, rgb, alpha)

    def line(self, x0, y0, x1, y1, rgb, alpha=255):
        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        for s in range(steps + 1):
            x = x0 + dx * s // steps
            y = y0 + dy * s // steps
            self.blend(x, y, rgb, alpha)

    def thick_line(self, x0, y0, x1, y1, width, rgb, alpha=255):
        dx = x1 - x0
        dy = y1 - y0
        length = math.hypot(dx, dy) or 1.0
        nx = -dy / length * width / 2.0
        ny = dx / length * width / 2.0
        poly = [
            (x0 + nx, y0 + ny), (x1 + nx, y1 + ny),
            (x1 - nx, y1 - ny), (x0 - nx, y0 - ny),
        ]
        self.poly_fill(poly, rgb, alpha)

    def poly_fill(self, pts, rgb, alpha=255):
        """Scanline fill of a polygon (list of (x, y) floats)."""
        if not pts:
            return
        ys = [p[1] for p in pts]
        y_min = max(0, int(math.floor(min(ys))))
        y_max = min(self.h - 1, int(math.ceil(max(ys))))
        n = len(pts)
        for y in range(y_min, y_max + 1):
            xs = []
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                xa = max(0, int(math.ceil(xs[k])))
                xb = min(self.w - 1, int(math.floor(xs[k + 1])))
                for x in range(xa, xb + 1):
                    self.blend(x, y, rgb, alpha)

    def circle_fill(self, cx, cy, r, rgb, alpha=255):
        r2 = r * r
        for y in range(max(0, int(cy - r)), min(self.h, int(cy + r) + 1)):
            dy = y - cy
            dx = int(math.sqrt(max(0, r2 - dy * dy)))
            for x in range(max(0, int(cx - dx)), min(self.w, int(cx + dx) + 1)):
                self.blend(x, y, rgb, alpha)

    def ring(self, cx, cy, r, width, rgb, alpha=255):
        for y in range(max(0, int(cy - r - 1)), min(self.h, int(cy + r) + 2)):
            for x in range(max(0, int(cx - r - 1)), min(self.w, int(cx + r) + 2)):
                d = math.hypot(x - cx, y - cy)
                if r - width <= d <= r:
                    self.blend(x, y, rgb, alpha)

    def ellipse_fill(self, cx, cy, rx, ry, rgb, alpha=255):
        for y in range(max(0, int(cy - ry)), min(self.h, int(cy + ry) + 1)):
            t = (y - cy) / ry
            dx = int(rx * math.sqrt(max(0.0, 1.0 - t * t)))
            for x in range(max(0, int(cx - dx)), min(self.w, int(cx + dx) + 1)):
                self.blend(x, y, rgb, alpha)

    def sine_band(self, x0, x1, y_base, amp, period, phase, rgb, alpha=255):
        for x in range(max(0, x0), min(self.w, x1)):
            y = int(y_base + amp * math.sin(2 * math.pi * (x - x0) / period + phase))
            self.blend(x, y, rgb, alpha)

    def to_png(self):
        raw = bytearray()
        for y in range(self.h):
            raw.append(0)
            raw += self.buf[y * self.w * 3:(y + 1) * self.w * 3]
        comp = zlib.compress(bytes(raw), 9)

        def chunk(kind, data):
            out = struct.pack(">I", len(data)) + kind + data
            out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
            return out

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp)
            + chunk(b"IEND", b"")
        )


# ---------------------------------------------------------------------------
# text from the embedded bitmap fonts
# ---------------------------------------------------------------------------

_GLYPH_CACHE = {}


def _glyph(font, ch):
    key = (font, ch)
    g = _GLYPH_CACHE.get(key)
    if g is not None:
        return g
    entry = FONT.get(font, {}).get(ch)
    if entry is None:
        entry = FONT[font]["?"]
    w, h, xoff, yoff, adv, enc = entry
    if w and h:
        raw = zlib.decompress(base64.b85decode(enc.encode("ascii")))
    else:
        raw = b""
    g = (w, h, xoff, yoff, adv, raw)
    _GLYPH_CACHE[key] = g
    return g


def text_width(font, s, tracking=0):
    total = 0
    for ch in s:
        total += _glyph(font, ch)[4] + tracking
    return total - tracking if s else 0


def draw_text(img, font, x, y, s, rgb, align="l", tracking=0, alpha=255):
    """Draw s with its ascender line at y. align: l/c/r around x."""
    w = text_width(font, s, tracking)
    if align == "c":
        x -= w // 2
    elif align == "r":
        x -= w
    px = x
    for ch in s:
        gw, gh, xoff, yoff, adv, raw = _glyph(font, ch)
        if gw and gh:
            for gy in range(gh):
                row = raw[gy * gw:(gy + 1) * gw]
                for gx in range(gw):
                    a = row[gx]
                    if a:
                        img.blend(px + xoff + gx, y + yoff + gy, rgb,
                                  a * alpha // 255)
        px += adv + tracking
    return px


def draw_text_wrap(img, font, x, y, width, s, rgb, leading, alpha=255):
    """Greedy word wrap; returns the y after the last line."""
    words = s.split(" ")
    line = ""
    cy = y
    for word in words:
        trial = (line + " " + word).strip()
        if text_width(font, trial) <= width or not line:
            line = trial
        else:
            draw_text(img, font, x, cy, line, rgb, alpha=alpha)
            cy += leading
            line = word
    if line:
        draw_text(img, font, x, cy, line, rgb, alpha=alpha)
        cy += leading
    return cy


# ---------------------------------------------------------------------------
# stamps (drawn on a sprite, rotated, blitted)
# ---------------------------------------------------------------------------

class Sprite:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.rgb = bytearray(w * h * 3)
        self.a = bytearray(w * h)

    def set(self, x, y, rgb, alpha):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.rgb[i] = rgb[0]
            self.rgb[i + 1] = rgb[1]
            self.rgb[i + 2] = rgb[2]
            self.a[y * self.w + x] = alpha

    def blend(self, x, y, rgb, alpha):
        if alpha <= 0 or not (0 <= x < self.w and 0 <= y < self.h):
            return
        i = y * self.w + x
        old = self.a[i]
        na = min(255, old + alpha)
        if old == 0:
            j = i * 3
            self.rgb[j] = rgb[0]
            self.rgb[j + 1] = rgb[1]
            self.rgb[j + 2] = rgb[2]
        self.a[i] = na

    def line(self, x0, y0, x1, y1, rgb, alpha=200):
        dx, dy = x1 - x0, y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        for s in range(steps + 1):
            self.blend(x0 + dx * s // steps, y0 + dy * s // steps, rgb, alpha)

    def text(self, font, x, y, s, rgb, align="c", alpha=210):
        w = text_width(font, s)
        if align == "c":
            x -= w // 2
        elif align == "r":
            x -= w
        px = x
        for ch in s:
            gw, gh, xoff, yoff, adv, raw = _glyph(font, ch)
            if gw and gh:
                for gy in range(gh):
                    row = raw[gy * gw:(gy + 1) * gw]
                    for gx in range(gw):
                        a = row[gx]
                        if a:
                            self.blend(px + xoff + gx, y + yoff + gy, rgb,
                                       a * alpha // 255)
            px += adv


def rotate_sprite(sp, angle_deg):
    """Nearest-neighbour rotation; returns a new Sprite."""
    ang = math.radians(angle_deg)
    ca, sa = math.cos(ang), math.sin(ang)
    w, h = sp.w, sp.h
    corners = [(0, 0), (w, 0), (0, h), (w, h)]
    rot = [(x * ca - y * sa, x * sa + y * ca) for x, y in corners]
    minx = min(p[0] for p in rot)
    maxx = max(p[0] for p in rot)
    miny = min(p[1] for p in rot)
    maxy = max(p[1] for p in rot)
    nw = int(math.ceil(maxx - minx)) + 1
    nh = int(math.ceil(maxy - miny)) + 1
    out = Sprite(nw, nh)
    cx, cy = w / 2.0, h / 2.0
    ncx, ncy = nw / 2.0, nh / 2.0
    for y in range(nh):
        for x in range(nw):
            dx = x - ncx
            dy = y - ncy
            sx = int(dx * ca + dy * sa + cx)
            sy = int(-dx * sa + dy * ca + cy)
            if 0 <= sx < w and 0 <= sy < h:
                a = sp.a[sy * w + sx]
                if a:
                    j = (sy * w + sx) * 3
                    out.set(x, y, (sp.rgb[j], sp.rgb[j + 1], sp.rgb[j + 2]), a)
    return out


def blit(img, sp, x0, y0):
    for y in range(sp.h):
        for x in range(sp.w):
            a = sp.a[y * sp.w + x]
            if a:
                j = (y * sp.w + x) * 3
                img.blend(x0 + x, y0 + y,
                          (sp.rgb[j], sp.rgb[j + 1], sp.rgb[j + 2]), a)


def oval_stamp(lines, color, angle, rng, w=196, h=84):
    sp = Sprite(w, h)
    cx, cy = w // 2, h // 2
    # double oval border
    for rx, ry, alpha in ((w // 2 - 3, h // 2 - 3, 215), (w // 2 - 8, h // 2 - 8, 190)):
        for t in range(360):
            a = math.radians(t)
            sp.blend(int(cx + rx * math.cos(a)), int(cy + ry * math.sin(a)),
                     color, alpha)
    n = len(lines)
    y = cy - (n - 1) * 10 - 2
    for ln in lines:
        sp.text("SN11", cx, y, ln, color)
        y += 20
    # a few ink gaps so the stamp reads as stamped, not printed
    for _ in range(26):
        x = rng.randrange(w)
        yy = rng.randrange(h)
        sp.a[yy * w + x] = 0
    return rotate_sprite(sp, angle)


def rect_stamp(lines, color, angle, rng, w=200, h=78):
    sp = Sprite(w, h)
    for x in range(4, w - 4):
        sp.blend(x, 4, color, 215)
        sp.blend(x, h - 5, color, 215)
    for y in range(4, h - 4):
        sp.blend(4, y, color, 215)
        sp.blend(w - 5, y, color, 215)
    for x in range(8, w - 8):
        sp.blend(x, 8, color, 170)
        sp.blend(x, h - 9, color, 170)
    n = len(lines)
    y = h // 2 - (n - 1) * 10 - 2
    for ln in lines:
        sp.text("SN11", w // 2, y, ln, color)
        y += 20
    for _ in range(26):
        x = rng.randrange(w)
        yy = rng.randrange(h)
        sp.a[yy * w + x] = 0
    return rotate_sprite(sp, angle)


def round_stamp(lines, color, angle, rng, d=86):
    sp = Sprite(d, d)
    cx = cy = d // 2
    for r, alpha in ((d // 2 - 2, 215), (d // 2 - 7, 180)):
        for t in range(360):
            a = math.radians(t)
            sp.blend(int(cx + r * math.cos(a)), int(cy + r * math.sin(a)),
                     color, alpha)
    n = len(lines)
    y = cy - (n - 1) * 10 - 4
    for ln in lines:
        sp.text("SN11", cx, y, ln, color)
        y += 20
    for _ in range(18):
        x = rng.randrange(d)
        yy = rng.randrange(d)
        sp.a[yy * d + x] = 0
    return rotate_sprite(sp, angle)


# ---------------------------------------------------------------------------
# machine-readable zone (ICAO 9303 check digits)
# ---------------------------------------------------------------------------

def mrz_check(s):
    vals = {}
    for i in range(10):
        vals[str(i)] = i
    for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        vals[ch] = 10 + i
    vals["<"] = 0
    total = 0
    for i, ch in enumerate(s):
        total += vals[ch] * (7, 3, 1)[i % 3]
    return str(total % 10)


def mrz_lines():
    line1 = "P<SKRSKJOLD<<INGRID<MARIA"
    line1 = line1 + "<" * (44 - len(line1))
    doc = "SK0417829"
    dob = "880612"
    exp = "330302"
    personal = "1206884173" + "<" * 4
    line2 = (
        doc + mrz_check(doc)
        + "SKR"
        + dob + mrz_check(dob)
        + "F"
        + exp + mrz_check(exp)
        + personal + mrz_check(personal)
    )
    line2 += mrz_check(line2)
    return line1, line2


# ---------------------------------------------------------------------------
# emblem: lighthouse over waves inside a ring
# ---------------------------------------------------------------------------

def draw_emblem(img, cx, cy, r, ring_rgb=GOLD, ink_rgb=INK):
    img.ring(cx, cy, r, 2, ring_rgb, 235)
    img.ring(cx, cy, r - 5, 1, ring_rgb, 200)
    # light rays
    for dx, dy in ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0)):
        img.thick_line(cx, cy - r + 12, cx + dx * (r - 8), cy - r + 12 + dy * 10,
                       1, GOLD, 200)
    # tower: tapered trapezoid
    top = r - 16
    img.poly_fill([
        (cx - 4, cy - top), (cx + 4, cy - top),
        (cx + 8, cy + 6), (cx - 8, cy + 6),
    ], ink_rgb, 235)
    # lamp room
    img.rect(cx - 6, cy - top - 5, cx + 6, cy - top, ink_rgb, 235)
    img.circle_fill(cx, cy - top - 2, 2, GOLD_LIGHT, 235)
    # waves: two sine lines
    for k, yy in enumerate((cy + 12, cy + 18)):
        for x in range(cx - r + 8, cx + r - 7):
            y = int(yy + 2 * math.sin((x - cx) / 5.0 + k))
            img.blend(x, y, ink_rgb, 220)
    # three stars
    for sx, sy in ((cx - 14, cy - r + 16), (cx + 14, cy - r + 16),
                   (cx, cy - r + 8)):
        img.set(sx, sy, GOLD)
        img.set(sx - 1, sy, GOLD)
        img.set(sx + 1, sy, GOLD)
        img.set(sx, sy - 1, GOLD)
        img.set(sx, sy + 1, GOLD)


# ---------------------------------------------------------------------------
# portrait: engraved profile silhouette
# ---------------------------------------------------------------------------

def draw_portrait(img, x0, y0, w, h):
    # background: pale blue-grey with fine horizontal ruling
    for y in range(y0, y0 + h):
        t = (y - y0) / h
        r = int(PHOTO_BG[0] + (PHOTO_BG2[0] - PHOTO_BG[0]) * t)
        g = int(PHOTO_BG[1] + (PHOTO_BG2[1] - PHOTO_BG[1]) * t)
        b = int(PHOTO_BG[2] + (PHOTO_BG2[2] - PHOTO_BG[2]) * t)
        img.hline(x0, x0 + w, y, (r, g, b))
    for y in range(y0 + 4, y0 + h, 6):
        img.hline(x0, x0 + w, y, (170, 182, 192), 60)
    # faint guilloche rosette behind the head
    rcx, rcy = x0 + w // 2 + 12, y0 + 62
    for r in range(14, 46, 8):
        img.ring(rcx, rcy, r, 1, (150, 164, 178), 90)

    # profile, facing left (local coords, origin x0, y0; box 150x190)
    def P(pts):
        return [(x0 + x, y0 + y) for x, y in pts]

    # hair mass behind the head
    img.poly_fill(P([
        (98, 12), (76, 4), (50, 12), (42, 32), (44, 56), (50, 80),
        (56, 102), (64, 120), (76, 130), (94, 136), (106, 126),
        (110, 102), (112, 74), (110, 44), (104, 24),
    ]), (24, 40, 64), 255)
    # bun
    img.circle_fill(x0 + 104, y0 + 34, 13, (24, 40, 64), 255)
    # face + neck + shoulders, skin-tone ink silhouette in deep navy
    img.poly_fill(P([
        (94, 16), (68, 6), (48, 18), (43, 36), (39, 50), (24, 64),
        (40, 72), (35, 78), (31, 82), (37, 86), (33, 90), (40, 96),
        (43, 104), (61, 118), (66, 140), (58, 150), (30, 165), (8, 180),
        (142, 180), (128, 158), (112, 146), (104, 138), (100, 110),
        (103, 70), (101, 40), (99, 24),
    ]), INK, 255)
    # engraving hatches across the hair (paper-coloured, low alpha)
    for k in range(5):
        yy = 26 + k * 12
        for x in range(52, 108):
            y = yy + int(6 * math.sin((x - 52) / 9.0 + k))
            img.blend(x0 + x, y0 + y, PAGE, 70)
    # collar line
    img.thick_line(x0 + 58, y0 + 152, x0 + 96, y0 + 152, 2, PAGE, 160)
    img.thick_line(x0 + 66, y0 + 140, x0 + 58, y0 + 152, 2, PAGE, 160)
    img.thick_line(x0 + 96, y0 + 140, x0 + 104, y0 + 152, 2, PAGE, 160)
    # frame
    img.rect(x0, y0, x0 + w, y0 + 2, INK)
    img.rect(x0, y0 + h - 2, x0 + w, y0 + h, INK)
    img.rect(x0, y0, x0 + 2, y0 + h, INK)
    img.rect(x0 + w - 2, y0, x0 + w, y0 + h, INK)
    img.rect(x0 + 3, y0 + 3, x0 + w - 3, y0 + 5, GOLD)
    img.rect(x0 + 3, y0 + h - 5, x0 + w - 3, y0 + h - 3, GOLD)


# ---------------------------------------------------------------------------
# page furniture
# ---------------------------------------------------------------------------

def guilloche_band(img, x0, x1, y, rgb=GUILLOCHE, alpha=150):
    for k in range(3):
        img.sine_band(x0, x1, y + k * 4, 2, 26, k * 1.3, rgb, alpha)


def rule(img, x0, x1, y, rgb=INK, alpha=220):
    img.hline(x0, x1, y, rgb, alpha)
    img.hline(x0, x1, y + 3, rgb, alpha // 2)


def field(img, x, y, label, value, label_rgb=INK_SOFT, value_rgb=INK):
    draw_text(img, "SN11", x, y, label, label_rgb)
    draw_text(img, "SN15", x, y + 15, value, value_rgb)


def draw_page_shadow(img, x0, y0, x1, y1):
    # drop shadow under the page
    for k in range(10):
        a = 70 - k * 7
        img.rect(x0 + 4 + k, y1 + k, x1 + 4 + k, y1 + k + 1, (0, 0, 0), max(a, 0))
        img.rect(x1 + k, y0 + 4 + k, x1 + k + 1, y1 + k, (0, 0, 0), max(a, 0))
    # gutter shadow on the inner edge
    for k in range(12):
        a = 60 - k * 5
        img.vline(x1 - 1 - k, y0, y1, (0, 0, 0), max(a, 0))


# ---------------------------------------------------------------------------
# the spread
# ---------------------------------------------------------------------------

def build():
    rng = random.Random(20261121)
    img = Img(W, H, DESK)
    # desk shading: darker corners
    for y in range(H):
        for x in range(0, W, 4):
            d = math.hypot(x - W / 2, y - H / 2) / (W / 2)
            if d > 0.75:
                a = int(min(60, (d - 0.75) * 240))
                img.blend(x, y, DESK_DARK, a)
                img.blend(x + 1, y, DESK_DARK, a)
                img.blend(x + 2, y, DESK_DARK, a)
                img.blend(x + 3, y, DESK_DARK, a)

    lx0, ly0, lx1, ly1 = 56, 140, 500, 884
    rx0, ry0, rx1, ry1 = 524, 140, 968, 884

    # right page first (left page overlaps the gutter slightly)
    draw_page_shadow(img, rx0, ry0, rx1, ry1)
    img.rect(rx0, ry0, rx1, ry1, PAGE)
    draw_page_shadow(img, lx0, ly0, lx1, ly1)
    img.rect(lx0, ly0, lx1, ly1, PAGE)
    # page edge tint
    img.rect(lx0, ly0, lx1, ly0 + 3, PAGE_EDGE)
    img.rect(rx0, ry0, rx1, ry0 + 3, PAGE_EDGE)
    # gutter shadow between the pages
    for k in range(14):
        a = 55 - k * 4
        img.vline(lx1 - 1 - k, ly0, ly1, (0, 0, 0), max(a, 0))
        img.vline(rx0 + k, ry0, ry1, (0, 0, 0), max(a, 0))

    # ---- left page: data page -------------------------------------------
    guilloche_band(img, lx0 + 16, lx1 - 16, 296)
    guilloche_band(img, lx0 + 16, lx1 - 16, 640)
    draw_emblem(img, 278, 178, 26)
    draw_text(img, "SB30", 278, 208, "FREE STATE OF SKERRY", INK, align="c")
    draw_text(img, "SB12", 278, 246, "VEGABRÉF  ·  PASSPORT", MAROON, align="c")
    rule(img, lx0 + 24, lx1 - 24, 268)

    draw_portrait(img, 80, 288, 150, 190)
    draw_text(img, "SN11", 155, 484, "PHOTOGRAPH / MYND", INK_SOFT, align="c")

    fx = 246
    field(img, fx, 288, "SURNAME / ETTERNAVN", "SKJOLD")
    field(img, fx, 326, "GIVEN NAMES / FORNAVN", "INGRID MARIA")
    field(img, fx, 364, "NATIONALITY / NASJONALITET", "SKERRY")
    field(img, fx, 402, "DATE OF BIRTH / FØDT", "12 JUN 1988")
    field(img, fx, 440, "PLACE OF BIRTH / FØDESTED", "PORT ANSELM")

    field(img, 80, 516, "SEX / KJØNN", "F")
    field(img, 80, 562, "DATE OF ISSUE / UTSTEDT", "03 MAR 2023")
    field(img, 80, 608, "AUTHORITY / MYNDIGHET", "PORT ANSELM")
    draw_text(img, "SN15", 80, 640, "HARBOUR OFFICE", INK)
    field(img, 300, 516, "PASSPORT NO.", "SK 0417829")
    field(img, 300, 562, "DATE OF EXPIRY / GYLDIG TIL", "02 MAR 2033")
    field(img, 300, 608, "PERSONAL NO.", "120688-4173")

    draw_text(img, "SN11", 80, 664, "HOLDER'S SIGNATURE / UNDERSKRIFT", INK_SOFT)
    draw_text(img, "SRIT20", 80, 682, "Ingrid Maria Skjold", INK)
    img.hline(80, 300, 706, INK_SOFT, 150)

    line1, line2 = mrz_lines()
    draw_text(img, "SM14", 79, 736, line1, INK)
    draw_text(img, "SM14", 79, 758, line2, INK)
    guilloche_band(img, lx0 + 16, lx1 - 16, 800)
    draw_text(img, "SN11", 80, 812, "SKERRYMAAL  ·  ENGLISH", INK_SOFT)
    draw_text(img, "SN11", lx1 - 24, 812, "1", INK_SOFT, align="r")

    # ---- right page: visas and stamps ------------------------------------
    guilloche_band(img, rx0 + 16, rx1 - 16, 356)
    guilloche_band(img, rx0 + 16, rx1 - 16, 660)
    draw_text(img, "SB18", 746, 158, "VISAS AND STAMPS", INK, align="c")
    rule(img, rx0 + 24, rx1 - 24, 184)

    # Kestrelia visitor visa
    vx0, vy0, vx1, vy1 = 548, 204, 944, 330
    img.rect(vx0, vy0, vx1, vy1, VISA_BG)
    img.rect(vx0, vy0, vx1, vy0 + 2, VISA_LINE)
    img.rect(vx0, vy1 - 2, vx1, vy1, VISA_LINE)
    img.rect(vx0, vy0, vx0 + 2, vy1, VISA_LINE)
    img.rect(vx1 - 2, vy0, vx1, vy1, VISA_LINE)
    img.rect(vx0 + 5, vy0 + 5, vx1 - 5, vy0 + 7, VISA_LINE, 160)
    img.rect(vx0 + 5, vy1 - 7, vx1 - 5, vy1 - 5, VISA_LINE, 160)
    draw_text(img, "SB18", 746, 216, "KESTRELIA", INK, align="c")
    draw_text(img, "SB12", 746, 240, "VISITOR VISA", MAROON, align="c")
    draw_text(img, "SN11", 746, 266,
              "VALID 28 MAR 2024 – 27 APR 2024  ·  30 DAYS  ·  SINGLE ENTRY",
              INK, align="c")
    draw_text(img, "SN11", 746, 286,
              "ISSUED AT PORT ANSELM  ·  No. KV-2024-1187", INK, align="c")
    draw_text(img, "SN11", 746, 306, "HOLDER MUST REGISTER WITH THE HARBOURMASTER",
              INK_SOFT, align="c")

    # stamps: eight, in two columns x four rows
    stamps = [
        (["KESTRELIA", "ARRIVED", "14 APR 2024"], STAMP_BLUE, "oval", -7),
        (["KESTRELIA", "DEPARTED", "21 APR 2024"], STAMP_BLUE, "oval", 6),
        (["VELMARA", "ARRIVED", "02 SEP 2024"], STAMP_PURPLE, "rect", 5),
        (["VELMARA", "DEPARTED", "09 SEP 2024"], STAMP_PURPLE, "rect", -6),
        (["TARNOVIA", "ARRIVED", "18 JUN 2025"], STAMP_TEAL, "oval", -5),
        (["TARNOVIA", "DEPARTED", "30 JUN 2025"], STAMP_TEAL, "oval", 7),
        (["KESTRELIA", "ARRIVED", "11 NOV 2025"], STAMP_BLUE, "oval", 6),
        (["KESTRELIA", "DEPARTED", "18 NOV 2025"], STAMP_BLUE, "oval", -7),
    ]
    col_x = (560, 758)
    row_y = (382, 458, 534, 610)
    for i, (lines, color, shape, angle) in enumerate(stamps):
        cx = col_x[i % 2]
        cy = row_y[i // 2]
        if shape == "oval":
            sp = oval_stamp(lines, color, angle, rng)
        else:
            sp = rect_stamp(lines, color, angle, rng)
        blit(img, sp, cx - sp.w // 2, cy - sp.h // 2)

    # round return stamp overlapping the visa's lower right corner
    sp = round_stamp(["PORT ANSELM", "RETURNED", "19 NOV 2025"], STAMP_RED, -12, rng, d=96)
    blit(img, sp, 880 - sp.w // 2, 358 - sp.h // 2)

    # tide table
    tx0, ty0, tx1 = 548, 690, 944
    draw_text(img, "SB12", tx0, ty0, "TIDES — PORT ANSELM", INK)
    draw_text(img, "SN11", tx1, ty0, "NOV 2025", INK_SOFT, align="r")
    img.hline(tx0, tx1, ty0 + 18, INK, 200)
    tides = [
        ("MON 24 NOV", "HW 06:12  3.8 m", "LW 12:31  0.6 m"),
        ("TUE 25 NOV", "HW 06:54  3.9 m", "LW 13:12  0.5 m"),
        ("WED 26 NOV", "HW 07:36  4.0 m", "LW 13:54  0.5 m"),
        ("THU 27 NOV", "HW 08:19  4.1 m", "LW 14:37  0.4 m"),
    ]
    ty = ty0 + 26
    for day, hw, lw in tides:
        draw_text(img, "SN11", tx0, ty, day, INK)
        draw_text(img, "SN11", tx0 + 130, ty, hw, INK)
        draw_text(img, "SN11", tx0 + 270, ty, lw, INK)
        ty += 18
    img.hline(tx0, tx1, ty + 2, INK, 200)

    # harbour-dues stamp in the gap between the stamps and the tide table
    sp = rect_stamp(["HARBOUR DUES", "12 KR — PAID"], STAMP_RED, -8, rng, w=150, h=40)
    blit(img, sp, 746 - sp.w // 2, 663 - sp.h // 2)

    # condition 7
    cx0, cy0, cx1, cy1 = 548, 806, 944, 868
    img.rect(cx0, cy0, cx1, cy0 + 1, MAROON, 200)
    img.rect(cx0, cy1 - 1, cx1, cy1, MAROON, 200)
    img.rect(cx0, cy0, cx0 + 1, cy1, MAROON, 200)
    img.rect(cx1 - 1, cy0, cx1, cy1, MAROON, 200)
    draw_text_wrap(img, "SN11", cx0 + 10, cy0 + 8, cx1 - cx0 - 20,
                   "CONDITION 7 — THE HOLDER MUST BE ASHORE BEFORE THE "
                   "FIRST AUTUMN GALE. THE CAUSEWAY FLOODS AT HIGH WATER.",
                   MAROON, 15)
    draw_text(img, "SN11", rx1 - 24, 872, "2", INK_SOFT, align="r")

    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img = build()
    data = img.to_png()
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(data)


if __name__ == "__main__":
    main()
