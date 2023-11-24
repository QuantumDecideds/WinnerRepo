for num_steps in 1000 10000 100000 1000000
do
	for num_runs in 1 10 100 1000
	do
		if [[ "$num_runs" -eq "1000" ]] && [[ "$num_steps" -eq "1000000" ]]; then
			continue;
		fi
		for dt in "0.01" "0.05" "0.1" "0.25" "0.5" "1"
		do	
			for q in "0.025" "0.05" "0.75" "0.1" "0.4" "0.8"
			do 
				python3 generate_yaml.py -dt=$dt -q=q -steps=$((num_steps)) -runs=$((num_runs));
				./run_demo;
				cp output/solution.yaml grid_results/solution_${q}_${dt}_${num_steps}_${num_runs}.yaml;
			done	
		done
	done
done