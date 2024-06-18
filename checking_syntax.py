hist = []
print(len(hist))
hist.append((1,2,"string"))
hist.append((3,4,"string2"))
print(hist)
here = hist.pop()

hist.append((3,4,"string2"))
hist.append((3,4,"string2"))

hist2 = []
hist2.extend(hist)

print(hist2)

print(here[2])