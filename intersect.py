from numpy import *
'''
Algorithm to check if two line segments intersect

'''




# line segment a given by endpoints a1, a2
# line segment b given by endpoints b1, b2
# return
def seg_intersect(a1,a2, b1,b2) :

    def perp(a):
        b = empty_like(a)
        b[0] = -a[1]
        b[1] = a[0]
        return b

    da = a2-a1
    db = b2-b1
    dp = a1-b1
    dap = perp(da)
    denom = dot( dap, db)

    if denom==0:
        return False
    else:
        num = dot( dap, dp )

        MAX_XA = max(a1[0],a2[0])
        MIN_XA = min(a1[0], a2[0])

        MAX_YA = max(a1[1], a2[1])
        MIN_YA = min(a1[1],a2[1])

        MAX_XB = max(b1[0], b2[0])
        MIN_XB = min(b1[0], b2[0])

        MAX_YB = max(b1[1], b2[1])
        MIN_YB = min(b1[1], b2[1])

        ANS = ((num / denom.astype(float))*db + b1)

        if MIN_XA<=ANS[0]<=MAX_XA and MIN_XB<=ANS[0]<=MAX_XB and MIN_YA<=ANS[1]<=MAX_YA and MIN_YB<=ANS[1]<=MAX_YB:
            return True

        else:
            return False



