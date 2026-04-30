## Diagnostics

| source_dir              | source_file                                            | total_rows   | priority_rows   | excluded_rows   | participants   | top_excluded                                                                                                                                                                   |
|:------------------------|:-------------------------------------------------------|:-------------|:----------------|:----------------|:---------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ARIC-v8-c1-remapped     | ARIC-v8-c1-MeasurementObservation-HMB-IRB-data.tsv     | 143,007      | 143,007         | 0               | 14,565         |                                                                                                                                                                                |
| CARDIA-v3-c1-remapped   | CARDIA-v3-c1-MeasurementObservation-HMB-IRB-data.tsv   | 555,202      | 549,315         | 5,887           | 3,111          | {'OBA:VT0000188': 5887}                                                                                                                                                        |
| CHS-v7-c1-remapped      | CHS-v7-c1-MeasurementObservation-HMB-IRB-MDS-data.tsv  | 2,240,344    | 2,209,482       | 30,862          | 5,353          | {'OBA:VT0000188': 21412, 'fasting_hdl_in_plasma': 3872, 'fasting_triglycerides_in_plasma': 3872}                                                                               |
| COPDGene-v6-c1-remapped | COPDGene-v6-c1-MeasurementObservation-HMB-data.tsv     | 100,990      | 100,990         | 0               | 10,099         |                                                                                                                                                                                |
| FHS-v31-c1-remapped     | FHS-v31-c1-MeasurementObservation-HMB-IRB-MDS-data.tsv | 2,414,416    | 1,828,121       | 586,295         | 13,071         | {'OBA:VT0000188': 286109, 'fasting_hdl_in_plasma': 157440, 'OMOP:4273021': 71950, 'OMOP:37311566': 17734, 'OMOP:2212186': 14496}                                               |
| HCHS-SOL-v1-c1-remapped | HCHS-SOL-v1-c1-MeasurementObservation-HMB-NPU-data.tsv | 152,284      | 133,594         | 18,690          | 3,461          | {'OMOP:44777566': 3461, 'OMOP:37208634': 3461, 'fasting_hdl_in_serum': 2774, 'fasting_ldl_in_serum': 2774, 'fasting_total_cholesterol_in_serum': 2774}                         |
| JHS-v7-c1-remapped      | JHS-v7-c1-MeasurementObservation-HMB-IRB-NPU-data.tsv  | 877          | 877             | 0               | 877            |                                                                                                                                                                                |
| MESA-v13-c1-remapped    | MESA-v13-c1-MeasurementObservation-HMB-data.tsv        | 1,370,573    | 1,133,317       | 237,256         | 7,440          | {'OMOP:607590': 35164, 'OMOP:4172830': 29552, 'OMOP:4111665': 29552, 'OMOP:3007081': 24884, 'OMOP:4099154': 13448}                                                             |
| WHI-v12-c1-remapped     | WHI-v12-c1-MeasurementObservation-HMB-IRB-data.tsv     | 13,601,999   | 13,506,304      | 95,695          | 117,675        | {'fasting_hdl_in_plasma': 40872, 'OBA:VT0000188': 13831, 'fasting_ldl_in_plasma': 13624, 'fasting_total_cholesterol_in_serum': 13624, 'fasting_triglycerides_in_serum': 13624} |

## Summary

