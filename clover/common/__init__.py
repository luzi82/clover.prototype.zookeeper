def between(a,b,c):
    return (a<=b) and (b<c)

def in_rect(pos,rect):
    return between(rect[0],pos[0],rect[2]) and between(rect[1],pos[1],rect[3])
