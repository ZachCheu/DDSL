class StripImg(object):
    def __init__(self, tifId, tifName, corner):
        self.id = tifId
        self.name = tifName
        self.corner = corner

import csv

array = []
array.append(StripImg(1,2,3))
array.append(StripImg(4,5,6))
for stripImg in array:
    print(stripImg.id)