
# Checks if a course is in a list
def isin(course, courselst):
	for i in courselst:
		if course.equals(i):
			return True
	return False

# Brute force checks if two courses overlap
def overlaps(courselst):
    overlappinglst = []
    rtn = False
    if len(courselst)<2:
        return False, []
    for ri in range(len(courselst)):
        i = courselst[ri]
        for rj in range(ri+1, len(courselst)):
            j = courselst[rj]
            for di in i.meetings:
                for dj in j.meetings:
                    ti = i.meetings[di]
                    tj = j.meetings[dj]
                    if di==dj: # Checks if course is on the same day
                        if (ti[0]>=tj[0] and ti[0]<=tj[1]) or (tj[0]<=ti[0] and tj[0]<=ti[1]) or (
                                ti[1]<=tj[1] and ti[1]>=tj[0]) or (tj[1]<=ti[1] and tj[1]>=ti[0]):
                            rtn = True
                            overlappinglst.append([ri, rj, di, ti, tj])
    return rtn, overlappinglst

