from numpy import *



def perp( a ) :
    b = empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b

# line segment a given by endpoints a1, a2
# line segment b given by endpoints b1, b2
# return
def seg_intersect(a1,a2, b1,b2) :
    da = a2-a1
    db = b2-b1
    dp = a1-b1
    dap = perp(da)
    denom = dot( dap, db)
    if denom==0:
        return False
    else:
        num = dot( dap, dp )
        if a1[0]<=((num / denom.astype(float))*db + b1)[0]<=a2[0]:
            return True
        else:
            return False



