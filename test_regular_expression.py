import re

p = re.compile('')
t1 = re.split('\d', "1000 smoke  fire [310.0, 253.0, 367.0, 156.99999999999997]" )
t2 = re.split('\W+', "1000 smoke  fire [310.0, 253.0, 367.0, 156.99999999999997]")
print t2
print re.sub('\[|\]|,', ' ', "1000 smoke  fire [310.0, 253.0, 367.0, 156.99999999999997]").split()

p = (3, 4)
print p[0]

dict = {}

print int('100')
for i in range(1, 5):
	print i

str = "asdf"
print str.rfind("/")
print str[-1:]