import qubovert as qv
import numpy as np
import yaml
import pandas

N_lecturers = 5
N_subj = 2
N_groups = 2
N_days = 12
N_t = 8

x = {(g,s,p,d,t): qv.QUBO.create_var('x%d%d%d%d%d'% (g,s,p,d,t)) for g in range(N_groups) for s in range(N_subj) for p in range(N_lecturers) for d in range(N_days) for t in range(N_t)}

power_2nd_cond = 3 # 7>6
slack_2nd_cond = {(g,d,pow_): qv.QUBO.create_var('s2_%d%d%d'% (g,d,pow_)) for g in range(N_groups) for d in range(N_days) for pow_ in range(power_2nd_cond)}

power_3rd_cond = 2 # 3>2
slack_3rd_cond = {(d,p,s,g,pow_): qv.QUBO.create_var('s3_%d%d%d%d%d'% (d,p,s,g,pow_)) for g in range(N_groups) for s in range(N_subj) for p in range(N_lecturers) for d in range(N_days) for pow_ in range(power_3rd_cond)}

power_6th_cond = 5 # 31>20
slack_6th_cond = {(p,w,pow_): qv.QUBO.create_var('s6_%d%d%d'% (p,w,pow_)) for p in range(N_lecturers) for w in range(2) for pow_ in range(power_6th_cond)}



model = 0


# 4th condition:
for key in x.keys():
    if key[2] == 0 and (key[3] == 2 or key[3] == 8):
        x[key] == 0

    if key[2] == 1 and (key[3] == 0 or key[3] == 6): # ponedelnik
        x[key] == 0

    if key[2] == 2 and (key[3] == 5 or key[3] == 11):
        x[key] == 0

    if (key[2] == 3 or key[2] == 4) and (key[3] == 1 or key[3] == 7):
        x[key] == 0


# 2nd condition:
for d in range(N_days):
    for g in range(N_groups):
        sum_1 = 0
        sum_2 = 0

        for p in range(N_lecturers):
            for s in range(N_subj):
                for t in range(N_t):
                    sum_1 += x[(g,s,p,d,t)]

        for pow_ in range(power_2nd_cond):
            sum_2 += 2**(pow_) * slack_2nd_cond[(g,d,pow_)]
        
        model += (sum_1 + sum_2 - 6)**2


# 3rd condition:
for d in range(N_days):
    for g in range(N_groups):
        for p in range(N_lecturers):
            for s in range(N_subj):
                
                sum_1 = 0
                sum_2 = 0

                for t in range(N_t):
                    sum_1 += x[(g,s,p,d,t)]
         
                for pow_ in range(power_3rd_cond):
                    sum_2 += 2**(pow_) * slack_3rd_cond[(d,p,s,g,pow_)]
        
                model += (sum_1 + sum_2 - 2)**2


# 5th condition:
for p in range(N_lecturers):
    for s in range(N_subj):
        for g in range(N_groups):
            sum_ = 0
            for t in range(N_t):
                for d in range(N_days):
                    sum_ += x[(g,s,p,d,t)]
            model += (sum_ - 4)**2


# 6th condition:
for p in range(N_lecturers):

    sum_1 = 0
    sum_2 = 0

    for d in range(0, 6):
        for s in range(N_subj):
            for g in range(N_groups):
                for t in range(N_t):
                    sum_1 += x[(g,s,p,d,t)]
    
    for pow_ in range(power_6th_cond):
        sum_2 += 2**(pow_) * slack_6th_cond[(p,0,pow_)]
    
    model += (sum_1 + sum_2 - 20) ** 2

    sum_1 = 0
    sum_2 = 0

    for d in range(6, 12):
        for s in range(N_subj):
            for g in range(N_groups):
                for t in range(N_t):
                    sum_1 += x[(g,s,p,d,t)]
    
    for pow_ in range(power_6th_cond):
        sum_2 += 2**(pow_) * slack_6th_cond[(p,1,pow_)]
    
    model += (sum_1 + sum_2 - 20) ** 2


# additional const-s:

