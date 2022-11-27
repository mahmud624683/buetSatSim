import string
 
test_str = 'Gfg, is best: for ! Geeks ;'
 
test_str = test_str.translate(str.maketrans(' ', ',', string.punctuation))
print(test_str)