import torch
import torch.neuronx
import torch_neuron as tn

# Load the PyTorch model
model = torch.load('/path/to/model.pth')

# Convert the model to Neuron-optimized format
neuron_model = tn.neuronize(model)

# Create an inference session
session = tn.Session(neuron_model)

# Load the input data
input_data = torch.tensor([1, 2, 3, 4])

# Run inference
output = session.run([input_data])

# Print the output
print(output)