| observation_type        | label                                     | n         | nulls_missing   | participants   | mean       | median    | min      | max           | sd           |
|:------------------------|:------------------------------------------|:----------|:----------------|:---------------|:-----------|:----------|:---------|:--------------|:-------------|
| albumin_bld             | Albumin in blood                          | 47,273    | 9,682           | 22,922         | 3.98       | 4.00      | 2.00     | 5.90          | 0.35         |
| albumin_creatinine      | Albumin creatinine ratio in urine         | 32,786    | 3,818           | 12,511         | 28.80      | 5.50      | -0.13    | 35,312.50     | 257.61       |
| albumin_urine           | Albumin in urine                          | 59,568    | 24,161          | 22,139         | 69.18      | 8.00      | 0.50     | 48,800.00     | 706.00       |
| alcohol_servings        | Alcohol                                   | 1,035,673 | 909,423         | 125,424        | 6.95       | 7.00      | 0.00     | 700.00        | 6.73         |
| alt_sgpt                | ALT SGPT                                  | 10,674    | 3,983           | 7,607          | 23.90      | 20.00     | 1.80     | 1,966.00      | 30.09        |
| apnea_hypop_index       | AHI Apnea-Hypopnea Index                  | 1,068,362 | 870,354         | 11,020         | 8.74       | 0.70      | 0.00     | 145.12        | 15.56        |
| ast_sgot                | AST SGOT                                  | 18,195    | 508             | 10,718         | 269.98     | 24.30     | 1.00     | 37,795.80     | 966.04       |
| basophil_ncnc_bld       | basophils count                           | 12,381    | 1,198           | 10,527         | 0.02       | 0.00      | 0.00     | 2.00          | 0.07         |
| bdy_hgt                 | Height                                    | 942,159   | 730,694         | 152,055        | 1,312.01   | 167.00    | 0.00     | 19,558.00     | 4,152.12     |
| bdy_temp                | Temperature                               | 15,237    | 330             | 6,624          | 23.53      | 24.00     | 0.00     | 33.00         | 1.60         |
| bdy_wgt                 | Body weight                               | 1,240,578 | 1,082,579       | 151,197        | 74.29      | 72.12     | 24.04    | 453.14        | 16.83        |
| bilirubin_con           | Bilirubin Conjugated Direct               | 2,947     | 133             | 2,947          | 15.86      | 14.00     | 0.00     | 220.00        | 9.31         |
| bilirubin_tot           | Bilirubin total                           | 17,661    | 494             | 10,719         | 14.07      | 0.73      | 0.10     | 583.00        | 30.48        |
| bmi                     | BMI                                       | 583,979   | 560,015         | 133,441        | 28.83      | 27.96     | 12.29    | 64.10         | 6.06         |
| bp_diastolic            | Diastolic blood pressure                  | 2,269,900 | 2,259,639       | 130,647        | 76.79      | 77.00     | 34.00    | 135.00        | 10.88        |
| bp_systolic             | Systolic blood pressure                   | 2,270,138 | 2,256,766       | 130,885        | 124.54     | 123.00    | 60.00    | 228.00        | 17.50        |
| bun                     | BUN                                       | 41,857    | 33,824          | 34,860         | 17.11      | 15.00     | 4.00     | 129.00        | 8.50         |
| cac_score               | CAC Score                                 | 260,267   | 107,321         | 16,076         | 176.22     | 2.34      | 0.00     | 34,092.70     | 546.17       |
| cac_volume              | CAC volume                                | 186,289   | 79,638          | 9,600          | 134.27     | 0.00      | 0.00     | 9,638.10      | 374.92       |
| carotid_imt             | Carotid IMT                               | 118,063   | 48,414          | 28,691         | 0.84       | 0.80      | 0.22     | 4.49          | 0.28         |
| carotid_sten_left       | Carotid stenosis left                     | 25,196    | 20,756          | 11,207         | 3.00       | 1.00      | 0.00     | 100.00        | 11.87        |
| carotid_sten_right      | Carotid stenosis right                    | 25,196    | 20,734          | 11,207         | 3.23       | 1.00      | 0.00     | 100.00        | 12.84        |
| cd40                    | CD40 in blood                             | 1,463     | 0               | 1,463          | 229.95     | 173.60    | 84.10    | 9,662.80      | 448.47       |
| cesd_score              | CESD score                                | 25,747    | 25,747          | 7,753          |            |           |          |               |              |
| chloride_bld            | Chloride in blood                         | 9,673     | 569             | 8,135          | 107.89     | 108.00    | 84.40    | 132.00        | 4.78         |
| creat_bld               | Creatinine in blood                       | 140,642   | 76,503          | 49,991         | 1.62       | 0.92      | 0.10     | 110.00        | 2.67         |
| creat_urin              | Creatinine in urine                       | 26,260    | 608             | 13,800         | 517,466.13 | 128.00    | 4.40     | 54,367,647.40 | 4,363,644.90 |
| crp                     | c-reactive protein CRP                    | 60,929    | 16,793          | 24,956         | 1,548.98   | 3.06      | 0.12     | 357,990.50    | 10,574.08    |
| cysc_bld                | Cystatin C in blood                       | 20,172    | 7,615           | 8,171          | 200.72     | 0.11      | 0.05     | 5,941.70      | 565.72       |
| d_dimer                 | D-Dimer                                   | 34,279    | 14,293          | 14,976         | 148,567.70 | 1.10      | -99.00   | 999,909.00    | 278,984.34   |
| egfr                    | EGFR                                      | 49,922    | 6,490           | 9,515          | 82.78      | 82.52     | 4.82     | 536.40        | 21.32        |
| eosinophil_ncnc_bld     | Eosinophils count                         | 12,381    | 1,192           | 10,527         | 0.17       | 0.10      | 0.00     | 230.00        | 2.18         |
| eselectin               | E-selectin in blood                       | 12,740    | 10,375          | 6,715          | 53.17      | 48.04     | 4.65     | 499.00        | 30.18        |
| factor_7                | Factor VII                                | 66,120    | 41,065          | 14,228         | 167.52     | 112.00    | 5.00     | 3,699.90      | 174.40       |
| factor_8                | Factor VIII                               | 25,113    | 1,370           | 13,918         | 238.24     | 1.26      | 0.01     | 21,967.40     | 1,093.54     |
| fast_gluc_bld           | Fasting blood glucose                     | 86,839    | 15,385          | 23,009         | 99.59      | 94.00     | 25.00    | 714.00        | 27.67        |
| fast_lipids             | Fasting lipids                            | 2,505     | 1,337           | 2,505          | 228.46     | 224.00    | 98.00    | 417.00        | 43.01        |
| ferritin                | Ferritin                                  | 6,387     | 674             | 4,924          | 3,259.43   | 163.90    | 7.00     | 159,186.50    | 10,231.51    |
| fev1                    | FEV1 - Forced Expiratory Volume in 1 sec  | 116,517   | 22,872          | 33,370         | 2.92       | 2.89      | 0.00     | 6.91          | 0.97         |
| fev1_fvc                | FEV1 FVC                                  | 10,564    | 175             | 10,254         | 0.66       | 0.71      | 0.14     | 0.98          | 0.15         |
| fibrin                  | Fibrinogen                                | 77,077    | 31,655          | 26,672         | 4,961.11   | 316.00    | 2.00     | 401,622.70    | 25,733.85    |
| fruit_serving           | Fruits                                    | 912,593   | 887,961         | 132,623        | 12.37      | 10.35     | 0.00     | 175.00        | 11.44        |
| fvc                     | FVC - Forced Vital Capacity               | 145,405   | 31,316          | 34,323         | 4.52       | 3.83      | 0.00     | 60.90         | 4.11         |
| gfr                     | GFR                                       | 11,660    | 1,688           | 5,830          | 77.04      | 76.40     | 5.68     | 175.49        | 17.61        |
| hdl                     | HDL                                       | 96,798    | 49,912          | 15,241         | 45.63      | 47.00     | 0.00     | 204.00        | 21.73        |
| hemat                   | Hematocrit                                | 294,627   | 226,285         | 141,021        | 43.61      | 44.00     | 10.90    | 76.10         | 4.36         |
| hemo                    | Hemoglobin                                | 269,059   | 221,369         | 139,388        | 13.90      | 13.90     | 3.60     | 44.90         | 1.41         |
| hemo_a1c                | Hemoglobin A1c                            | 24,258    | 2,427           | 14,779         | 5.78       | 5.60      | 3.20     | 19.10         | 0.93         |
| hip_circ                | Hip circumference                         | 677,508   | 588,887         | 141,404        | 103.30     | 101.60    | 2.54     | 306.00        | 11.07        |
| hrtrt                   | Heart rate                                | 943,672   | 594,572         | 93,394         | 76.95      | 67.64     | 0.00     | 671.00        | 30.50        |
| icam                    | ICAM1 in blood                            | 21,811    | 13,105          | 15,649         | 695.24     | 269.26    | 3.00     | 9,065.80      | 1,124.40     |
| il10                    | Interleukin 10 in blood                   | 4,790     | 2,499           | 4,248          | 100.18     | 107.40    | -555.00  | 4,692.10      | 187.09       |
| il1_beta                | Interleukin 1 beta in blood               | 1,463     | 0               | 1,463          | 2,189.49   | 1,777.30  | 496.60   | 29,778.10     | 1,987.32     |
| il6                     | interleukin 6 in blood                    | 16,530    | 747             | 12,862         | 24.90      | 1.69      | 0.13     | 14,830.20     | 160.60       |
| insulin_blood           | Insulin in blood                          | 91,497    | 43,692          | 24,485         | 86.56      | 54.00     | 0.00     | 6,208.02      | 155.92       |
| isoprostane_8_epi_pgf2a | 8-epi-PGF2a in urine                      | 8,653     | 5,989           | 8,653          | 60.87      | 52.08     | 6.26     | 422.97        | 34.06        |
| lactate_blood           | Lactate in blood                          | 2,501     | 86              | 2,501          | 0.92       | 0.90      | 0.00     | 5.16          | 0.42         |
| lactate_dehyd           | Lactate Dehydrogenase LDH                 | 2,359     | 145             | 1,464          | 516.52     | 615.05    | 79.90    | 2,030.30      | 262.98       |
| ldl                     | LDL                                       | 164,184   | 55,975          | 26,923         | 120.04     | 118.00    | 6.00     | 418.00        | 35.69        |
| lppla2_act              | Activity LP-PLA2 in blood                 | 10,233    | 274             | 4,880          | 92.20      | 63.77     | 8.67     | 332.60        | 61.08        |
| lppla2_mass             | Mass LP-PLA2 in blood                     | 10,233    | 339             | 10,233         | 266.68     | 229.49    | 51.40    | 1,427.90      | 124.32       |
| lympho_pct              | Lymphocytes percent                       | 6,408     | 237             | 6,408          | 18.84      | 22.00     | 0.00     | 90.00         | 18.78        |
| mch                     | mean corpuscular hemoglobin               | 15,086    | 989             | 12,336         | 21.50      | 29.30     | 2.80     | 49.80         | 12.56        |
| mchc                    | mean corpuscular hemoglobin concentration | 19,041    | 1,345           | 15,643         | 30.13      | 33.30     | 6.70     | 51.70         | 7.42         |
| mcp1                    | MCP1 in blood                             | 1,463     | 0               | 1,463          | 851.09     | 774.70    | 297.00   | 19,849.40     | 725.31       |
| mcv                     | mean corpuscular volume                   | 15,930    | 1,318           | 12,531         | 90.99      | 91.00     | 60.00    | 971.00        | 15.00        |
| mmp9                    | MMP9 in blood                             | 2,926     | 0               | 1,463          | 4,037.91   | 3,663.95  | 370.10   | 182,956.30    | 5,325.56     |
| mn_art_pres             | Mean arterial pressure                    | 24,369    | 1,521           | 11,103         | 93.82      | 93.00     | 40.00    | 173.00        | 13.29        |
| monocyte_ncnc_bld       | monocytes count                           | 15,868    | 1,612           | 12,798         | 0.43       | 0.40      | 0.00     | 14.80         | 0.53         |
| mpo                     | Myeloperoxidase in blood                  | 1,463     | 0               | 1,463          | 13,782.28  | 13,224.20 | 3,748.20 | 39,632.90     | 4,638.66     |
| neutro_pct              | Neutrophils percent                       | 6,572     | 130             | 6,572          | 53.64      | 55.00     | 1.00     | 92.00         | 11.90        |
| nt_bnp                  | NT pro BNP                                | 213,970   | 204,318         | 37,811         | 564.47     | 39.91     | 4.00     | 162,263.00    | 2,602.45     |
| obesity                 | Obesity                                   | 34,519    | 34,519          | 11,440         |            |           |          |               |              |
| opg                     | Osteoprotegerin in blood                  | 1,463     | 0               | 1,463          | 6,647.86   | 6,639.90  | 605.10   | 16,618.40     | 2,098.05     |
| pacem_stat              | Pacemaker implant status                  | 23,956    | 23,956          | 12,855         |            |           |          |               |              |
| platelet_ct             | Platelet count                            | 216,581   | 184,765         | 137,836        | 2,046.84   | 246.00    | 0.00     | 49,944.00     | 7,006.45     |
| pmv                     | mean platelet volume                      | 5,973     | 954             | 5,973          | 8.73       | 8.60      | 5.60     | 13.60         | 0.98         |
| potassium               | Potassium in blood                        | 33,072    | 12,586          | 11,183         | 4.20       | 4.20      | 2.40     | 7.90          | 0.39         |
| pr_ekg                  | PR interval                               | 152,283   | 152,283         | 53,735         |            |           |          |               |              |
| qrs_ekg                 | QRS interval                              | 211,476   | 173,464         | 58,759         | 94.46      | 88.00     | 56.00    | 461.00        | 19.16        |
| qt_ekg                  | QT interval                               | 331,600   | 304,649         | 60,476         | 377.76     | 380.00    | 30.00    | 800.00        | 34.85        |
| rdbld_ct                | Red blood cell count                      | 12,844    | 397             | 10,094         | 4.67       | 4.65      | 0.64     | 8.36          | 0.51         |
| rdw                     | Red cell distribution width               | 7,005     | 931             | 7,005          | 13.33      | 13.10     | 11.00    | 29.90         | 1.22         |
| sleep_duration_daily    | Sleep hours                               | 649,814   | 241,497         | 143,020        | 8.02       | 7.00      | 0.00     | 9,999.00      | 39.05        |
| sodium_blood            | Sodium in blood                           | 42,986    | 33,791          | 39,116         | 143.72     | 144.00    | 118.00   | 172.00        | 5.18         |
| sodium_intak            | Sodium intake                             | 339,766   | 295,509         | 135,778        | 2,986.91   | 2,489.35  | 1.32     | 59,865.80     | 2,023.25     |
| spo2                    | SpO2                                      | 30,494    | 12,772          | 19,788         | 96.25      | 97.00     | 58.00    | 100.00        | 2.97         |
| tnfa                    | TNFa in blood                             | 6,262     | 2,314           | 3,555          | 198.04     | 159.50    | 0.06     | 60,717.90     | 1,050.05     |
| tnfa_r1                 | TNFa-R1 in blood                          | 5,830     | 3,278           | 5,830          | 1,372.55   | 1,293.00  | -888.00  | 5,544.00      | 464.52       |
| tot_chol_bld            | Total cholesterol in blood                | 219,053   | 69,478          | 26,938         | 207.24     | 203.00    | 50.00    | 1,124.00      | 45.05        |
| triglyc_bld             | Triglycerides in blood                    | 138,352   | 48,953          | 25,300         | 272.85     | 108.00    | 0.00     | 9,996.00      | 1,133.21     |
| vege_serving            | Vegetables                                | 597,306   | 592,784         | 126,203        | 2.36       | 0.59      | 0.00     | 105.00        | 6.03         |
| waist_circ              | Waist circumference                       | 670,106   | 577,745         | 138,116        | 92.32      | 92.00     | 24.50    | 251.00        | 15.47        |
| waist_hip               | Waist-hip ratio                           | 555,397   | 551,948         | 121,136        | 0.92       | 0.93      | 0.54     | 1.25          | 0.07         |
| whtbld_ct               | White blood cell count                    | 198,742   | 173,899         | 132,930        | 16.00      | 6.50      | 0.00     | 559.00        | 21.76        |
| willeb_fac              | von Willebrand factor                     | 17,488    | 5,491           | 9,934          | 1,303.25   | 109.20    | 1.00     | 51,942.30     | 3,985.52     |