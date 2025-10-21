def isPalindrome(word):
    word = word.lower().replace(" ","")
    wordReversed = word[::-1]
    if word==wordReversed:
        print(wordReversed)
        return True
    else:
        return False

def fibbonaci(num):
    num=num-1
    a,b =0,1
    for i in range(num):
        a,b=b,a+b

    return a

def count_vowels(word):
    sum=0
    word=word.lower()
    for l in word:
        if l in "aeiouy":
            sum+=1
    return sum

def calculate_discount(price, discount):
    if discount<0 or discount>1:
        raise ValueError("Niepoprawna znizka")
    discount=1-discount
    price=price*discount
    return price

