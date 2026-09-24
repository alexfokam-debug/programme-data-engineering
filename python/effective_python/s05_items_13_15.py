# item 13: use slicing to copy a list
def build_topics():
    topics = ["python", "sql", "pyspark"]
    return topics


# print(build_topics())


# items 14:
def get_slice_examples(values):
    return {
        "first_three": values[:3],
        "from_third": values[2:],
        "last_two": values[-2:],
        "middle": values[1:4],
        "copy": values[:],
    }


"""values = [10, 20, 30]

copy_values = values[:]
same_values = values

copy_values.append(40)
same_values.append(50)

print(values)
print(copy_values)
print(same_values)"""

# item 15: slice and stride


def get_even_values_from_middle(values):
    subset = values[2:9]
    return subset[::2]
