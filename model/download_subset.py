from datasets import load_dataset


GESTURES = ["fist", "point", "peace"]
NUM_PER_CLASS = 500

dataset = load_dataset("cj-mills/hagrid-sample-500k-384p", split="train", streaming=True)

# print(dataset[0])
for i in range(100):
  print(dataset[i])

samples = {g: [] for g in GESTURES}

