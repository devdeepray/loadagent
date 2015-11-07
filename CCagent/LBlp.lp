\* LB problem *\
Minimize
Total_cost_to_minimize: 100 Lb_C1_D1_A1 + 300 Lb_C1_D2_A1 + 200 Lb_C2_D1_A1
 + 200 Lb_C2_D2_A1 + 300 Lb_C3_D1_A1 + 100 Lb_C3_D2_A1
Subject To
Distribution_fraction_sum_constraint_for_A1C1: Lb_C1_D1_A1 + Lb_C1_D2_A1 = 1
Distribution_fraction_sum_constraint_for_A1C2: Lb_C2_D1_A1 + Lb_C2_D2_A1 = 1
Distribution_fraction_sum_constraint_for_A1C3: Lb_C3_D1_A1 + Lb_C3_D2_A1 = 1
bandwid_constraint_for_D1: 100 Lb_C1_D1_A1 + 100 Lb_C2_D1_A1 + 100 Lb_C3_D1_A1
 <= 18
bandwid_constraint_for_D2: 100 Lb_C1_D2_A1 + 100 Lb_C2_D2_A1 + 100 Lb_C3_D2_A1
 <= 12
Bounds
Lb_C1_D1_A1 <= 1
Lb_C1_D2_A1 <= 1
Lb_C2_D1_A1 <= 1
Lb_C2_D2_A1 <= 1
Lb_C3_D1_A1 <= 1
Lb_C3_D2_A1 <= 1
End
