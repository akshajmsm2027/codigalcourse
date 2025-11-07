
def convert_tuple_to_list(input_tuple):
    
    return list(input_tuple)


if __name__ == "__main__":
    
    sample_tuple = (1, 2, 3, 4, 5)
    print("Original Tuple:", sample_tuple)

    
    converted_list = convert_tuple_to_list(sample_tuple)
    print("Converted List:", converted_list)
