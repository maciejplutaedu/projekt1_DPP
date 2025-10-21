def isPalindrome(word):
    word = word.lower().replace(" ","")
    wordReversed = word[::-1]
    if word==wordReversed:
        print(wordReversed)
        return True
    else:
        return False

def fibonacci(n):
    if n < 0:
        raise ValueError("n cannot be negative")
    elif n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b


def count_vowels(word):
    sum=0
    word=word.lower()
    for l in word:
        if l in "aąeęióouy":
            sum+=1
    return sum

def calculate_discount(price, discount):
    if discount<0 or discount>1:
        raise ValueError("Niepoprawna znizka")
    discount=1-discount
    price=price*discount
    return price

def flatten_list(nested_list):
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list


import string
import string


def word_frequencies(text):
    text = text.lower()
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)
    words = text.split()
    ignored_words = {'a', 'i'}
    words = [word for word in words if word not in ignored_words]
    frequency = {}
    for word in words:
        frequency[word] = frequency.get(word, 0) + 1

    return frequency


def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


#2
