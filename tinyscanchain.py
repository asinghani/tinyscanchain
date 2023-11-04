import os, sys, time, json, subprocess

if len(sys.argv) < 4:
    print("Usage: tinyscanchain.py [infile.sv] [top_module] [outfile.sv] [logfile.txt]")

files = sys.argv[1]
top_mod = sys.argv[2]
outfile = sys.argv[3]
logfile = sys.argv[4]

with open(os.path.dirname(__file__)+"/prep-json.ys") as f:
    script = f.read()

script = script.replace("FILES", files)
script = script.replace("TOP_MOD", top_mod)
script = script.replace("OUT_JSON", "/tmp/design.json")

with open("/tmp/synth.ys", "w+") as f:
    f.write(script)

_ = subprocess.check_output(["yosys", "-s", "/tmp/synth.ys"])

with open("/tmp/design.json") as f:
    des = json.load(f)

assert top_mod in des["modules"]
assert len(des["modules"]) == 1

# Find an index to start adding new nets with
idx = max([max(y for y in x["bits"] if isinstance(y, int))
           for x in des["modules"][top_mod]["netnames"].values()])+1

scan_in = (idx := idx + 1)
scan_en = (idx := idx + 1)
scan_cur = scan_in

des["modules"][top_mod]["ports"]["scan_in"] = {"direction": "input", "bits": [scan_in]}
des["modules"][top_mod]["ports"]["scan_en"] = {"direction": "input", "bits": [scan_en]}

netnames = {}

for name, net in des["modules"][top_mod]["netnames"].items():
    if len(net["bits"]) == 1:
        netnames[net["bits"][0]] = name
    else:
        for i in range(len(net["bits"])):
            if net["bits"][i] in netnames:
                netnames[net["bits"][i]] += f" / {name}[{i}]"
            else:
                netnames[net["bits"][i]] = f"{name}[{i}]"



muxes = {}
scan_list = []

for name, cell in des["modules"][top_mod]["cells"].items():
    if "$" in cell["type"] and "dff" in cell["type"]:
        assert "D" in cell["connections"]
        assert "Q" in cell["connections"]
        width = len(cell["connections"]["D"])
        assert len(cell["connections"]["Q"]) == width

        for i in range(width):
            orig = cell["connections"]["D"][i]
            cell["connections"]["D"][i] = (idx := idx + 1)

            muxes[f"scanchain_mux{idx}"] = {
                "hide_name": 1,
                "type": "$mux",
                "parameters": {"WIDTH": "00000000000000000000000000000001"},
                "attributes": {},
                "port_directions": {
                    "A": "input",
                    "B": "input",
                    "S": "input",
                    "Y": "output"
                },
                "connections": {
                    "A": [orig],
                    "B": [scan_cur],
                    "S": [scan_en],
                    "Y": [idx]
                }
            }

            scan_cur = cell["connections"]["Q"][i]
            scan_list.append((scan_cur, netnames[scan_cur], cell["attributes"].get("src", None)))


des["modules"][top_mod]["cells"].update(muxes)

scan_out = scan_cur
des["modules"][top_mod]["ports"]["scan_out"] = {"direction": "output", "bits": [scan_out]}

with open("/tmp/design_out.json", "w+") as f:
    json.dump(des, f)

with open(logfile, "w+") as f:
    for i, x in enumerate(scan_list):
        line = f"{i}: {x[1]}"
        f.write(line+"\n")
        print(line)

_ = subprocess.check_output(["yosys", "-p", "read_json /tmp/design_out.json; opt; write_verilog "+outfile])
