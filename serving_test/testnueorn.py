import subprocess


print(subprocess.run(["neuron-ls"], capture_output=True, check=True))


