import yaml
import argparse

parser = argparse.ArgumentParser(description='Argument Parser')

# Add the float arguments
parser.add_argument('-dt', type=float, help='Time step')
parser.add_argument('-q', type=float, help='q')
parser.add_argument('-steps', type=int, help='Number of steps in each run')
parser.add_argument('-runs', type=int, help='Number of runs')

args = parser.parse_args();

yaml_structure = {
'problems' : [{
	'id': 'QUBO problem test from data', 
	'type': 'QUBO', 
	'data_dir': '~/data/qubo', 
	'solver': 'simcim',
	'options' : ['opt1'],
	"objective": {
		"to": "min", 
		"filenames" : "Q.pkl", 
		"target": -7296
	}
}], 
"simcim" : {
	"opt1": {
		"num_runs" : args.runs,
		"num_steps": args.steps, 
		"dt": args.dt,
		'q': args.q
	}
}
}
# yaml_structure = [{"problems" : ["id", "type", "data_dir"]}]

with open("/home/denison/code/WinnerRepo/test_config.yaml", "w") as file:
	yaml.dump(yaml_structure, file, default_flow_style=False)