# constr 1:
slack_add_1 = {(g,d,t): qv.QUBO.create_var('sa1%d%d%d'% (g,d,t)) for g in range(N_groups) for d in range(N_days) for t in range(N_t)}

for d in range(N_days):
    for g in range(N_groups):
        for t in range(N_t):
            sum_1 = 0
            for p in range(N_lecturers):
                for s in range(N_subj):
                    sum_1 += x[(g,s,p,d,t)]
            model += (sum_1 + slack_add_1[(g,d,t)] - 1) ** 2


# constr 2:
slack_add_2 = {(s,p,d,t): qv.QUBO.create_var('sa2%d%d%d%d'% (s,p,d,t)) for s in range(N_subj) for p in range(N_lecturers) for d in range(N_days) for t in range(N_t)}

for d in range(N_days):
    for p in range(N_lecturers):
        for s in range(N_subj):
            for t in range(N_t):
                sum_1 = 0
                for g in range(N_groups):
                    sum_1 += x[(g,s,p,d,t)]               
                model += (sum_1 + slack_add_2[(s,p,d,t)] - 1)**2

matr = model.to_qubo()
map_ = model.reverse_mapping
# print(map_)

import qubovert.utils

offset = matr[()]


# ===parser part==

 # Specify the file path and name of the YAML file to parse
file_path = './solution.yaml'

ret_dict = dict()
# Read and parse the YAML file
with open(file_path, 'r') as file:
    parsed_data = yaml.safe_load(file)
    ret_dict.update({int(key[2:]) : int(value) for key, value in parsed_data[0]['solution']['variables'].items()})
    

# print(ret_dict)
# num_of_var: 0/1

solution_simcim_string = {map_[i]: ret_dict[i]  for i in map_.keys()}
# print(solution_simcim_string)




teach_sub = [('Иванов', 'Квантовая механика', 'Квантовая теория информации'), ('Петров', 'Квантовые вычисления', 'Сложность квантовых алгоритмов'), ('Сидоров', 'Квантовые алгоритмы в логистике', 'Квантовое машинное обучение'), ('Карпов', 'Моделирование квантовых систем', 'Квантовые алгоритмы в химии'), ('Соколов', 'Физическая реализация квантовых компьютеров', 'Моделирование квантовых алгоритмов') ]
days = [('неделя 1', 'пн'), ('неделя 1', 'вт'), ('неделя 1', 'ср'), ('неделя 1', 'чт'), ('неделя 1', 'пт'), ('неделя 1', 'сб'), ('неделя 2', 'пн'), ('неделя 2', 'вт'), ('неделя 2', 'ср'), ('неделя 2', 'чт'), ('неделя 2', 'пт'), ('неделя 2', 'сб')]
time = ['9:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00', '13:00-14:00', '14:00-15:00', '15:00-16:00', '16:00-17:00']
group = ['QC_1', 'QC_2']

fp = open('./timetable.csv', 'w', encoding = 'UTF-8')

pair_dict = set()
for key in solution_simcim_string.keys():
    if (key[0] == 'x' and solution_simcim_string[key] == 1):
        pair_dict.add((int(key[1]),int(key[2]),int(key[3]),int(key[4]),int(key[5])))

# print(pair_dict)
# print(len(pair_dict))


for p in range(N_lecturers):
    for g in range(N_groups):
        for s in range(N_subj):
            for d in range(N_days):
                for t in range(N_t):
                    if (g,s,p,d,t) in pair_dict:
                        fp.write(group[g] + ',' + days[d][0] + ',' + days[d][1] + ',' + time[t] + ',' + teach_sub[p][s+1] + ',' + teach_sub[p][0] + '\n')
                    
for g in range(N_groups):
    for d in range(N_days):
        for t in range(N_t):
            no_lect = 0
            for p in range(N_lecturers):
                for s in range(N_subj):
                    if (g,s,p,d,t) in pair_dict:
                        no_lect += 1
            if no_lect == 0:
                fp.write(group[g] + ',' + days[d][0] + ',' + days[d][1] + ',' + time[t] + ',' + 'нет занятий' + ',' + 'нет занятий' + '\n')
                    
fp.close()  

# (pandas.read_csv('timetable.csv')).to_latex('timetable.tex')

